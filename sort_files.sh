#!/usr/bin/sh

for file in public/*/*/*.txt; do
    sort -o $file $file
done
