#!/bin/bash

cpu_num=`cat /proc/stat | grep cpu[0-9] -c`
cpu_array=()
total=0
for((i=0;i<${cpu_num};i++))
{
        cpu_array[$i]=`./cpu.sh $i`
        total=`expr ${total} + ${cpu_array[$i]}`
}
average=`awk 'BEGIN{printf "%.2f",('$total'/'$cpu_num')}'`
echo $average
