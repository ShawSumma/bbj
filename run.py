
MEM_SIZE = 2**24
mem = [0] * MEM_SIZE

write_head = 0

with open('out/out.bb32', 'rb') as f:
    pc = int.from_bytes(f.read(4), byteorder='little')
    while True:
        b = f.read(4)
        if len(b) == 0:
            break
        mem[write_head] = int.from_bytes(b, byteorder='little')
        write_head += 1

stdin = ''

while True:
    a = (pc + mem[pc // 32 + 0]) & 0xFFFFFFFF
    b = (pc + mem[pc // 32 + 1]) & 0xFFFFFFFF
    c = (pc + mem[pc // 32 + 2]) & 0xFFFFFFFF

    if a == b:
        if c == pc:
            break
        if a != pc:
            value = mem[a // 32]
            if value != 0:
                print(chr(value), end='')
            else:
                if len(stdin) == 0:
                    stdin = input() + '\n'
                char = ord(stdin[0])
                stdin = stdin[1:]
                mem[a // 32] = char
    else:
        if mem[b // 32] & (1 << (b % 32)):
            mem[a // 32] |= 1 << (a % 32)
        else:
            mem[a // 32] &= ~(1 << (a % 32))

    pc = c
