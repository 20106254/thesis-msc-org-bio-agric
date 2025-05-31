#!/bin/bash
DATA_SET="../datasets/site-68-2025/*.csv"

grep -v '^RELEVE_ID' $DATA_SET | cut -d',' -f1 | sort -n | uniq | wc -l
