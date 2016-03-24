#! /usr/bin/python3 -Wall

#usage : python asm_generate_unpack.py  > asmsimdpacking.cpp

import sys
from asm_generate_inline import InlineSSE

#DEBUG = print
DEBUG = lambda x : None

def shouldSkip(entry, skipList):
    if entry in skipList:
        del skipList[entry]
        return True
    else:
        return False
    
def zipStoresLoadsAddsMasksShifts(bits):
    cycle = 9
    storeOffset = 0
    loadOffset = 0
    skipStore = {}
    skipMask = {}

    f = False   # static start from header
    stores = [f, f, f, f, f, f, f, f, False]
    adds =   [f, f, f, f, f, f, f, False]
    masks =  [f, f, f, f, f, f, f, True]
    shifts = [f, f, f, f, f, f, f, bits]
    loads =  [0]
    shift = bits % 32

    if (bits == 32): shifts[-1] = False

    while storeOffset < 32:                  # until we have 32 stores
        if shift == 0: 
            loadOffset += 1

        if storeOffset < 31: 
            shift = (shift + bits) % 32
        else: shift = 0

        if shift > 0 and shift < bits:
            # fit in an extra cycle to handle a junction
            shift = shift - bits             # do now for logging
            DEBUG("%d + shift %d in %d out %d" % 
                  (bits, shift, loadOffset, storeOffset))
            if loadOffset < bits:
                loads.append(loadOffset)   
            else:
                loads.append(False)

            if cycle in skipStore:
                del skipStore[cycle]
                stores.append(False)
            else:
                stores.append(storeOffset) 
                storeOffset += 1
            skipStore[cycle + 1] = True

            shifts.append(shift)             # negative means SHIFTL
            masks.append(False)              # don't mask 
            adds.append(True)                # but always add
            shift = (shift + bits) % 32      # shift was negative
            cycle += 1
            if loadOffset < bits:
                loadOffset += 1              # next load advances

        DEBUG("%d - shift %d in %d out %d" % 
              (bits, shift, loadOffset, storeOffset))


        if cycle in skipStore:
            del skipStore[cycle]
            stores.append(False)
        else:
            stores.append(storeOffset) 
            storeOffset += 1

        adds.append(True)     

        if loadOffset < bits:
            loads.append(loadOffset)
        else:
            loads.append(False)


        if bits < 32 and storeOffset < 31 and not shouldSkip(cycle, skipMask):
            masks.append(True)   
        else: 
            masks.append(False)

        if (shift > 0): 
            shifts.append(shift) 
        else: 
            shifts.append(False)
        if (shift + bits == 32):
            skipMask[cycle + 1] = True

        cycle += 1

    loads.extend([False for i in range(len(loads), cycle)])
    adds.extend([False])      #  add a non-read
    masks.extend([f])         #  add a non-mask
    shifts.extend([f])   #  falsify last three 

    assert len(loads) == cycle, "%d %d\n%s" % (len(loads), cycle, loads)
    assert len(stores) == cycle, "%d %d\n%s" % (len(stores), cycle, stores)
    assert len(adds) == cycle, "%d %d\n%s" % (len(adds), cycle, adds)
    assert len(masks) == cycle, "%d %d\n%s" % (len(masks), cycle, masks)
    assert len(shifts) == cycle, "%d %d\n%s" % (len(shifts), cycle, shifts)
   
    assert max(stores) == 31, "%d\n%s" % (max(stores), stores)
    assert max(loads) == bits-1, "%d %d\n%s" % (max(loads), bits-1, loads)
    
    DEBUG("loads %d %s\nstores %d %s\nadds %d %s\nmasks %d %s\nshifts %d %s\n" 
          % (len(loads), loads, len(stores), stores, len(adds), adds,
             len(masks), masks, len(shifts), shifts))
    return zip(stores, loads, adds, masks, shifts)

def makeUnpackFunc(code, bits):
    slams = zipStoresLoadsAddsMasksShifts(bits)    
    (stores, loads, adds, masks, shifts) = zip(*slams)

    func = code.header(bits, stores, loads, masks, adds, shifts)

    cycle = 0
    for store, load, add, mask, shift in \
            zip(stores, loads, adds, masks, shifts):

        if cycle > 8:

            func += "\n"
        
            if load is not False:
                func += code.load(code.reg(cycle), load)
                
            if store is not False: 
                func += code.store(code.reg(cycle + 1), store)
                    
            if add is not False:
                func += code.add(code.reg(cycle + 2), code.reg(cycle + 1))
                        
            if mask is not False: 
                func += code.mask(code.reg(cycle + 3))
                            
            if shift is not False:
                assert shift != 0
                if (shift > 0):
                    func += code.shiftr(code.reg(cycle + 4), shift)
                else:
                    func += code.shiftl(code.reg(cycle + 4), -shift)
                                    
        cycle += 1
    func += code.copy(code.offsetVar,code.reg(cycle))

    func += code.footer(bits)
        
    return func


if __name__ == "__main__":
    print("#include \"asmsimdpacking.h\"")
    for i in range(1,32): # Daniel: we disable differential coding for bit 32
        code = InlineSSE()
        func = makeUnpackFunc(code, i)
        print(func)
    print("""
// the code where bit = 0 is special, we basically do a memset
__m128i asmsimdunpack0(__m128i initOffset, const __m128i *  __restrict__ , uint32_t *  __restrict__  _out) {
    __m128i       *out = reinterpret_cast<__m128i*>(_out);
    for (unsigned i = 0; i < 8; ++i) {
      _mm_store_si128(out++, initOffset);
      _mm_store_si128(out++, initOffset);
      _mm_store_si128(out++, initOffset);
      _mm_store_si128(out++, initOffset);
    }
    return initOffset;
}

    """)
    print("""

// the code where bit = 32 is special, we do not use differential coding
__m128i asmsimdunpack32(__m128i, const __m128i*  __restrict__ in, uint32_t *  __restrict__ _out) {
	__m128i * mout = reinterpret_cast<__m128i *>(_out);
	__m128i invec; // we proceed with what is essential a vectorized memcpy
	for(size_t k = 0; k < 128/4; ++k) {
		invec =  _mm_load_si128(in++);
	    _mm_store_si128(mout++, invec);
	}
	return invec;
}

    """)
    print("""
    

__m128i asmsimdunpack(__m128i initOffset, const __m128i *  __restrict__ in,
		     uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {
    """)
    for i in range(0,33):
      print("        case "+str(i)+": return asmsimdunpack"+str(i)+"(initOffset,in,out);");
    print("""
            default: break;
    }

    // FUTURE: report this error somehow
    cout << "Failed to find an unpack function.  Bit was " << bit << endl;
    return initOffset;
}

    """)


