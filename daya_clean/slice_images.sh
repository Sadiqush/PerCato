#!/bin/bash

###################################################
## Sepereate val and train images for OCR project
###################################################

for item in $(cat $1); do
    mv -v $item $2
done
