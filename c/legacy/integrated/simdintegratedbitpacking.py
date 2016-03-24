#!/usr/bin/env python3
# scripts/simdintegratedbitpacking.py > include/simdintegratedbitpacking.h
#### This is current as of December 9th 2013

from math import ceil

print("""
/**
* This code is released under the
* Apache License Version 2.0 http://www.apache.org/licenses/.
*
*/
#include "simdintegratedbitpacking.h"

""");

def mask(bit):
  return str((1 << bit) - 1)

#
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


#for bit in range(1,33):
#  print("const static __m128i  mask" + str(bit) + " =  _mm_set1_epi32(" + str(mask(bit)) +"U);");



for length in [32]:
  print("""
template <class DeltaHelper>
__m128i  iunpack0(__m128i initOffset, const __m128i *   , uint32_t *    _out) {
    __m128i       *out = reinterpret_cast<__m128i*>(_out);
    static const __m128i zero =  _mm_set1_epi32 (0);

    for (unsigned i = 0; i < 8; ++i) {
    	initOffset = DeltaHelper::PrefixSum(zero, initOffset);
        _mm_store_si128(out++, initOffset);
    	initOffset = DeltaHelper::PrefixSum(zero, initOffset);
    	_mm_store_si128(out++, initOffset);
    	initOffset = DeltaHelper::PrefixSum(zero, initOffset);
        _mm_store_si128(out++, initOffset);
    	initOffset = DeltaHelper::PrefixSum(zero, initOffset);
        _mm_store_si128(out++, initOffset);
    }

    return initOffset;
}

  """)
  print("""
template <class DeltaHelper>
void ipackwithoutmask0(__m128i  , const uint32_t *  , __m128i *  ) {

}

template <class DeltaHelper>
void ipack0(__m128i  , const uint32_t *   , __m128i *    ) {
}
""") 
  for bit in range(1,33):
    offsetVar = " initOffset";
    if (bit == 32):
        offsetVar = " /* initOffset */ ";
    print("""  
template <class DeltaHelper>
void ipackwithoutmask"""+str(bit)+"""(__m128i """+offsetVar+""", const uint32_t *   _in, __m128i *   out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i    OutReg;

      """);
    
    if (bit != 32):
      print("    __m128i CurrIn = _mm_load_si128(in);");
      print("    __m128i InReg = DeltaHelper::Delta(CurrIn, initOffset);");
      print("    initOffset = CurrIn;");
    else:
      print("    __m128i InReg = _mm_load_si128(in);");

    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      if(valuecounter == length): break
      for x in range(inwordpointer,32,bit):
        if(x!=0) :
          print("    OutReg = _mm_or_si128(OutReg, _mm_slli_epi32(InReg, " + str(x) + "));");
          #print("    *out |= ( (*in)  ) << ",x,";");
        else:
          print("    OutReg = InReg; ");
          #print("    *out =  (*in)  ;");
        if((x+bit>=32) ):
          while(inwordpointer<32):
            inwordpointer += bit
          print("    _mm_store_si128(out, OutReg);");
          print("");

          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
            #print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        if(valuecounter + 1 < length):
          print("    ++in;") 

          if (bit != 32):
            print("    CurrIn = _mm_load_si128(in);");
            print("    InReg = DeltaHelper::Delta(CurrIn, initOffset);");
            print("    initOffset = CurrIn;");
          else:
            print("    InReg = _mm_load_si128(in);");
          print("");
        #print("    ++in;") 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n""")
# Masked packing
    print("""  
template <class DeltaHelper>
void ipack"""+str(bit)+"""(__m128i """+offsetVar+""", const uint32_t *   _in, __m128i *    out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i     OutReg;

      """);
    if (bit != 32):
      print("    const __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ;");
    print("");
     
    
    if (bit != 32):
      print("    __m128i CurrIn = _mm_load_si128(in);");
      print("    __m128i InReg = _mm_and_si128(DeltaHelper::Delta(CurrIn, initOffset), mask);");
      print("    initOffset = CurrIn;");
    else:
      print("    __m128i InReg = _mm_load_si128(in);");
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      if(valuecounter == length): break
      for x in range(inwordpointer,32,bit):
        if(x!=0) :
          print("    OutReg =  _mm_or_si128(OutReg,_mm_slli_epi32(InReg, " + str(x) + "));");
        else:
          print("    OutReg = InReg; ");
        if((x+bit>=32) ):
          while(inwordpointer<32):
            inwordpointer += bit
          print("    _mm_store_si128(out, OutReg);");
          print("");
          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
        if(valuecounter + 1 < length):
          print("    ++in;") 
          if (bit != 32):
            print("    CurrIn = _mm_load_si128(in);");
            print("    InReg = _mm_and_si128(DeltaHelper::Delta(CurrIn, initOffset), mask);");
            print("    initOffset = CurrIn;");
          else:
            print("    InReg = _mm_load_si128(in);");
          print("");
        #print("    ++in;") 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n""")
  
  
  for bit in range(1,32):
    offsetVar = " initOffset";
    #if (bit == 32):
        #offsetVar = " /* initOffset */ ";
    print("""\n
template <class DeltaHelper>
__m128i iunpack"""+str(bit)+"""(__m128i """+offsetVar+""", const  __m128i*   in, uint32_t *   _out) {
      """);
    print("""    __m128i*   out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg = _mm_load_si128(in);
    __m128i    OutReg;    
    __m128i     tmp;
    const __m128i mask =  _mm_set1_epi32((1U<<"""+str(bit)+""")-1);

    """);

    MainText = "";

    MainText += "\n";
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      for x in range(inwordpointer,32,bit):
        if(valuecounter == length): break
        if (x > 0):
          MainText += "    tmp = _mm_srli_epi32(InReg," + str(x) +");\n"; 
        else:
          MainText += "    tmp = InReg;\n"; 
        if(x+bit<32):
          MainText += "    OutReg = _mm_and_si128(tmp, mask);\n";
        else:
          MainText += "    OutReg = tmp;\n";        
        if((x+bit>=32) ):      
          while(inwordpointer<32):
            inwordpointer += bit
          if(valuecounter + 1 < length):
             MainText += "    ++in;"
             MainText += "    InReg = _mm_load_si128(in);\n";
          inwordpointer -= 32;
          if(inwordpointer>0):
            MainText += "    OutReg = _mm_or_si128(OutReg, _mm_and_si128(_mm_slli_epi32(InReg, " + str(bit) + "-" + str(inwordpointer) + "), mask));\n\n";
        if (bit != 32):
          MainText += "    OutReg = DeltaHelper::PrefixSum(OutReg, initOffset);\n"; 
          MainText += "    initOffset = OutReg;\n"; 
        MainText += "    _mm_store_si128(out++, OutReg);\n\n"; 
        MainText += "";
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print(MainText)
    print("    return initOffset;");
    print("\n}\n\n")
  print("""
template <class DeltaHelper>
__m128i iunpack32(__m128i  , const  __m128i*   in, uint32_t *    _out) {
	__m128i * mout = reinterpret_cast<__m128i *>(_out);
	__m128i invec;
	for(size_t k = 0; k < 128/4; ++k) {
		invec =  _mm_load_si128(in++);
	    _mm_store_si128(mout++, invec);
	}
	return invec;
	//memcpy(_out,in,128*4);
    //return _mm_load_si128(in+31);
}
  """)

for i in range(33):
  print("""
template __m128i  iunpack"""+str(i)+"""<RegularDeltaSIMD>(__m128i, const __m128i *, uint32_t *);
template void ipack"""+str(i)+"""<RegularDeltaSIMD>(__m128i, const uint32_t *, __m128i *);
template void ipackwithoutmask"""+str(i)+"""<RegularDeltaSIMD>(__m128i, const uint32_t *, __m128i *);
  """)


for i in range(33):
  print("""
template __m128i  iunpack"""+str(i)+"""<CoarseDelta4SIMD>(__m128i, const __m128i *, uint32_t *);
template void ipack"""+str(i)+"""<CoarseDelta4SIMD>(__m128i, const uint32_t *, __m128i *);
template void ipackwithoutmask"""+str(i)+"""<CoarseDelta4SIMD>(__m128i, const uint32_t *, __m128i *);
  """)

for i in range(33):
  print("""
template __m128i  iunpack"""+str(i)+"""<CoarseDelta2SIMD>(__m128i, const __m128i *, uint32_t *);
template void ipack"""+str(i)+"""<CoarseDelta2SIMD>(__m128i, const uint32_t *, __m128i *);
template void ipackwithoutmask"""+str(i)+"""<CoarseDelta2SIMD>(__m128i, const uint32_t *, __m128i *);
  """)

for i in range(33):
  print("""
template __m128i  iunpack"""+str(i)+"""<Max4DeltaSIMD>(__m128i, const __m128i *, uint32_t *);
template void ipack"""+str(i)+"""<Max4DeltaSIMD>(__m128i, const uint32_t *, __m128i *);
template void ipackwithoutmask"""+str(i)+"""<Max4DeltaSIMD>(__m128i, const uint32_t *, __m128i *);
  """)


#  print("""
#template <class DeltaHelper>
#__m128i simdintegratedunpack(__m128i initOffset, const __m128i *   in, uint32_t *   out, const uint32_t bit) {
#    switch(bit) {""")
#  print("        case 0: return __SIMD_integratedfastunpack0_"+str(length)+"<DeltaHelper>(initOffset,in,out);\n")
#  for bit in range(1,33):
#    print("        case "+str(bit)+": return __SIMD_integratedfastunpack"+str(bit)+"_"+str(length)+"<DeltaHelper>(initOffset,in,out); \n")
#  print("""        default: break;    
#    }
#    throw std::logic_error("number of bits is unsupported");
#}
#""")
#  
#  print("""
#  
#  /*assumes that integers fit in the prescribed number of bits*/
#template <class DeltaHelper>
#void simdintegratedpackwithoutmask(__m128i initOffset, const uint32_t *   in, __m128i *   out, const uint32_t bit) {
#    switch(bit) {""")
#  print("        case 0: return;\n")
#  for bit in range(1,33):
#    print("        case "+str(bit)+": __SIMD_integratedfastpackwithoutmask"+str(bit)+"_"+str(length)+"<DeltaHelper>(initOffset,in,out); return;\n")
#  print("""        default: break;    
#    }
#    throw std::logic_error("number of bits is unsupported");
#}
#  """)
#
#  
#  print("""
#  
#  /*assumes that integers fit in the prescribed number of bits*/
#template <class DeltaHelper>
#void simintegratedpack(__m128i initOffset, const uint32_t *  in, __m128i *    out, const uint32_t bit) {
#    switch(bit) {""")
#  print("        case 0: return;\n")
#  for bit in range(1,33):
#    print("        case "+str(bit)+": __SIMD_integratedfastpack"+str(bit)+"_"+str(length)+"<DeltaHelper>(initOffset, in,out); return;\n")
#  print("""        default: break;    
#    }
#    throw std::logic_error("number of bits is unsupported");
#}
#  """)
#print("#endif")
