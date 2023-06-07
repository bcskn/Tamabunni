#!/bin/env bash

for file in $(ls -1 | grep .bmp); do
    python3 -m tobin $file;
done

cp -v *.bin ../src/img/
