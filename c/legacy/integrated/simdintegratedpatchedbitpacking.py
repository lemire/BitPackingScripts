#!/usr/bin/env python3
# scripts/simdintegratedpatchedbitpacking.py > simdintegratedpatchedbitpacking.cpp

from math import ceil

print("""
#include "simdintegratedbitpacking.h"

/**
* This is like regular integrated unpacking, except that 
* it assumes that there is already data in the output that
* we want to preserve. This is meant to be used in conjunction
* with patching (PFOR) schemes.
*/

""");

def mask(bit):
  return str((1 << bit) - 1)


#print("""
#    const static __m128i mask1 =  _mm_set1_epi32((1U<<1)-1);
#    const static __m128i mask2 =  _mm_set1_epi32((1U<<2)-1);
#    const static __m128i mask3 =  _mm_set1_epi32((1U<<3)-1);
#    const static __m128i mask4 =  _mm_set1_epi32((1U<<4)-1);
#    const static __m128i mask5 =  _mm_set1_epi32((1U<<5)-1);
#    const static __m128i mask6 =  _mm_set1_epi32((1U<<6)-1);
#    const static __m128i mask7 =  _mm_set1_epi32((1U<<7)-1);
#    const static __m128i mask8 =  _mm_set1_epi32((1U<<8)-1);
#    const static __m128i mask9 =  _mm_set1_epi32((1U<<9)-1);
#    const static __m128i mask10 =  _mm_set1_epi32((1U<<10)-1);
#    const static __m128i mask11 =  _mm_set1_epi32((1U<<11)-1);
#    const static __m128i mask12 =  _mm_set1_epi32((1U<<12)-1);
#    const static __m128i mask13 =  _mm_set1_epi32((1U<<13)-1);
#    const static __m128i mask14 =  _mm_set1_epi32((1U<<14)-1);
#    const static __m128i mask15 =  _mm_set1_epi32((1U<<15)-1);
#    const static __m128i mask16 =  _mm_set1_epi32((1U<<16)-1);
#    const static __m128i mask17 =  _mm_set1_epi32((1U<<17)-1);
#    const static __m128i mask18 =  _mm_set1_epi32((1U<<18)-1);
#    const static __m128i mask19 =  _mm_set1_epi32((1U<<19)-1);
#    const static __m128i mask20 =  _mm_set1_epi32((1U<<20)-1);
#    const static __m128i mask21 =  _mm_set1_epi32((1U<<21)-1);
#    const static __m128i mask22 =  _mm_set1_epi32((1U<<22)-1);
#    const static __m128i mask23 =  _mm_set1_epi32((1U<<23)-1);
#    const static __m128i mask24 =  _mm_set1_epi32((1U<<24)-1);
#    const static __m128i mask25 =  _mm_set1_epi32((1U<<25)-1);
#    const static __m128i mask26 =  _mm_set1_epi32((1U<<26)-1);
#    const static __m128i mask27 =  _mm_set1_epi32((1U<<27)-1);
#    const static __m128i mask28 =  _mm_set1_epi32((1U<<28)-1);
#    const static __m128i mask29 =  _mm_set1_epi32((1U<<29)-1);
#    const static __m128i mask30 =  _mm_set1_epi32((1U<<30)-1);
#    const static __m128i mask31 =  _mm_set1_epi32((1U<<31)-1);
#""")


for length in [32]:
  print("""
template <class DeltaHelper>
__m128i  ipatchedunpack0(__m128i initOffset, const __m128i *  __restrict__ , uint32_t *   _out, const  __m128i * const patchedbuffer) {
    __m128i    * const  out = reinterpret_cast<__m128i*>(_out);
    __m128i    OutReg;
    for (unsigned i = 0; i < 8; ++i) {
   	    OutReg = _mm_load_si128(patchedbuffer+0+i*4);
   	    initOffset = DeltaHelper::PrefixSum(OutReg, initOffset);
        _mm_store_si128(out+0+i*4, initOffset);

     	OutReg = _mm_load_si128(patchedbuffer+1+i*4);
     	initOffset = DeltaHelper::PrefixSum(OutReg, initOffset);
        _mm_store_si128(out+1+i*4, initOffset);

       	OutReg = _mm_load_si128(patchedbuffer+2+i*4);
       	initOffset = DeltaHelper::PrefixSum(OutReg, initOffset);
        _mm_store_si128(out+2+i*4, initOffset);

        OutReg = _mm_load_si128(patchedbuffer+3+i*4);
        initOffset = DeltaHelper::PrefixSum(OutReg, initOffset);
        _mm_store_si128(out+3+i*4, initOffset);

    }
    return initOffset;
}


template <class DeltaHelper>
__m128i ipatchedunpack32(__m128i  init, const  __m128i*   in, uint32_t *   __restrict__  _out, const  __m128i * const ) {
    __m128i    InReg;
    __m128i    * const  out = reinterpret_cast<__m128i*>(_out);

    __m128i    OutReg =  init;

    for (unsigned i = 0; i < 8; ++i) {
    	InReg = _mm_load_si128(in+0+i*4);
    	OutReg = DeltaHelper::PrefixSum(InReg, OutReg);
    	_mm_store_si128(out+0+i*4, OutReg);

    	InReg = _mm_load_si128(in+1+i*4);
    	OutReg = DeltaHelper::PrefixSum(InReg, OutReg);
    	_mm_store_si128(out+1+i*4, OutReg);

    	InReg = _mm_load_si128(in+2+i*4);
    	OutReg = DeltaHelper::PrefixSum(InReg, OutReg);
    	_mm_store_si128(out+2+i*4, OutReg);

    	InReg = _mm_load_si128(in+3+i*4);
    	OutReg = DeltaHelper::PrefixSum(InReg, OutReg);
    	_mm_store_si128(out+3+i*4, OutReg);

      }
    return OutReg;

}


  """)
  for bit in range(1,32):
    offsetVar = " initOffset";
    #if (bit == 32):
        #offsetVar = " /* initOffset */ ";
    print("""\n
template <class DeltaHelper>
inline __m128i ipatchedunpack"""+str(bit)+"""(__m128i """+offsetVar+""", const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out, const  __m128i * const  __restrict__ patchedbuffer) {
      """);
    print("""    __m128i*  const  __restrict__ out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg = _mm_load_si128(in);
    __m128i    OutReg;    
    """);
    #__m128i     tmp;
    if(bit!=32):
      print("""
    const __m128i mask =  _mm_set1_epi32((1U<<"""+str(bit)+""")-1);
      """)
    incounter = 0;
    outcounter = 0;

    MaskText = "";
    MainText = "";

    #if (bit != 32) :
    #  MaskText += "    const static __m128i mask" + str(bit) +" =  _mm_set1_epi32(" + str(mask(bit)) +"U); \n";
    MaskSet = { bit }

    MainText += "\n";
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      for x in range(inwordpointer,32,bit):
        if(valuecounter == length): break
        #if (x > 0):
        #  MainText += "    tmp = _mm_srli_epi32(InReg," + str(x) +");\n"; 
        #else:
        #  MainText += "    tmp = InReg;\n"; 
        if (x > 0):
          tmp = "_mm_srli_epi32(InReg," + str(x) +")"; 
        else:
          tmp = " InReg"; 
        #if(x+bit<32):
        #  MainText += "    OutReg = _mm_or_si128(_mm_load_si128(patchedbuffer+"+str(outcounter)+"),_mm_and_si128(tmp, mask" + str(bit) + "));\n";
        #else:
        #  MainText += "    OutReg = _mm_or_si128(_mm_load_si128(patchedbuffer+"+str(outcounter)+"),tmp);\n";        
        if(x+bit<32):
          MainText += "    OutReg = _mm_or_si128(_mm_load_si128(patchedbuffer+"+str(outcounter)+"),_mm_and_si128("+tmp+", mask));\n";
        else:
          MainText += "    OutReg = _mm_or_si128(_mm_load_si128(patchedbuffer+"+str(outcounter)+"),"+tmp+");\n";        
        if((x+bit>=32) ):      
          while(inwordpointer<32):
            inwordpointer += bit
          if(valuecounter + 1 < length):
             #MainText += "    ++in;"
             incounter = incounter + 1
             MainText += "    InReg = _mm_load_si128(in+"+str(incounter)+");\n";
          inwordpointer -= 32;
          if(inwordpointer>0):
            MainText += "    OutReg = _mm_or_si128(OutReg, _mm_and_si128(_mm_slli_epi32(InReg, " + str(bit) + "-" + str(inwordpointer) + "), mask));\n\n";
            if (inwordpointer not in MaskSet):
              #MaskText += "    const static __m128i mask" + str(inwordpointer) + " =  _mm_set1_epi32(" + str(mask(inwordpointer)) +"U); \n";
              MaskSet = MaskSet.union({inwordpointer})
        if (bit != 32):
          #MainText += "    OutReg = DeltaHelper::PrefixSum(OutReg, initOffset);\n"; 
          #MainText += "    initOffset = OutReg;\n"; 
          MainText += "    initOffset = DeltaHelper::PrefixSum(OutReg, initOffset);\n"; 
          #MainText += "    initOffset = OutReg;\n"; 
        #MainText += "    _mm_store_si128(out+"+str(outcounter)+", OutReg);\n\n";
        MainText += "    _mm_store_si128(out+"+str(outcounter)+", initOffset);\n\n";
        outcounter = outcounter + 1 
        MainText += "";
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print(MaskText)
    print(MainText)
    print("    return initOffset;");
    print("\n}\n\n")



  for bit in range(33):
    print("""
	template __m128i  ipatchedunpack"""+str(bit)+"""<RegularDeltaSIMD>(__m128i, const __m128i *, uint32_t *,const  __m128i * const);
	template __m128i  ipatchedunpack"""+str(bit)+"""<Max4DeltaSIMD>(__m128i, const __m128i *, uint32_t *,const  __m128i * const);
	template __m128i  ipatchedunpack"""+str(bit)+"""<CoarseDelta2SIMD>(__m128i, const __m128i *, uint32_t *,const  __m128i * const);
	template __m128i  ipatchedunpack"""+str(bit)+"""<CoarseDelta4SIMD>(__m128i, const __m128i *, uint32_t *,const  __m128i * const);
	template __m128i  ipatchedunpack"""+str(bit)+"""<NoDelta>(__m128i, const __m128i *, uint32_t *,const  __m128i * const);
  
    """)
