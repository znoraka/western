#!/bin/bash

echo "set terminal png
set output '$1'
set style histogram
plot 'histo.txt' with boxes" | gnuplot
