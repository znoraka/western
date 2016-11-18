#!/bin/bash

echo "set terminal png
set output '$1'
plot 'histo.txt' with points title '$2'" | gnuplot
