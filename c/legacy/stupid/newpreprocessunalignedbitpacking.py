#!/usr/bin/env python
# ./newpreprocessunalignedbitpacking.py>bitpackingunaligned.h

#print ("// this file is generated automatically by typing ./preprocessunalignedbitpacking.py>bitpackingunaligned.h or the equivalent")

print ("#ifndef BITPACKINGUNALIGNED\n#define BITPACKINGUNALIGNED")

from math import ceil
print ("typedef uint8_t byte;")


def mask(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " % (1U << "+str(bit)+" )"
  return ""


print("""
typedef const byte * (*runpacker)(const byte *  __restrict__ in, uint32_t *  __restrict__  out);
typedef byte * (*rpacker)(const uint32_t *  __restrict__ in, byte *  __restrict__  out);
""")
print("""
typedef const byte * (*rbyteunpacker)(const byte *  __restrict__ in, byte *  __restrict__  out);
typedef byte * (*rbytepacker)(const byte *  __restrict__ in, byte *  __restrict__  out);
""")


print("""
byte * nullpacker(const uint32_t *  __restrict__ /*in*/, byte *  __restrict__  out) {
  return out;
}""")

print("""
byte * nullbytepacker(const byte *  __restrict__ /*in*/, byte *  __restrict__  out) {
  return out;
}""")

for length in [8,16]: #[8,16,24,32]:
  print("""
    const byte * nullunpacker"""+str(length)+"""(const byte *  __restrict__ in, uint32_t *  __restrict__  out) {
      memset(out,0,"""+str(length)+""" * 4);
      return in;
    }
  """)
  print("""
    const byte * nullbyteunpacker"""+str(length)+"""(const byte *  __restrict__ in, byte *  __restrict__  out) {
      memset(out,0,"""+str(length)+""" );
      return in;
    }
  """)  
  for bit in range(1,33):
    print("""  
    byte * __fastunalignedpackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(const uint32_t *  __restrict__ in, byte *  __restrict__  outbyte) {
      uint32_t *  __restrict__ out = reinterpret_cast<uint32_t *>(outbyte);
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
        #if(x+bit<32) :
        print("    ++in;") 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("""
      return reinterpret_cast<byte *>(out) + """+str((length*bit % 32)//8)+""";
    }\n\n""")
  
  
  for bit in range(1,33):
    print("""\n\nconst byte * __fastunalignedunpack"""+str(bit)+"""_"""+str(length)+"""(const byte *  __restrict__ inbyte, uint32_t *  __restrict__  out) {
      const uint32_t *  __restrict__ in = reinterpret_cast<const uint32_t *>(inbyte);
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
    print("""
      return reinterpret_cast<const byte *>(in)  + """+str((length*bit % 32)//8)+""";
    }\n\n""")

  for bit in range(1,9):
    print("""  
    byte * __fastunalignedbytepackwithoutmask"""+str(bit)+"""_"""+str(length)+"""(const byte *  __restrict__ in, byte *  __restrict__  out) {
      """);
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 8)):
      if(valuecounter == length): break
      for x in range(inwordpointer,8,bit):
        if(x!=0) :
          print("    *out |= ( (*in)  ) << ",x,";");
        else:
          print("    *out =  (*in)  ;");
        if((x+bit>=8) ):
          while(inwordpointer<8):
            inwordpointer += bit
          print("    ++out;")
          inwordpointer -= 8;
          if(inwordpointer>0):
            print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
        print("    ++in;") 
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("""
      return out;
    }\n\n""")
  
  
  for bit in range(1,9):
    print("""\n\nconst byte * __fastunalignedbyteunpack"""+str(bit)+"""_"""+str(length)+"""(const byte *  __restrict__ in, byte *  __restrict__  out) {
      """);
    inwordpointer = 0
    valuecounter = 0
    for k in range(ceil((length * bit) / 8)):
      for x in range(inwordpointer,8,bit):
        if(valuecounter == length): break
        if(x+bit<32):
          print("    *out = ( (*in) >> ",x," ) ",mask(bit),";");
        else:
          print("    *out = ( (*in) >> ",x," ) ;");
        if((x+bit>=8) ):      
          while(inwordpointer<8):
            inwordpointer += bit
          print("    ++in;")
          inwordpointer -= 8;
          if(inwordpointer>0):
            print("    *out |= ((*in) % (1U<<",inwordpointer,"))<<(",bit,"-",inwordpointer,");")
        print("    out++;")
        valuecounter = valuecounter + 1
        if(valuecounter == length): break
    assert(valuecounter == length)
    print("""
      return in;
    }\n\n""")



  print("""
  static const runpacker       unpackarray_"""+str(length)+"""[] = {
          nullunpacker"""+str(length)+""",""")
  for bit in range(1,33):
    print("  __fastunalignedunpack"+str(bit)+"_"+str(length)+",")
  print("""};
  """)
  
  print("""
  static const rpacker       packarray_"""+str(length)+"""[] = {
          nullpacker,""")
  for bit in range(1,33):
    print("  __fastunalignedpackwithoutmask"+str(bit)+"_"+str(length)+",")
  print("""};
  """)
  
  print("""
  const byte * fastunalignedunpack_"""+str(length)+"""(const byte *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullunpacker"+str(length)+"(in,out);\n")
  for bit in range(1,33):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastunalignedunpack"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)
  
  
  
  
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
  byte * fastunalignedpackwithoutmask_"""+str(length)+"""(const uint32_t *  __restrict__ in, byte *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullpacker(in,out);\n")
  for bit in range(1,33):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastunalignedpackwithoutmask"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)








  print("""
  static const rbyteunpacker       byteunpackarray_"""+str(length)+"""[] = {
          nullbyteunpacker"""+str(length)+""",""")
  for bit in range(1,9):
    print("  __fastunalignedbyteunpack"+str(bit)+"_"+str(length)+",")
  print("""};
  """)
  
  print("""
  static const rbytepacker       bytepackarray_"""+str(length)+"""[] = {
          nullbytepacker,""")
  for bit in range(1,9):
    print("  __fastunalignedbytepackwithoutmask"+str(bit)+"_"+str(length)+",")
  print("""};
  """)
  
  print("""
  const byte * fastunalignedbyteunpack_"""+str(length)+"""(const byte *  __restrict__ in, byte *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullbyteunpacker"+str(length)+"(in,out);\n")
  for bit in range(1,9):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastunalignedbyteunpack"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)
  
  
  
  
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
  byte * fastunalignedbytepackwithoutmask_"""+str(length)+"""(const byte *  __restrict__ in, byte *  __restrict__  out, const uint32_t bit) {
    switch(bit) {""")
  print("\t\t\tcase 0: return nullbytepacker(in,out);\n")
  for bit in range(1,9):
    print("\t\t\tcase "+str(bit)+":\n\t\t\t\treturn __fastunalignedbytepackwithoutmask"+str(bit)+"_"+str(length)+"(in,out);\n")
  print("""\t\t\tdefault: 
  \t\t\t\tbreak;    
    }
    throw logic_error("number of bits is unsupported");
  }
  """)














print ("#endif // BITPACKINGUNALIGNED")