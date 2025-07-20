
class RingBuffer:
    def __init__(self, size) -> None:
        self.buffer_size = size
        self.buffer = [None] * size
        self.head_idx = 0
        self.tail_idx = 0
        self.full = False

    def put(self, data):
        if self.full:
            self.get()  # discard oldest
        self.buffer[self.head_idx] = data
        self.head_idx += 1
        if self.head_idx == self.buffer_size:
            self.head_idx = 0
        if self.head_idx == self.tail_idx:
            self.full = True

    def get(self):
        if self.empty(): raise RuntimeError("Buffer is empty")
        data = self.buffer[self.tail_idx]
        self.tail_idx += 1
        if self.tail_idx == self.buffer_size:
            self.tail_idx = 0
        if self.full: 
            self.full = False
        return data
    
    def print_in_order(self):
        tail_idx = self.tail_idx
        head_idx = self.head_idx
        rng = 0
        if head_idx < tail_idx:
            rng = self.size - tail_idx
            rng += head_idx
        else:
            rng = head_idx - tail_idx
        print(rng)
        for i in range (rng):
            idx = self.tail_idx + i 
            idx %= self.size 
            print(idx)
    
    def peek_head(self):
        return self.buffer[self.head_idx]
    def peek_tail(self):
        return self.buffer[self.tail_idx]
    def empty(self):
        return (not self.full) and (self.head_idx == self.tail_idx)
    def full(self):
        return self.full

