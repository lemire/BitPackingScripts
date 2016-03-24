#!/usr/bin/env python3
# ./PrepBitPackSIMD.py > simdbitpacking.cpp
# synchronized with fastpfor/src/simdbitpacking.cpp on Dec. 9th 2013

from math import ceil

print("""/**
 * This code is released under the
 * Apache License Version 2.0 http://www.apache.org/licenses/.
 *
 * (c) Daniel Lemire
 */
#include "simdbitpacking.h"

using namespace std;

""");

def gcd32(x):
  count = 0
  while(x//2 * 2 == x):
    x = x//2
    count = count + 1
  return count



def mask(bit):
  return str((1 << bit) - 1)

for length in [32]:
  print("""
static void SIMD_nullunpacker"""+str(length)+"""(const __m128i *  __restrict__ , uint32_t *  __restrict__  out) {
    memset(out,0,"""+str(length)+""" * 4 * 4);
}
""")
  
#  for bit in range(1,32):
#    if (bit != 32) :
#      print("    const static __m128i mask"+str(bit)+" =  _mm_set1_epi32(" + str(mask(bit)) +"U);");
# Unmasked packing
  for bit in range(1,33):
    if( (bit==4) or (bit==8) or (bit ==16)): continue
    print("""  
static void __SIMD_fastpackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i    OutReg;
    __m128i    InReg = _mm_load_si128(in);
      """);
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
          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
            #print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        if(valuecounter + 1 < length):
          #print("    ++in;") 
          print("    InReg = _mm_load_si128(++in);");
        #print("    ++in;") 
        print("");
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n")


  for bit in [4,8,16]:
    print("""  
static void __SIMD_fastpackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i    OutReg;
    __m128i    InReg;
      """);
    inwordpointer = 0
    valuecounter = 0
    nbrloop = 1<<gcd32(bit)
    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
    for k in range(ceil((length * bit) / 32)):
      if(valuecounter == length/nbrloop): break
      for x in range(inwordpointer,32,bit):
        if(valuecounter>0):
          print("    InReg = _mm_load_si128(in+"+str(valuecounter)+");");
        else: 
          print("    InReg = _mm_load_si128(in);");
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
          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
            #print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        #if(valuecounter + 1 < length):
        #  print("    ++in;") 
        #  print("    InReg = _mm_load_si128(++in);");
        #print("    ++in;") 
        print("");
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length/nbrloop)
    print("    in+="+str(valuecounter)+";");
    print("  }"); 
    print("\n}\n\n")


# Masked packing
  for bit in range(1,33):
    if( (bit==4) or (bit==8) or (bit ==16)): continue
    print("""  
static void __SIMD_fastpack"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i     OutReg;
      """);
    if(bit!=32):
      print("""
    const __m128i mask =  _mm_set1_epi32((1U<<"""+str(bit)+""")-1);
      """)
    #print("    const static __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ;");
     
    
    if(bit<32): 
      print("    __m128i InReg = _mm_and_si128(_mm_load_si128(in), mask);");
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
          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
        if(valuecounter + 1 < length):
          #print("    ++in;")
          if(bit<32): 
            print("    InReg = _mm_and_si128(_mm_load_si128(++in), mask);");
          else:
            print("    InReg = _mm_load_si128(++in);"); 
        #print("    ++in;") 
        print("");
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n")

  for bit in [4,8,16]:
    print("""  
static void __SIMD_fastpack"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ _in, __m128i *  __restrict__  out) {
    const __m128i       *in = reinterpret_cast<const __m128i*>(_in);
    __m128i     OutReg, InReg;
   const __m128i mask =  _mm_set1_epi32((1U<<"""+str(bit)+""")-1);

      """);
    #print("    const static __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ;");
     
    
    inwordpointer = 0
    valuecounter = 0
    nbrloop = 1<<gcd32(bit)
    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
    for k in range(ceil((length * bit) / 32)):
      if(valuecounter == length/nbrloop): break
      for x in range(inwordpointer,32,bit):
        if(valuecounter>0):
          print("    InReg = _mm_and_si128(_mm_load_si128(in+"+str(valuecounter)+"), mask);");
        else: 
          print("    InReg = _mm_and_si128(_mm_load_si128(in), mask);");
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
          if(valuecounter + 1 < length):
            print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_srli_epi32(InReg, " + str(bit) + " - " + str(inwordpointer) + ");");
            #print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        #if(valuecounter + 1 < length):
        #  print("    ++in;") 
        #  print("    InReg = _mm_load_si128(++in);");
        #print("    ++in;") 
        print("");
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length/nbrloop)
    print("    in+="+str(valuecounter)+";");
    print("  }"); 
    print("\n}\n\n")

  print("""
  
static void __SIMD_fastunpack1_32(const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
    __m128i*   out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg1 = _mm_load_si128(in);
    __m128i    InReg2 = InReg1;
    __m128i    OutReg1, OutReg2, OutReg3, OutReg4;
    const __m128i mask =  _mm_set1_epi32(1);

    unsigned shift = 0;

    for (unsigned i = 0; i < 8; ++i) {
        OutReg1 = _mm_and_si128(  _mm_srli_epi32(InReg1,shift++) , mask);
        OutReg2 = _mm_and_si128(  _mm_srli_epi32(InReg2,shift++) , mask);
        OutReg3 = _mm_and_si128(  _mm_srli_epi32(InReg1,shift++) , mask);
        OutReg4 = _mm_and_si128(  _mm_srli_epi32(InReg2,shift++) , mask);
        _mm_store_si128(out++, OutReg1);
        _mm_store_si128(out++, OutReg2);
        _mm_store_si128(out++, OutReg3);
        _mm_store_si128(out++, OutReg4);
    }
}

  """)
  for bit in range(2,33):
    #if( (bit==4) or (bit==8) or (bit ==16)): continue
    if(bit ==32): continue
    print("""\n
static void __SIMD_fastunpack"""+str(bit)+"""_"""+str(length)+"""(const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
      """);
    print("""    __m128i*   out = reinterpret_cast<__m128i*>(_out);
    __m128i    InReg = _mm_load_si128(in);
    __m128i    OutReg;    
    const __m128i mask =  _mm_set1_epi32((1U<<"""+str(bit)+""")-1);
    """);#    //__m128i     tmp;
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      for x in range(inwordpointer,32,bit):
        if(valuecounter == length): break
        mystr = ""
        if (x > 0):
          mystr="  _mm_srli_epi32(InReg," + str(x) +") " 
        else:
          mystr=" InReg "; 
        if(x+bit<32):
          print("    OutReg = _mm_and_si128("+mystr+", mask);");
        else:
          print("    OutReg = "+mystr+";");        
        if((x+bit>=32) ):      
          while(inwordpointer<32):
            inwordpointer += bit
          if(valuecounter + 1 < length):
             #print("    ++in;")
             print("    InReg = _mm_load_si128(++in);\n");
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    OutReg = _mm_or_si128(OutReg, _mm_and_si128(_mm_slli_epi32(InReg, " + str(bit) + "-" + str(inwordpointer) + "), mask));");
        print("    _mm_store_si128(out++, OutReg);\n"); 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("\n}\n\n")
  print("""

static void __SIMD_fastunpack32_32(const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
    __m128i*   out = reinterpret_cast<__m128i*>(_out);
  for(uint32_t outer=0; outer< 32 ;++outer) {
    _mm_store_si128(out++, _mm_load_si128(in++));
  }
}
  
  """)

#  for bit in [4,8,16]:
#    print("""\n
#static void __SIMD_fastunpack"""+str(bit)+"""_"""+str(length)+"""(const  __m128i*  __restrict__ in, uint32_t *  __restrict__  _out) {
#      """);
#    print("""    __m128i*   out = reinterpret_cast<__m128i*>(_out);
#    __m128i    InReg ;
#    __m128i    OutReg;    
#    __m128i     tmp;
#    """);
#    if (bit != 32) :
#      print("    const static __m128i mask =  _mm_set1_epi32(" + str(mask(bit)) +"U); ");
#    inwordpointer = 0
#    valuecounter = 0
#    nbrloop = 1<<gcd32(bit)
#    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
#    print("    InReg = _mm_load_si128(in);");
#    for k in range(ceil((length * bit) / 32)):
#      for x in range(inwordpointer,32,bit):
#        if(valuecounter == length/nbrloop): break
#        if (x > 0):
#          print("    tmp = _mm_srli_epi32(InReg," + str(x) +");"); 
#        else:
#          print("    tmp = InReg;"); 
#        if(x+bit<32):
#          print("    OutReg = _mm_and_si128(tmp, mask);");
#        else:
#          print("    OutReg = tmp;");        
#        if((x+bit>=32) ):      
#          while(inwordpointer<32):
#            inwordpointer += bit
#          if(valuecounter + 1 < length):
#             print("    ++in;")
#          inwordpointer -= 32;
#          if(inwordpointer>0):
#            print("    OutReg = _mm_or_si128(OutReg, _mm_slli_epi32(_mm_and_si128(InReg, mask), " + str(bit) + "-" + str(inwordpointer) + "));");
#        print("    _mm_store_si128(out++, OutReg);\n"); 
#        valuecounter = valuecounter + 1
#        if(valuecounter == length/nbrloop): break
#    assert(valuecounter == length/nbrloop)
#    print("  }"); 
#    print("\n}\n\n")


  print("""
void simdunpack(const __m128i *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: SIMD_nullunpacker"+str(length)+"(in,out); return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_fastunpack"+str(bit)+"_"+str(length)+"(in,out); return;\n")
  print("""        default: break;    
    }
    throw logic_error("number of bits is unsupported");
}
""")
  
  
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
void simdpackwithoutmask(const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_fastpackwithoutmask"+str(bit)+"_"+str(length)+"(in,out); return;\n")
  print("""        default: break;    
    }
    throw logic_error("number of bits is unsupported");
}
  """)

  
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
void simdpack(const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("        case 0: return;\n")
  for bit in range(1,33):
    print("        case "+str(bit)+": __SIMD_fastpack"+str(bit)+"_"+str(length)+"(in,out); return;\n")
  print("""        default: break;    
    }
    throw logic_error("number of bits is unsupported");
}
  """)
print("""

void SIMD_fastunpack_32(const __m128i *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    simdunpack(in,out, bit);
}
void SIMD_fastpackwithoutmask_32(const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    simdpackwithoutmask(in,out, bit);
}
void SIMD_fastpack_32(const uint32_t *  __restrict__ in, __m128i *  __restrict__  out, const uint32_t bit) {
    simdpack(in,out, bit);
}
""")