#!/usr/bin/python
import commands


def get_cni_type():
    cni_type = ""
    ret,out = commands.getstatusoutput("kubectl get pods --all-namespaces | grep flannel")
    print "ret = " + str(ret)
    if ret == 0:
       print "inside_if"
       cni_type = "Flannel"
    ret,out = commands.getstatusoutput("kubectl get pods --all-namespaces | grep -i calico")
    print "ret = " + str(ret)
    if ret == 0:
       print "inside if"
       cni_type = "Calico"
    return cni_type

print get_cni_type()
