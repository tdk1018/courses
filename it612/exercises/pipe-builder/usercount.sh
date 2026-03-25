#!/bin/bash
set -e
cat "$1" | cut -d':' -f1 | sort | uniq | wc -l