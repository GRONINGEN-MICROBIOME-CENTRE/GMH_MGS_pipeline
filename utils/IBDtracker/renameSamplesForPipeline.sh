#!/bin/bash
for i in *_R1_001*.fastq.gz; do mv ${i} ${i/_R1_001./_1.}; done
for i in *_R2_001*.fastq.gz; do mv ${i} ${i/_R2_001./_2.}; done
