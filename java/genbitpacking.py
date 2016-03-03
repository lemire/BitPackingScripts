#!/usr/bin/env python

# ./genbitpacking.py  > BitPacking.java
minlengthofloop = 2


def gcd32(x):
  count = 0
  while(x//2 * 2 == x):
    x = x//2
    count = count + 1
  return count
def mask(bit):
  if(bit==1):
    return " & 1"
  if(bit<32):
    return " & "+str((1<<bit) - 1)+""
  return ""


print("public final class BitPacking {")
for bit in range(1,33):
  if( (bit==4) or (bit==8) or (bit ==16) ): continue
  print("\n\npublic static void fastpack"+str(bit)+"(final int [] in, final int [] out) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  isopen = False
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(x!=0): 
        #print("    out[",outcounter,"] |= ( in[",incounter,"] ",mask(bit)," ) << ",x,";");
        print("     | ( ( in[",incounter,"] ",mask(bit)," ) << ",x," ) ");
      else: 
        if(isopen) print("    ;")
        print("    out[",outcounter,"] = ( in[",incounter,"] ",mask(bit)," ) ");
        isopen = True
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        outcounter = outcounter + 1
        inwordpointer -= 32;
        if(inwordpointer>0):
          if(isopen) print("    ;")
          print("    out[",outcounter,"] =  ( in[",incounter,"] ",mask(bit),") >>> (",bit," - ",inwordpointer,")")
          isopen = True
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        incounter  = incounter + 1 
  print("}\n\n")
  

for bit in range(1,33):
  if( (bit==4) or (bit==8) or (bit ==16) ): continue
  print("\n\npublic static void fastunpack"+str(bit)+"(final int [] in, final int [] out) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  isopen = False
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(isopen):
        print ("    ;");
      print("    out[",outcounter,"] = (( in[",incounter,"] >>> ",x," ) ",mask(bit),") ");
      isopen = True
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):      
        while(inwordpointer<32):
          inwordpointer += bit 
        incounter  = incounter + 1 
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    | ((in[",incounter,"] ",mask(inwordpointer),")<<(",bit,"-",inwordpointer,"))")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        outcounter = outcounter + 1
  print("}\n\n")



for bit in [4,8,16]:
  print("\n\npublic static void fastunpack"+str(bit)+"(final int [] in, final int [] out) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  nbrloop = 1<<gcd32(bit)
  if(nbrloop>1):
    print("  for(int outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(inwordpointer,32,bit))
    if(mylen>=minlengthofloop):
      print("    for( int i = ",inwordpointer,";i<32/",bit,"; i++) ");
      print("      out[i] = ( in[outer] >>> (i * ",bit,") ) ",mask(bit),";");
      outcounter = outcounter + 1
    else: 
      for x in range(inwordpointer,32,bit):
        print("    out[",outcounter,"] = ( in[",incounter,"] >>> ",x," ) ",mask(bit),";");
        outcounter = outcounter + 1
    if(k<((32 * bit) // 32) - 1):
      while(inwordpointer<32):
        inwordpointer += bit
      incounter = incounter + 1
      inwordpointer -= 32;
      break
  if(nbrloop>1):
    print("  }")
  print("}\n\n")


for bit in [4,8,16]:
  print("\n\npublic static void fastpack"+str(bit)+"(final int [] in, final int [] out) {");
  inwordpointer = 0
  nbrloop = 1<<gcd32(bit)
  if(nbrloop>1):
    print("  for(int outer=0; outer<",nbrloop,";++outer) {");
  for k in range((32 * bit) // 32):
    mylen = len(range(inwordpointer,32,bit))
    for x in range(inwordpointer,32,bit):
        if(bit ==32):
          print("    out[",outcounter,"] = in[",incounter,"];");
          incounter  = incounter + 1 
        elif(x!=0): 
          print("    out[",outcounter,"] |=  ( in[",incounter,"] ",mask(bit)," )<< ",x,"   ;");
          incounter  = incounter + 1 
        else: 
          print("    out[",outcounter,"] = ( in[",incounter,"] )  ",mask(bit)," ;");
          incounter  = incounter + 1 
    if(k<((32 * bit) // 32) - 1):
      while(inwordpointer<32):
        inwordpointer += bit
      outcounter = outcounter + 1
      inwordpointer -= 32;
      break
  if(nbrloop>1):
    print("  }")
  print("}\n\n")



  
print("""
public static void fastunpack(final int [] in, final int [] out, final int bit) {
	switch(bit) {""")
for bit in range(1,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\tfastunpack"+str(bit)+"(in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")


print("""
public static void fastpack(final int [] in, final int [] out,int bit) {
	switch(bit) {""")
for bit in range(1,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\tfastpack"+str(bit)+"(in,out);\n\t\t\t	break;")
print("""\t\t\tdefault: 
\t\t\t\tbreak;		
	}
}
""")
print("}")
