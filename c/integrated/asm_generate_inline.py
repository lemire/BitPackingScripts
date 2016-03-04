
class InlineSSE:
    commentTemplate = '"# {text}\\n\\t"\n'
    commandTemplate = '"{command} {source}, {target}\\n\\t"\n'
    maskVar = "%%xmm15"
    offsetVar = "%0"

    loadVar = "%1"
    storeVar = "%2"

    def reg(self, cycle): return "%%xmm" + str(cycle % 10)

    def header(self, bits, stores, loads, masks, adds, shifts):
        shift7 = ""
        if shifts[7] > 0:
            shift7 = '"psrld ${SHIFT}, %%xmm1\\n\\t"'.format(SHIFT=shifts[7])
        assert not shifts[7] < 0

        shift8 = ""
        if shifts[8] > 0:
            shift8 = '"psrld ${SHIFT}, %%xmm2\\n\\t"'.format(SHIFT=  shifts[8])
        if shifts[8] < 0:
            shift8 = '"pslld ${SHIFT}, %%xmm2\\n\\t"'.format(SHIFT= -shifts[8])

        if bits == 32:
            mask1 = ""
            mask2 = ""
            mask7 = ""
        else:
            mask1 = '"pcmpeqd   %%xmm15, %%xmm15   \\n\\t"'            
            mask2 = '"psrld     $(32 - %d), %%%%xmm15 \\n\\t"' % bits
            mask7 = '"pand      %%xmm15, %%xmm0  \\n\\t"'

        if bits == 16 or bits == 32:
            mask8 = ""
        else:
            mask8 = '"pand      %%xmm15, %%xmm1  \\n\\t"'



        return """



__m128i asmsimdunpack{BITS}(__m128i offset,
                                const  __m128i*  __restrict__ in,
                                uint32_t *  __restrict__ out) {{


__asm__ __volatile__("\\n\\t"
{MASK1}
"movdqa    {OFFSET}, %%xmm14    # move 'offset' somewhere safe   \\n\\t"
"movdqa    {LOADS[0]}*16(%1), %%xmm0    # read 'in'         \\n\\t"
"movdqa    {LOADS[1]}*16(%1), %%xmm1    # and again         \\n\\t"

"movdqa    {LOADS[2]}*16(%1), %%xmm2                        \\n\\t"
"movdqa    {LOADS[3]}*16(%1), %%xmm3                        \\n\\t"
{MASK2}

"movdqa    {LOADS[4]}*16(%1), %%xmm4                        \\n\\t"
"movdqa    {LOADS[5]}*16(%1), %%xmm5                        \\n\\t"
       
"movdqa    {LOADS[6]}*16(%1), %%xmm6                        \\n\\t"
"movdqa    {LOADS[7]}*16(%1), %%xmm7                        \\n\\t"
{MASK7}
{SHIFT7}

"movdqa    {LOADS[8]}*16(%1), %%xmm8                        \\n\\t"
"paddd     %%xmm14, %%xmm0    # add the inital offset          \\n\\t"
{MASK8}
{SHIFT8}
""".format(OFFSET=self.offsetVar,BITS=bits, LOADS=loads, SHIFTS=shifts, SHIFT7=shift7, SHIFT8=shift8,
           MASK1=mask1, MASK2=mask2, MASK7=mask7, MASK8=mask8)
    
    def footer(self, bits):
        return """
		: "+x" (offset) :  "r" (in), "r" (out)
     ); // asm

	return  offset;
}
"""

    def add(self, target, source):
        return self.commandTemplate.format(command = "paddd", 
                             source = source,
                             target = target)
        
    def shiftr(self, target, bits):
        return self.commandTemplate.format(command = "psrld", 
                         source = "$" + str(bits),
                         target = target)

    def shiftl(self, target, bits):
        return self.commandTemplate.format(command = "pslld", 
                             source = "$" + str(bits),
                             target = target)
        
    def mask(self, target):
        return self.commandTemplate.format(command = "pand", 
                             source = self.maskVar,
                             target = target)
    
    def load(self, target, memoryOffset):
        memoryOffset = memoryOffset * 16
        return self.commandTemplate.format(command = "movdqa", 
                             source = str(memoryOffset)+ "("+self.loadVar+")",
                             target = target)
                              
    def copy(self, target, source):
        return self.commandTemplate.format(command = "movdqa", 
                             source = source,
                             target = target)
    
    def store(self, source, memoryOffset):
        memoryOffset = memoryOffset * 16
        return self.commandTemplate.format(command = "movdqa", 
                             target = str(memoryOffset) + "("+self.storeVar+")",
                             source = source)

    def comment(self, text):
        return self.commentTemplate.format(text = text)
