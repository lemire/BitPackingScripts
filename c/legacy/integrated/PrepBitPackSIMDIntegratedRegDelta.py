#!/usr/bin/env python3
# scripts/PrepBitPackSIMDIntegratedRegDelta.py > src/simdintegratedbitpackingregdelta.cpp

from math import ceil

print("""
#include "simdintegratedbitpacking.h"

using namespace std;

""");


def MaskOld(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " % (1U << "+str(bit)+" )"
  return ""

def mask(bit):
  return str((1 << bit) - 1)

for bit in range(1,33):
  print("const static __m128i  mask" + str(bit) + " =  _mm_set1_epi32(" + str(mask(bit)) +"U);");

print("""
#define Integrate4(_tmp0, prev) \\
  (_tmp1 = _mm_add_epi32(_mm_slli_si128(_tmp0, 8), _tmp0),\\
  _tmp2 = _mm_add_epi32(_mm_slli_si128(_tmp1, 4), _tmp1),\\
  _mm_add_epi32(_tmp2, _mm_shuffle_epi32(prev, 0xff)))

#define Delta4(_tmp0, _prev) _mm_sub_epi32(_tmp0, _mm_alignr_epi8(_tmp0, _prev, 12))
""");





for length in [32]:
  print("""
static void __SIMD_integratedfastunpack0_"""+str(length)+"""(__m128i initOffset, const __m128i *  __restrict__ , uint32_t *  __restrict__  _out) {
    __m128i       *out = reinterpret_cast<__m128i*>(_out);

    for (unsigned i = 0; i < 8; ++i) {
        _mm_store_si128(out++, initOffset);
        _mm_store_si128(out++, initOffset);
        _mm_store_si128(out++, initOffset);
        _mm_store_si128(out++, initOffset);
    }
}
  """)
# Unmasked packing
  for bit in range(1,33):
    print("""
static void __SIMD_integratedfastpackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(__m128i initOffset, const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i    OutReg;

      """);

    if (bit != 32):
      print("    __m128i CurrIn = _mm_load_si128(in);");
      print("    __m128i InReg = Delta4(CurrIn, initOffset);");
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
            print("    InReg = Delta4(CurrIn, initOffset);");
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
static void __SIMD_integratedfastpack"""+str(bit)+"""_"""+str(length)+"""(__m128i initOffset, const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i     OutReg;

      """);
    print("    const static __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ;");
    print("");


    if (bit != 32):
      print("    __m128i CurrIn = _mm_load_si128(in);");
      print("    __m128i InReg = _mm_and_si128(Delta4(CurrIn, initOffset), mask);");
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
            print("    InReg = _mm_and_si128(Delta4(CurrIn, initOffset), mask);");
            print("    initOffset = CurrIn;");
          else:
            print("    InReg = _mm_load_si128(in);");
          print("");
        #print("    ++in;")
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n""")

  print("""
  static void __SIMD_integratedfastunpack1_32(__m128i initOffset, const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
    __m128i*   out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg1 = _mm_load_si128(in);
    __m128i    InReg2 = InReg1;
    __m128i    OutReg1, OutReg2, OutReg3, OutReg4 = initOffset;
    __m128i    _tmp1, _tmp2;

    unsigned shift = 0;

    const static __m128i mask =  _mm_set1_epi32(1U);

    for (unsigned i = 0; i < 8; ++i) {
        OutReg1 = Integrate4(_mm_and_si128(  _mm_srli_epi32(InReg1,shift) , mask), OutReg4);
        ++shift;
        _mm_store_si128(out++, OutReg1);
        OutReg2 = Integrate4(_mm_and_si128(  _mm_srli_epi32(InReg2,shift) , mask), OutReg1);
        ++shift;
        _mm_store_si128(out++, OutReg2);
        OutReg3 = Integrate4(_mm_and_si128(  _mm_srli_epi32(InReg1,shift) , mask), OutReg2);
        ++shift;
        _mm_store_si128(out++, OutReg3);
        OutReg4 = Integrate4(_mm_and_si128(  _mm_srli_epi32(InReg2,shift) , mask), OutReg3);
        ++shift;
        _mm_store_si128(out++, OutReg4);
    }
}
  """);

  for bit in range(2,33):
    print("""\n
static void __SIMD_integratedfastunpack"""+str(bit)+"""_"""+str(length)+"""(__m128i initOffset, const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
      """);
    print("""    __m128i*   out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg = _mm_load_si128(in);
    __m128i    OutReg;
    __m128i     tmp;
    """);

    if (bit != 32) :
      print("    const static __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ");
      print("    __m128i    _tmp1, _tmp2;");
    print("");
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      for x in range(inwordpointer,32,bit):
        if(valuecounter == length): break
        if (x > 0):
          print("    tmp = _mm_srli_epi32(InReg," + str(x) +");");
        else:
          print("    tmp = InReg;");
        if(x+bit<32):
          print("    OutReg = _mm_and_si128(tmp, mask);");
        else:
          print("    OutReg = tmp;");
        if((x+bit>=32) ):
          while(inwordpointer<32):
            inwordpointer += bit
          if(valuecounter + 1 < length):
             print("    ++in;")
             print("    InReg = _mm_load_si128(in);\n");
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_or_si128(OutReg, _mm_slli_epi32(_mm_and_si128(InReg, mask" + str(inwordpointer)+"), " + str(bit) + "-" + str(inwordpointer) + "));");
        if (bit != 32):
          print("    OutReg = Integrate4(OutReg, initOffset);\n");
          print("    initOffset = OutReg;\n");
        print("    _mm_store_si128(out++, OutReg);\n");
        print("");
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n")

  print("""
void simdintegratedunpackregdelta(__m128i initOffset, const __m128i *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: __SIMD_integratedfastunpack0_"+str(length)+"(initOffset,in,out); return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_integratedfastunpack"+str(bit)+"_"+str(length)+"(initOffset,in,out); return;\n")
  print("""        default: break;
    }
    throw logic_error("number of bits is unsupported");
}
""")


  print("""

  /*assumes that integers fit in the prescribed number of bits*/
void simdintegratedpackwithoutmaskregdelta(__m128i initOffset, const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_integratedfastpackwithoutmask"+str(bit)+"_"+str(length)+"(initOffset,in,out); return;\n")
  print("""        default: break;
    }
    throw logic_error("number of bits is unsupported");
}
  """)


  print("""

  /*assumes that integers fit in the prescribed number of bits*/
void simintegratedpackregdelta(__m128i initOffset, const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_integratedfastpack"+str(bit)+"_"+str(length)+"(initOffset, in,out); return;\n")
  print("""        default: break;
    }
    throw logic_error("number of bits is unsupported");
}
  """)
