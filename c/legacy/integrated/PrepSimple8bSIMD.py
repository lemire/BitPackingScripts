#!/usr/bin/env python3
# ./PrepSimple8bSIMD.py > simdsimple8decfunc.h 

from math import ceil

def Join(l):
  res = []
  for v in l:
    res.append(str(v))

  return ",".join(res)

# Precomputing constants doesn not help to improve performance _mm_set* functions are quite fast
def GenerateFunc(bit, StartByte, PreCompConsts = 0):
  NumberOfValuesCoded = 60 // bit
  #print("{0} -> {1}".format(bit, NumberOfValuesCoded))

  ShuffleMasks = dict()
  ShuffleMaskNum = 1
  MulMasks = dict()
  MulMaskNum = 1
  AndMasks = dict()
  AndMaskNum = 1

  print("// To prevent buffer overrun, the destination buffer should have extra 16 bytes (extra 4 integers)!")
  print("template <class DeltaHelper>")
  print("inline void Simple8bSIMDUnpack{0}_{1}_{2}(__m128i code, uint32_t *&out, __m128i& initoffset) {{".format(NumberOfValuesCoded, bit, StartByte))
  print("    __m128i tmp, tmps;")
  print("    __m128i* pCurr = reinterpret_cast<__m128i*>(out);");

  func = ""

  print("// Number of values decoded " + str(NumberOfValuesCoded))
  PrevShuffleMask = ""
  for n4 in range(0, (NumberOfValuesCoded + 3) // 4):
    Num2Decode = min(NumberOfValuesCoded - n4 * 4, 4)
    FirstNum = n4 * 4;
    #print("FirstNum: {0} Num2Decode: {1}".format(FirstNum, Num2Decode))
  
    mask = []
    SrcShift = []
    DescStr = []
    for i in range(0, Num2Decode):
      AddModulo = 60 % Num2Decode
      StartBit = 60 - (i + FirstNum + 1) * bit + AddModulo
      EndBit   = StartBit + bit - 1
      DescStr.append("   // Bit field for num {0}: {1}-{2}".format(4 *n4 + i + 1,StartBit, EndBit)+'\n')
      SrcBytes = []

      SrcShift.append(StartBit % 8)
      pb = -1
      for k in range(StartBit, EndBit + 1):
        b = k // 8
        if (b != pb):
          pb = b
          SrcBytes.insert(0, b)
        

      for byte in range(0,4):
        if byte >= len(SrcBytes):
          mask.insert(0, -128)
        else:
          # In SrcBytes the bytes are stored in reversed order, starting from the most significant
          mask.insert(0, StartByte + SrcBytes[-1 - byte])
      DescStr[-1] = DescStr[-1] + "   // SrcBytes:  {0}".format(SrcBytes) + '\n'

    MaxShift = max(SrcShift)

    for i in range(Num2Decode, 4): 
      SrcShift.append(0)
      for j in range(0,4):
        mask.insert(0, -128)

    AddShift = [MaxShift -SrcShift[0], MaxShift - SrcShift[1], MaxShift - SrcShift[2], MaxShift - SrcShift[3]]
    for i in range(0, Num2Decode): 
      func = func + DescStr[i]
      func = func + '   // Shift from the byte beg.:' + str(SrcShift[i]) + " Complem. shift: " + str(AddShift[i]) + '\n//================================\n'

    Mul = []
    for j in range(0, 4):
      Mul.insert(0, 1<<AddShift[j])


    t = Join(mask)

    if not t in ShuffleMasks:
      ShuffleMasks[t] = str(ShuffleMaskNum)
      ShuffleMaskNum = ShuffleMaskNum + 1

    if t != PrevShuffleMask:
      if PreCompConsts:
        func = func + "   tmps = _mm_shuffle_epi8(code, ShuffleMask" + ShuffleMasks[t] + ");\n"
      else:
        func = func + "   tmps = _mm_shuffle_epi8(code, _mm_set_epi8(" + Join(mask) + "));\n"
      PrevShuffleMask = t
    else:
      func = func + "//   tmps = _mm_shuffle_epi8(code, _mm_set_epi8(" + Join(mask) + "));\n"


    t = Join(Mul)

    if not t in MulMasks:
      MulMasks[t] = str(MulMaskNum)
      MulMaskNum = MulMaskNum + 1

    if PreCompConsts:
      func = func + "   tmp = _mm_mullo_epi32(tmps, MulMask" + MulMasks[t] + ");\n"
    else:
      func = func + "   tmp = _mm_mullo_epi32(tmps, _mm_set_epi32(" + Join(Mul) + "));\n"

    # _mm_mullo_epi32 is a signed multiplication
    # We need an unsigned one. Hence, we don't want to mess with the sign bit 
    if MaxShift + bit > 31:
      print("Cannot process bit case: {}". str(bit))
      sys.exit(1)


    if not MaxShift in AndMasks:
      AndMasks[MaxShift] = str(AndMaskNum)
      AndMaskNum = AndMaskNum + 1

    if PreCompConsts:
      func = func + "   tmp = _mm_and_si128(tmp, AndMask" + AndMasks[MaxShift] + ");\n"
    else:
      func = func + "   tmp = _mm_and_si128(tmp, _mm_set1_epi32(" + str((1<<(MaxShift+bit)) - 1) + "));\n"

    func = func + "   tmp = _mm_srli_epi32(tmp, " + str(MaxShift) + ");\n"

    func = func + "   initoffset = DeltaHelper::PrefixSum(tmp, initoffset);\n";
  
    func = func + "   _mm_storeu_si128(pCurr++ , initoffset);\n"

  if PreCompConsts:
    for k,v in ShuffleMasks.items():
      print("   const static __m128i ShuffleMask{0} = _mm_set_epi8({1});".format(v, k))
  if PreCompConsts:
    for k,v in MulMasks.items():
      print("   const static __m128i MulMask{0} = _mm_set_epi32({1});".format(v, k))
  if PreCompConsts:
    for k,v in AndMasks.items():
      print("   const static __m128i AndMask{0} = _mm_set1_epi32({1});".format(v, (1<<(k+bit))-1))

  print(func)
  print("   out += " + str(NumberOfValuesCoded) + ";")
  print("}")

print("#ifndef SIMP_SIMPLE8B_DECFUNC_H")
print("#define SIMP_SIMPLE8B_DECFUNC_H")
print("""
#ifndef __SSE4_1__
#pragma message "No SSSE4.1 support? try adding -msse4.1"
#endif
#include "common.h"
""")

#for bit in (1,2,3,4,5,6,7,8,10,12,15,20,30):
# The case of b == 30 cannot be handled by the code below,
# b/c the encoded values spans over five bytes. Hence,
# it cannot be processed using a single shuffle instruction without blend!
for bit in (1,2,3,4,5,6,7,8,10,12,15,20):
  GenerateFunc(bit, 0)
  GenerateFunc(bit, 8)

print("#endif")

