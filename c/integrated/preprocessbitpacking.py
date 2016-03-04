#!/usr/bin/env python3
# ./preprocessbitpacking.py>integratedbitpacking.cpp


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


import re

print("""/**
 * This code is released under the
 * Apache License Version 2.0 http://www.apache.org/licenses/.
 *
 * (c) Daniel Lemire, http://lemire.me/en/
 */""")
#print ("#ifndef INTEGRATEDBITPACKING\n#define INTEGRATEDBITPACKING")
##########################
# we do the special cases (0 and 32)
# separately
##########################
print ("""

void __integratedfastunpack0(const uint32_t initoffset, const uint32_t *  __restrict__ , uint32_t *  __restrict__  out) {
	for(uint32_t i = 0; i<32;++i)
	  *(out++) = initoffset;
}
void __integratedfastpack0(const uint32_t, const uint32_t *  __restrict__ , uint32_t *  __restrict__  ) {
}
""")

print("""


void __integratedfastunpack32(const uint32_t, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
	for(int k = 0 ; k < 32 ;++k)
        out[k] = in[k]; // no sense in wasting time with deltas
}

void __integratedfastpack32(const uint32_t, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
    for(int k = 0 ; k < 32 ;++k)
        out[k] = in[k] ; // no sense in wasting time with deltas
}
""")

################################
# unpacking
################################
for bit in range(1,32):
  if( (bit==1) or (bit==4) or (bit==8) or (bit ==16)): continue
  print("\n\nvoid __integratedfastunpack"+str(bit)+"(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      reference = " out[-1] ";
      if((k == 0) and (x == 0)) : reference = " initoffset ";
      if(bit+x<32):
        print("    *out = ( *in >> ",x," ) ",mask(bit)," ;");
      else: 
        print("    *out = ( *in >> ",x," ) ;");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):      
        while(inwordpointer<32):
          inwordpointer += bit
        print("    ++in;")
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    *out |= (*in % (1U<<",inwordpointer,"))<<(",bit,"-",inwordpointer,");")
      print ("    *out +=   ",reference," ; // integrated delta decoding ") 
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        print("    out++;")
  print("}\n\n")


print(""""


void __integratedfastunpack1(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {
    *out = (  *in    & 1  ) +  initoffset;
    ++out;
    *out = (  (*in >> 1) & 1) + out[-1];
    ++out;
    for( uint32_t i =  2 ; i < 32; i +=  1 ) {
      *out = ( ( *in >> i)   & 1  ) + out[-1];
      ++i;
      ++out;
      *out = ( ( *in >> i)   & 1  ) + out[-1];
      ++out;
    }
}

""")

for bit in [4,8,16]:
  print("\n\nvoid __integratedfastunpack"+str(bit)+"(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  nbrloop = 1<<gcd32(bit)
  for k in range((32 * bit) // 32):
    if(k == 0) : 
      print("    *(out++) = (  *in  ",mask(bit)," ) +  initoffset;");
      print("    for( uint32_t i = ",bit,"; i < 32; i += ",bit,") {");
      print("      *out = ( ( *in >> i ) ",mask(bit)," ) + out[-1];");
      print("      ++out;");
      print("    }");
    else :
      print("    for( uint32_t i = 0; i < 32; i += ",bit,") {");
      print("      *out = ( ( *in >> i ) ",mask(bit)," ) + out[-1];");
      print("      ++out;");
      print("    }");
    if ( k + 1 != (32 * bit) // 32) : print("    ++in;");
  print("}\n\n")




################################
# packing
################################

for bit in range(1,32):
  if( (bit==1) or (bit==4) or (bit==8) or (bit ==16)): continue
  print("\n\n void __integratedfastpack"+str(bit)+"(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {");
  inwordpointer = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      reference = " in[-1] ";
      if((k == 0) and (x == 0)) : reference = " initoffset ";
      if(bit ==32):
        print("    *out = *in - ",reference,";");
      elif(x!=0): 
        if(x+bit<32):
          print("    *out |= ( (*in  - ",reference,") ",carefulmask(bit)," ) << ",x,";");
        else:
          print("    *out |= ( (*in - ",reference,") ) << ",x,";");
      else: 
        print("    *out = (*in - ",reference,") ",carefulmask(bit),";");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        print("    ++out;")
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    *out =  ( (*in - ",reference,") ",carefulmask(bit),") >> (",bit," - ",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        print("    ++in;") 
  print("}\n\n")
  
  




for bit in [1,4,8,16]:
  print("""
  /*assumes that integers fit in the prescribed number of bits*/
  void __integratedfastpack"""+str(bit)+"""(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out) {""");
  nbrloop = 1<<gcd32(bit)
  print("   *out = *(in++) - initoffset ;");
  #if(nbrloop>1): print("  for(uint32_t outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(0,32,bit))
    if(k == 0): 
      print("    for( uint32_t i = ",bit,"; i < 32; i += ",bit,") {");
      print("      *out |= ( *in - in[-1] ) << i ;");
      print("      ++in ;");
      print("    }")
    else:
      print("    *out =  *in - in[-1] ;");
      print("    ++in ;");
      print("    for( uint32_t i = ",bit,"; i < 32; i += ",bit,") {");
      print("      *out |= ( *in - in[-1] ) << i ;");
      print("      ++in ;");
      print("    }")
    if(nbrloop>1): print("    ++out;")
  #if(nbrloop>1): print("  }")
  print("}\n\n")





################################
# switch cases 
################################


  
print("""
void integratedfastunpack(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
	// Could have used function pointers instead of switch.
	// Switch calls do offer the compiler more opportunities for optimization in
	// theory. In this case, it makes no difference with a good compiler.
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\t__integratedfastunpack"+str(bit)+"(initoffset,in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")





print("""

/*assumes that integers fit in the prescribed number of bits*/
void integratedfastpack(const uint32_t initoffset, const uint32_t *  __restrict__ in, uint32_t *  __restrict__  out, const uint32_t bit) {
	// Could have used function pointers instead of switch.
	// Switch calls do offer the compiler more opportunities for optimization in
	// theory. In this case, it makes no difference with a good compiler.
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\t__integratedfastpack"+str(bit)+"(initoffset,in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")



#print ("#endif // INTEGRATEDBITPACKING")
