import numpy as np
import matplotlib.pyplot as plt

# N = 10
# C_array = np.linspace(1,6000000,40)
# print(C_array)
#
# def C_sum(C_in, C_add):
#     return 1 / (1/C_in + 1/C_add)
#
# C_Sum = C_array[0]
# sum_list = list()
# i_list = list()
# counter = 0
# for i in C_array:
#     counter += 1
#     C_Sum = C_sum(C_Sum,i)
#     sum_list.append(C_Sum)
#     i_list.append(counter)
#
# print(sum_list)
#
# plt.plot(i_list,sum_list)
# plt.show()



Nc = 100

DoD_list = list()
count_list = list()
count = 0
for i in range(1, Nc):
    count += 1
    DoD = 175 - 30 * np.log10(i)
    count_list.append(count)
    DoD_list.append(DoD)

plt.plot(count_list,DoD_list)
plt.show()

print(DoD_list)
