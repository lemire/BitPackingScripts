#!/usr/bin/env python3
SIMPLE8B_LOGDESC = 4;

def gen(Q, log1):
  mask = ((1) << log1) - 1

  print('static inline void unpack{}_{}(uint32_t *&out, const uint64_t *&in, uint32_t& initoffset) {{'.format(Q, log1))
  print('    const uint64_t val = *in++;')

  for k in range(0, Q):
    print('    *out = initoffset + (static_cast<uint32_t> ((val >> {}) & {})); initoffset = *out++;'.format(64 - SIMPLE8B_LOGDESC - log1 - k * log1, mask))
  print('}\n')

for log1 in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30]:
  gen(60 // log1, log1)
