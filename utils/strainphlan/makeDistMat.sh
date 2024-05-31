#!/bin/bash
echo 'maker of distance matrix from multiple alignment'
echo ' feed it with .aln file (multiple alignment)'
echo 'NOTE: make sure conda is loaded'
distmat -sequence ${1} -nucmethod 2 -outfile ${1/.aln/.dmat}
