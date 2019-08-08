#!/usr/bin/python
import matplotlib.pyplot as plt

# plot with various axes scales
plt.figure(1)


# iperf 64k

x = ([2.01, 2.07, 2.00, 2.03, 2.09, 1.95, 2.09, 2.07, 1.91, 1.92])
plt.subplot(221)
plt.plot(x)
plt.axis([0,10,0,3])
plt.title('iperf 64k')
plt.grid(True)


# iperf 128k
x = ([2.01, 2.07, 2.00, 2.03, 2.09, 1.95, 2.09, 2.07, 1.91, 1.92])
plt.subplot(222)
plt.plot(x)
plt.axis([0,10,0,3])
plt.title('iperf 128k')
plt.grid(True)


plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

plt.show()
