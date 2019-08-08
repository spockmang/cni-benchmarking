#!/usr/bin/python
import sys
import time
import getopt
import commands
import matplotlib.pyplot as plt
import numpy as np

pkt_size_list = ["64k", "128k", "256k", "512k", "1m"]
list_64k = []
list_128k = []
list_256k = []
list_512k = []
list_1m = []

def run_server():
    ret,out = commands.getstatusoutput("kubectl apply -f iperf-dev-s-1.yaml")
    if ret == 0:
       print "Server pod created successfully !"
    else:
       print "Server pod creation failed !"
       exit(2)

def delete_server():
    ret,out = commands.getstatusoutput("kubectl delete -f iperf-dev-s-1.yaml")
    if ret == 0:
       print "Server pod deleted successfully !"
    else:
       print "Server pod deletion failed !"

def run_client(pkt_len):
    ret,out = commands.getstatusoutput("kubectl apply -f iperf_client_" + pkt_len + ".yaml > /dev/null 2>&1")
    if ret == 0 :
       print "Client pod created successfully !"
    else:
       print "Client pod creation failed !"
       exit(2)
    time.sleep(10)
    client_log_out = commands.getoutput("kubectl logs -f iperf-client")
    print client_log_out
    bandwidth = commands.getoutput("kubectl logs -f iperf-client | grep receiver | awk {'print $7'}")
    ret,out = commands.getstatusoutput("kubectl delete -f iperf_client_" + pkt_len + ".yaml > /dev/null 2>&1")
    if ret == 0 :
        print "Client pod deleted successfully"
    return bandwidth

def get_cni_type():
    cni_type = ""
    ret,out = commands.getstatusoutput("kubectl get pods --all-namespaces | grep -i flannel")
    if ret == 0:
       cni_type = "Flannel"
    ret,out = commands.getstatusoutput("kubectl get pods --all-namespaces | grep -i calico")
    if ret == 0:
       cni_type = "Calico"
    return cni_type

n_iter = 0

try:
    opts, args = getopt.getopt(sys.argv[1:],"hs:c:l:i:")
except getopt.GetoptError:
    print './kube_iperf.py -s <number_of_servers> -o <number_of_clients> -l <buffer_length_in_Kbytes> -i <iterations : default=1>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
       print './kube_iperf.py -s <number_of_servers> -o <number_of_clients> -l <buffer_length_in_Kbytes> -i <iterations : default=1>'
       sys.exit()
    elif opt in ("-s"):
       n_servers = int(arg)
    elif opt in ("-c"):
       n_clients = arg
    elif opt in ("-l"):
       pkt_len = arg
    elif opt in ("-i"):
       n_iter = int(arg)
if n_iter == 0:
   n_iter = 1

if pkt_len == "all":
    pkt_sizes = pkt_size_list
else:
    pkt_sizes =  pkt_len.split(",")

for size in pkt_sizes:
    if size not in pkt_size_list:
       print "Please enter suitable packet sizes as per below list: "
       print pkt_size_list

run_server()
time.sleep(10)
server_name = commands.getoutput("kubectl get pods | grep iperf-dev | awk {'print $1'}")
print "server_name = " + server_name
server_ip = commands.getoutput("kubectl get pods -o wide | grep '" + server_name + "' | awk {'print $6'}")
print "server ip = " + server_ip
iperf_dict = {}

for size in pkt_sizes:
    iperf_dict[size] = []
    out = commands.getoutput("sed -i 's/args.*/args: \[\"-c\",\"" + server_ip  + "\",\"-l\",\"" + size + "\"\]/' iperf_client_" + size + ".yaml")
    print ""
    print "---------------------------------------------------------------------------------"
    print "                       Traffic stats for Buffer size = " + size + " bytes"
    print "---------------------------------------------------------------------------------"

    for i in range(n_iter):
        iperf_dict[size].append(run_client(size))

delete_server()
time.sleep(10)

print iperf_dict

print "Plot for data"

plt.figure(1)

pkt_size_list = ('64k', '128k', '256k', '512k', '1m')
y_pos = np.arange(len(pkt_size_list))
performance = []
for key in pkt_size_list:
    if key in iperf_dict.keys():
       performance.append(float(iperf_dict[key][0]))
print performance
plt.bar(y_pos, performance, align='center', width=0.5, alpha=0.5)
plt.xticks(y_pos, pkt_size_list)
plt.ylabel('Throughput in GBits/s')
plt.xlabel('Application buffer size in Kbytes')
plt.title('K8S CNI benchmarking for ' + get_cni_type() + ' CNI plugin')
plt.show()

