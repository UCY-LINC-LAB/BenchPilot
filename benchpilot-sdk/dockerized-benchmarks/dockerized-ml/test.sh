#!/bin/bash

# Define the directories
mlperf_dir="mlperf"
mlperf_tf_dir="mlperf_tf"

# Loop through files in mlperf directory
for file in "$mlperf_dir"/*; do
    # Get the filename
    filename=$(basename "$file")
    # Compare corresponding files in mlperf and mlperf_tf directories
    diff "$mlperf_dir/$filename" "$mlperf_tf_dir/$filename"
done
