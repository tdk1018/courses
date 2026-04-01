#!/bin/bash

grep "GET" log.txt | sed 's/Apr/May/'
#didn't get to a useful awk command