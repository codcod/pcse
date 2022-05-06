#!/usr/bin/env bash

file=./pcse/asyncio/priority_queue/priority_queue.py

declare -a params
params=( \
    '--sleep=5 --uvloop --producers=1 --consumers=1 --count=5 --log-level=info'
    '--sleep=0 --uvloop --producers=8 --consumers=8 --count=100000 --log-level=warning'
    '--sleep=1 --uvloop --producers=8 --consumers=8 --log-level=error'
    '--sleep=30 --uvloop --producers=8 --consumers=8 --log-level=error'
    '--sleep=0 --uvloop --producers=2 --consumers=2 --log-level=error'
    '--sleep=30 --uvloop --producers=2 --consumers=2 --log-level=error'
    '--sleep=30 --uvloop --producers=1 --consumers=1 --log-level=warning'
)

for i in "${!params[@]}"; do
    p="${params[$i]}"
    printf '\n*********************************************************\n'
    printf "ROUND $i\nPARAMS: $p\n\n"
    python $file $p
done

# vim: ft=sh:sw=4:et:ai
