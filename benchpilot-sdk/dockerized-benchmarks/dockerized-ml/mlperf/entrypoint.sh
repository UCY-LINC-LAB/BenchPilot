#!/bin/bash

echo "Clearing caches."
sync && echo 3 | tee /host_proc/sys/vm/drop_caches


cd /root

common_opt=""

start_fmt=$(date +%Y-%m-%d\ %r)
echo "STARTING RUN AT $start_fmt"

cd /benchmark
if [[ $BENCHMARK_MODE == "STREAMING" ]]; then
  python python/main.py $opts
else
  python python/main_old.py $opts
fi

end_fmt=$(date +%Y-%m-%d\ %r)
echo "ENDING RUN AT $end_fmt"
