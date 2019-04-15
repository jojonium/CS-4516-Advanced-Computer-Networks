#!/bin/bash

# This script calls the Python script `classifyFlows.py' on all pcap files in
# the input directory

# Usage:
#   ./classify.sh dir

dir="$1"

for f in "$dir"/*.pcap
do
    python3 classifyFlows.py $f
done
