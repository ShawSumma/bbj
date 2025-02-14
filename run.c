
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define PROFILE 0
#define USE_SAFE 1
#define MEMORY_WORDS (1 << 24)

int main(int argc, char **argv) {
    if (argv[0] == NULL) {
        return 1;
    }
    if (argv[1] == NULL) {
        fprintf(stderr, "please give bb32 a file at the command line\n");
        return 1;
    }
    FILE *f = fopen(argv[1], "rb");
    if (f == NULL) {
        fprintf(stderr, "no such file: %s\n", argv[1]);
        return 1;
    }
    uint32_t *mem = calloc(1, sizeof(uint32_t) * MEMORY_WORDS);
    size_t write_head = 0;
    while (true) {
        uint8_t buf[4];
        size_t nread = fread(buf, 4, 1, f);
        if (nread != 1) {
            break;
        }
        mem[write_head++] = ((uint32_t) buf[0]) | ((uint32_t) buf[1] << 8) | ((uint32_t) buf[2] << 16) | ((uint32_t) buf[3] << 24);
        // printf("0x%zX 0x%zX\n", (size_t) (write_head * 32 - 32), (size_t) mem[write_head-1]);
    }
#if PROFILE & 2
    clock_t t1 = clock();
#endif
    uint32_t pc = *mem++;
#if PROFILE & 1
    size_t num = 0;
#endif
    while (true) {
#if PROFILE & 1
        num += 1;
#endif
        uint32_t last_pc = pc;

        uint32_t a = pc + mem[pc / 32 + 0];
        uint32_t b = pc + mem[pc / 32 + 1];
        uint32_t c = pc + mem[pc / 32 + 2];

        // printf("0x%zX: 0x%zX 0x%zX 0x%zx\n", (size_t) pc, (size_t) a, (size_t) b, (size_t) c);

#if USE_SAFE
        if (a / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid write to 0x%zx\n", (size_t) a);
            return 1;
        }

        if (b / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid read from 0x%zx\n", (size_t) b);
            return 1;
        }

        if (c / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid jump to 0x%zx\n", (size_t) c);
            return 1;
        }
#endif

        if (a == b) {
            if (c == pc) {
                break;
            }
            if (a != pc) {
                uint8_t *pvalue = &((uint8_t *) mem)[a / 8];
                // printf("[addr = %zx; value = %zu]", (size_t) a, (size_t) *pvalue);
                if (*pvalue != 0) {
                    fprintf(stdout, "%c", *pvalue);
                    fflush(stdout);
                } else {
                    int c = getchar();
                    if (c == EOF) {
                        c = 0;
                    }
                    *pvalue = c;
                }
            }
        } else {
            mem[a / 32] = (mem[a / 32] & ~(1u << (a % 32))) | (((mem[b / 32] >> (b % 32)) & 1) << (a % 32));
        }

        pc = c;
    }
#if PROFILE & 1
    printf("instrs: %zu\n", num);
#endif
#if PROFILE & 2
    clock_t t2 = clock();
    printf("millis: %f\n", (double) (t2 - t1) / (double) CLOCKS_PER_SEC * 1000);
#endif
}
