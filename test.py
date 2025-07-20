from common.ring_buffer import * 

rb = RingBuffer(4)
rb.put('h')
rb.put('o')
rb.put('l')

print(rb.get())
print(rb.get())
print(rb.get())
rb.put('s')
rb.put('r')
print(rb.get())
print(rb.get())
print(rb.tail_idx, rb.head_idx)