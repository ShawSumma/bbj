
class Subleq():
    def __init__(self):
        self.pc = 0
        self.memory = {}
        self.f1 = 

    def read(self, addr):
        if addr in self.memory:
            return self.memory[addr]
        else:
            return 0
        
    def write(self, addr, data):
        self.memory[addr] = data

    def next(self):
        ret = self.read(self.pc)
        self.pc += 1
        return ret

    def run(self):
        a = self.next()
        b = self.next()
        c = self.next()
        self.write(a, self.read(a) - self.read(b))
        self.
        

def main():
    pass

if __name__ == '__main__':
    main()
