#!/usr/bin/env python
# ./preprocessbitpackingvl.py>bitpackingaligned.h

#print ("// this file is generated automatically by typing ./preprocessunalignedbitpacking.py>bitpackingunaligned.h or the equivalent")

print ("#ifndef BITPACKINGALIGNED\n#define BITPACKINGALIGNED")

from math import ceil


def mask(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " % (1U << "+str(bit)+" )"
  return ""


print("""
uint32_t * nullpacker(const uint32_t *  __restrict__ /*in*/, uint32_t *  __restrict__  out) {
  return out;
}""")


for length in [8,16,24,32]:
  print("""
    const uint32_t * nullunpacker"""+str(length)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
      memset(out,0,"""+str(length)+""" * 4);
      return in;
    }
  """)
  for bit in range(1,33):
    print("""  
    uint32_t * __fastpackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
      """);
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      if(valuecounter == length): break
      for x in range(inwordpointer,32,bit):
        if(x!=0) :
          print("    *out |= ( (*in)  ) << ",x,";");
        else:
          print("    *out =  (*in)  ;");
        if((x+bit>=32) ):
          while(inwordpointer<32):
            inwordpointer += bit
          print("    ++out;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        print("    ++in;") 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    if(length * bit % 32 ==0 ):
      print("""
        return out;
      }\n\n""")
    else : 
      print("""
        return out + 1;
      }\n\n""")  
  
  for bit in range(1,33):
    print("""\n\nconst uint32_t * __fastunpack"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
      """);
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 32)):
      for x in range(inwordpointer,32,bit):
        if(valuecounter == length): break
        if(x+bit<32):
          print("    *out = ( (*in) >> ",x," ) ",mask(bit),";");
        else:
          print("    *out = ( (*in) >> ",x," ) ;");
        if((x+bit>=32) ):      
          while(inwordpointer<32):
            inwordpointer += bit
          print("    ++in;")
          inwordpointer -= 32;
          if(inwordpointer>0):
            print("    *out |= ((*in) % (1U<<",inwordpointer,"))<<(",bit,"-",inwordpointer,");")
        #if(x+bit<32):
        print("    out++;")
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    if(length * bit % 32 ==0 ):
      print("""
        return in;
      }\n\n""")
    else : 
      print("""
        return in + 1;
      }\n\n""")  

  print("""
  const uint32_t * fastunpack_"""+str(length)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullunpacker"+str(length)+"(in,out);\n")
  for bit in range(1,33):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastunpack"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)
  
  
  
  
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
  uint32_t * fastpackwithoutmask_"""+str(length)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullpacker(in,out);\n")
  for bit in range(1,33):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastpackwithoutmask"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)



print ("#endif // BITPACKINGALIGNED")