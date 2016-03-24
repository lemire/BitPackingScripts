#!/usr/bin/env python
# ./preprocessbitpacking.py>bitpacking.h

minlengthofloop = 2
#mainop="*(out + k) = ( (*in + (k * bit ) / 32 ) >> ( ( k * bit) % 32) ) % (1U << bit);"
#overflow="*(out + %d) = (*in + (%d * bit ) / 32 + 1) % (1U<<(bit - 32 + ((%d * bit) % 32)));"

def gcd32(x):
  count = 0
  while(x//2 * 2 == x):
    x = x//2
    count = count + 1
  return count


def carefulmask(bit):
  return mask(bit)
  
def mask(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " % (1U << "+str(bit)+" )"
  return ""

def altmask(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " & "+str((1<<bit) - 1)+""
  return ""


import re

print("""/**
 * This code is released under the
 * Apache License Version 2.0 http://www.apache.org/licenses/.
 *
 * (c) Daniel Lemire, http://lemire.me/en/
 */""")
print ("#ifndef BITPACKING\n#define BITPACKING")


print ("""

void __fastunpack0(const uint32_t *  __restrict__ , uint32_t *  __restrict__  out) {
	for(uint32_t i = 0; i<32;++i)
	  *(out++) = 0;
}
void __fastpack0(const uint32_t *  __restrict__ , uint32_t *  __restrict__  ) {
}
void __fastpackwithoutmask0(const uint32_t *  __restrict__ , uint32_t *  __restrict__  ) {
}
""")

print("""

void __fastunpack32(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
    for(int k = 0 ; k <32 ;++k)
        out[k] = in[k];
}
void __fastpack32(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
    for(int k = 0 ; k <32 ;++k)
        out[k] = in[k];
}

void __fastpackwithoutmask32(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
    for(int k = 0 ; k <32 ;++k)
        out[k] = in[k];
}
""")

for bit in range(1,32):
  if( (bit==4) or (bit==8) or (bit ==16)): continue
  print("\n\nvoid __fastunpack"+str(bit)+"(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(bit+x<32):
        print("    *out = ( (*in) >> ",x," ) ",mask(bit),";");
      else: 
        print("    *out = ( (*in) >> ",x," ) ;");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):      
        while(inwordpointer<32):
          inwordpointer += bit
        print("    ++in;")
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    *out |= ((*in) % (1U<<",inwordpointer,"))<<(",bit,"-",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        print("    out++;")
  print("}\n\n")


for bit in [4,8,16]:
  print("\n\nvoid __fastunpack"+str(bit)+"(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  nbrloop = 1<<gcd32(bit)
  if(nbrloop>1):
    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(inwordpointer,32,bit))
    if(mylen>=minlengthofloop):
      print("    for( uint32_t inwordpointer = ",inwordpointer,";inwordpointer<32; inwordpointer += ",bit,") ");
      print("      *(out++) = ( (*in) >> inwordpointer ) ",mask(bit),";");
    else: 
      for x in range(inwordpointer,32,bit):
        print("    *(out++) = ( (*in) >> ",x," ) ",mask(bit),";");
    if(k<((32 * bit) // 32) - 1):
      while(inwordpointer<32):
        inwordpointer += bit
      print("    ++in;")
      inwordpointer -= 32;
      if(inwordpointer>0):
        print("    *(out-1) |= ((*in) % (1U<<",inwordpointer,"))<<(",bit,"-",inwordpointer,");")
      else:
        break
  if(nbrloop>1):
    print("  }")
  print("}\n\n")



for bit in range(1,32):
  #if( (bit==4) or (bit==8) or (bit ==16)): continue
  print("\n\nvoid __fastpack"+str(bit)+"(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(bit ==32):
        print("    *out = *in;");
      elif(x!=0): 
        if(x+bit<32):
          print("    *out |= ( (*in) ",carefulmask(bit)," ) << ",x,";");
        else:
          print("    *out |= ( (*in) ) << ",x,";");
      else: 
        print("    *out = (*in) ",carefulmask(bit),";");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        print("    ++out;")
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    *out =  ( (*in) ",carefulmask(bit),") >> (",bit," - ",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        print("    ++in;") 
  print("}\n\n")
  
  


for bit in []:
  print("\n\nvoid __fastpack"+str(bit)+"(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  nbrloop = 1<<gcd32(bit)
  if(nbrloop>1):
    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(inwordpointer,32,bit))
    if(mylen>=minlengthofloop):
      assert(inwordpointer == 0)
      print("    *out = ((*(in++)) ",carefulmask(bit)," ) ;");
      print("    for( uint32_t inwordpointer = ",inwordpointer+bit,";inwordpointer<32; inwordpointer += ",bit,") ");
      print("      *out |= ((*(in++)) ",carefulmask(bit)," ) << inwordpointer  ;");
    else: 
      for x in range(inwordpointer,32,bit):
        if(bit ==32):
          print("    *out = *(in++);");
        elif(x!=0): 
          print("    *out |=  ( (*(in++)) ",carefulmask(bit)," )<< ",x,"   ;");
        else: 
          print("    *out = ( *(in++) )  ",carefulmask(bit)," ;");
    if(k<((32 * bit) // 32) - 1):
      while(inwordpointer<32):
        inwordpointer += bit
      print("    ++out;")
      inwordpointer -= 32;
      if(inwordpointer>0):
        print("    *out =  ((*(in-1)) ",carefulmask(bit),")  >> (",bit," - ",inwordpointer,") ;")
      else:
        break
  if(nbrloop>1):
    print("  }")
  print("}\n\n")




for bit in range(1,32):
  #if( (bit==4) or (bit==8) or (bit ==16)): continue
  print("""  
  /*assumes that integers fit in the prescribed number of bits */
  void __fastpackwithoutmask"""+str(bit)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {""");
  inwordpointer = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(bit ==32):
        print("    *out = *in;");
      elif(x!=0): 
        print("    *out |= ( (*in)  ) << ",x,";");
      else: 
        print("    *out = (*in) ;");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        print("    ++out;")
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    *out =  ( (*in) ) >> (",bit," - ",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        print("    ++in;") 
  print("}\n\n")
  
  


for bit in []:
  print("""
  
  /*assumes that integers fit in the prescribed number of bits*/
  void __fastpackwithoutmask"""+str(bit)+"""(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {""");
  inwordpointer = 0
  nbrloop = 1<<gcd32(bit)
  if(nbrloop>1):
    print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(inwordpointer,32,bit))
    if(mylen>=minlengthofloop):
      assert(inwordpointer==0)
      print("    *out = ((*(in++))  )   ;");
      print("    for( uint32_t inwordpointer = ",inwordpointer+bit,";inwordpointer<32; inwordpointer += ",bit,") ");
      print("      *out |= ((*(in++))  ) << inwordpointer  ;");
    else: 
      for x in range(inwordpointer,32,bit):
        if(bit ==32):
          print("    *out = *(in++);");
        elif(x!=0): 
          print("    *out |=  ( (*(in++))  )<< ",x,"   ;");
        else: 
          print("    *out = ( *(in++) )  ;");
    if(k<((32 * bit) // 32) - 1):
      while(inwordpointer<32):
        inwordpointer += bit
      print("    ++out;")
      inwordpointer -= 32;
      if(inwordpointer>0):
        print("    *out =  ((*(in-1)) )  >> (",bit," - ",inwordpointer,") ;")
      else:
        break
  if(nbrloop>1):
    print("  }")
  print("}\n\n")





  
print("""
void fastunpack(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
	// Could have used function pointers instead of switch.
	// Switch calls do offer the compiler more opportunities for optimization in
	// theory. In this case, it makes no difference with a good compiler.
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\t__fastunpack"+str(bit)+"(in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")



print("""

void fastpack(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
	// Could have used function pointers instead of switch.
	// Switch calls do offer the compiler more opportunities for optimization in
	// theory. In this case, it makes no difference with a good compiler.
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\t__fastpack"+str(bit)+"(in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")



print("""

/*assumes that integers fit in the prescribed number of bits*/
void fastpackwithoutmask(const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
	// Could have used function pointers instead of switch.
	// Switch calls do offer the compiler more opportunities for optimization in
	// theory. In this case, it makes no difference with a good compiler.
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\t__fastpackwithoutmask"+str(bit)+"(in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")



print ("#endif // BITPACKING")
