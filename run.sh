#!/usr/bin/env sh

python3 asm.py "$1" && \
    cc -O2 run.c -o out/run && \
    ./out/run out/out.bb32
