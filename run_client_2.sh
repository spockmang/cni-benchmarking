#!/bin/bash

declare -a size_array=(64k 128k 256k 512k 1m)
declare -a array_64k=()
declare -a array_128k=()
declare -a array_256k=()
declare -a array_512k=()
declare -a array_1m=()

calculate_avg()
{
   arr=("$@")
   sum=0
   for i in "${arr[@]}"
   do
     sum=$(echo $sum + $i | bc -l);
   done
   average=$(echo $sum / ${#arr[@]} | bc -l)
   echo "$average"
}


if [ "$1" != "" ]; then
   count=$1
else
   count=1
fi
echo "Start script to run iperf client pods"

server_ip="$(kubectl get pods -o wide | grep iperf-dev-s-2 |awk {'print $6'})"

for i in $(seq 1 $count)
do 
   for size in "${size_array[@]}"
   do
     #if kubectl get pods | grep iperf-client$ > /dev/null 2>&1 ; then
     #   kubectl delete -f iperf_client.yaml > /dev/null 2>&1
     #   echo "Deleted client pod"
     #fi
     #sed -i 's/args.*/args: \["-c",'$server_ip',"-l","'$size'"\]/' iperf_client_"$size".yaml
     sed -i 's/args.*/args: \["-c",'$server_ip',"-l","'$size'"\]/' iperf_client_"$size"_2.yaml
     echo "Creating client pod with packet length $size"
     kubectl apply -f iperf_client"_$size"_2.yaml >  /dev/null 2>&1
     sleep 10
     kubectl logs -f iperf-client-2
     bandwidth=$(kubectl logs -f iperf-client-2 | grep receiver | awk {'print $7'})
     if [ "$size" == "64k" ]; then
	array_64k+=("$bandwidth")
     elif [ "$size" == "128k" ]; then
        array_128k+=("$bandwidth")
     elif [ "$size" == "256k" ]; then
        array_256k+=("$bandwidth")
     elif [ "$size" == "512k" ]; then
        array_512k+=("$bandwidth")
     else
	array_1m+=("$bandwidth")
     fi
     echo "Delete client pod with packet length $size"
     kubectl delete -f iperf_client"_$size"_2.yaml > /dev/null 2>&1
     echo "-------------------------------------------------------------------------------------------------------------------"
   done   
done
echo "-------------------------------------------------------------------------------------------------------------------"
echo "iperf client results for 64k  : ${array_64k[@]}"
echo "iperf client results for 128k : ${array_128k[@]}"
echo "iperf client results for 256k : ${array_256k[@]}"
echo "iperf client results for 512k : ${array_512k[@]}"
echo "iperf client results for 1m   : ${array_1m[@]}"
if [ $count -gt 1 ]; then
   echo -n "Average bandwidth for 64k packet size = "
   calculate_avg "${array_64k[@]}"
   echo ""
   echo -n "Average bandwidth for 128k packet size = "
   calculate_avg "${array_128k[@]}"
   echo ""
   echo -n "Average bandwidth for 256k packet size = "
   calculate_avg "${array_256k[@]}"
   echo ""
   echo -n "Average bandwidth for 512k packet size = "
   calculate_avg "${array_512k[@]}"
   echo ""
   echo -n "Average bandwidth for 1m packet size = "
   calculate_avg "${array_1m[@]}"
   echo ""
fi
echo "-------------------------------------------------------------------------------------------------------------------"
echo ""
