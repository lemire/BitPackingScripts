#!/usr/bin/env python

# ./genbitpacking.py  > BitPackingWithReducedArrayAccess.java
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


print("""


import java.util.Arrays;

public final class BitPackingWithReducedArrayAccess {

	""")



for bit in range(1,32):
  print("\n\npublic static void fastpackwithoutmask"+str(bit)+"(final int [] in, int inpos,  final int [] out, int outpos) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(bit ==32):
        print("    out[",outcounter," + outpos] = in[",incounter," + inpos];");
      elif(x!=0):
        print("    out[",outcounter," + outpos] |= ( in[",incounter," + inpos]  ) << ",x,";");
      else:
        print("    out[",outcounter," + outpos] = in[",incounter," + inpos] ;");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        outcounter = outcounter + 1
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    out[",outcounter," + outpos] =  ( in[",incounter," + inpos] ) >>> (",bit," - ",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        incounter  = incounter + 1
  print("}\n\n")



for bit in range(1,32):
  print("\n\npublic static void fastpack"+str(bit)+"(final int [] in, int inpos,  final int [] out, int outpos) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(bit ==32):
        print("    out[",outcounter," + outpos ] = in[",incounter," + inpos];");
      elif(x!=0):
        if(x+bit<32):
          print("    out[",outcounter," + outpos ] |= ( in[",incounter,"+ inpos] ",mask(bit)," ) << ",x,";");
        else:
          print("    out[",outcounter," + outpos ] |= ( in[",incounter,"+ inpos] ) << ",x,";");
      else:
        print("    out[",outcounter," + outpos ] = in[",incounter,"+ inpos] ",mask(bit),";");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        outcounter = outcounter + 1
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    out[",outcounter," + outpos ] =  ( in[",incounter,"+ inpos] ",mask(bit),") >>> (",bit," - ",inwordpointer,");")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        incounter  = incounter + 1
  print("}\n\n")


for bit in range(1,32):
  print("\n\npublic static void fastunpack"+str(bit)+"(final int [] in, int inpos,  final int [] out, int outpos) {");
  inwordpointer = 0
  outcounter = 0
  incounter = 0
  print("    int source = in[0 + inpos];")
  for k in range((32 * bit) // 32):
    for x in range(inwordpointer,32,bit):
      if(x + bit < 32):
        print("    out[",outcounter," + outpos] = ( source >>> ",x," ) ",mask(bit),";");
      elif (x + bit == 32):
        print("    out[",outcounter," + outpos] = ( source >>> ",x," ) ;");
      else :
        print("    out[",outcounter," + outpos] = ( source >>> ",x," ) ");
      if((x+bit>=32) and (k<((32 * bit) // 32) - 1)):
        while(inwordpointer<32):
          inwordpointer += bit
        incounter  = incounter + 1
        inwordpointer -= 32;
        if(inwordpointer>0):
          print("    | ((source = in[",incounter,"+ inpos]) ",mask(inwordpointer),")<<(",bit,"-",inwordpointer,");")
          #print("    out[",outcounter," + outpos] |= ((source = in[",incounter,"+ inpos]) ",mask(inwordpointer),")<<(",bit,"-",inwordpointer,");")
        else :
         print("    source = in[",incounter,"+ inpos];")
      if((x+bit<32) or (k<((32 * bit) // 32) - 1)):
        outcounter = outcounter + 1
  print("}\n\n")


print("""

public static void fastunpack32(final int [] in, int inpos,  final int [] out, int outpos) {
	System.arraycopy(in, inpos, out, outpos, 32);
}


public static void fastpack32(final int [] in, int inpos,  final int [] out, int outpos) {
	System.arraycopy(in, inpos, out, outpos, 32);
}


public static void fastpackwithoutmask32(final int [] in, int inpos,  final int [] out, int outpos) {
	System.arraycopy(in, inpos, out, outpos, 32);
}


public static void fastunpack0(final int [] in, int inpos,  final int [] out, int outpos) {
	Arrays.fill(out,outpos,outpos+32,0);
}


public static void fastpack0(final int [] in, int inpos,  final int [] out, int outpos) {
	// nothing
}


public static void fastpackwithoutmask0(final int [] in, int inpos,  final int [] out, int outpos) {
	// nothing
}

""")




print("""
public static void fastunpack(final int [] in, int inpos,  final int [] out, int outpos, final int bit) {
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\tfastunpack"+str(bit)+"(in,inpos,out,outpos);\n\t\t\t	break;")
print("""\t\t\tdefault:
\t\t\t\tthrow new IllegalArgumentException(\"Unsupported bit width.\");
	}
}
""")


print("""
public static void fastpack(final int [] in, int inpos,  final int [] out, int outpos, final int bit) {
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\tfastpack"+str(bit)+"(in,inpos,out,outpos);\n\t\t\t	break;")
print("""\t\t\tdefault:
\t\t\t\tthrow new IllegalArgumentException(\"Unsupported bit width.\");
	}
}
""")



print("""
public static void fastpackwithoutmask(final int [] in, int inpos,  final int [] out, int outpos, final int bit) {
	switch(bit) {""")
for bit in range(0,33):
  print("\t\t\tcase "+str(bit)+":\n\t\t\t\tfastpackwithoutmask"+str(bit)+"(in,inpos,out,outpos);\n\t\t\t	break;")
print("""\t\t\tdefault:
\t\t\t\t throw new IllegalArgumentException(\"Unsupported bit width.\");
	}
}
""")

print("}")
