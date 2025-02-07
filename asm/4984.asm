    jmp main

main:
.loop n, 0, 5
    write space + WORD*n
.end
    hlt

space:
    .raw 52
    .raw 57
    .raw 56
    .raw 52
    .raw 10

.macro write n
    mov n, n
.end

.macro mov a, b
    .raw a, b, next
next:
.end

.macro jmp addr
    .raw 0, 0, addr
.end

.macro out addr
    .raw addr, addr, next
next:
.end

.macro hlt
self:
    jmp self
.end 
