import matplotlib.pyplot as plt
import numpy as np
from random import sample

data = np.random.randint(0, 10, 100)


counts, bins = np.histogram(data)
counts = counts * 0.79

print(counts)
plt.hist(bins[:-1], bins, weights=counts, rwidth=0.85)
plt.show()






# y = [1, 4, 9, 16, 25,36,49, 64]
# x1 = [1, 16, 30, 42,55, 68, 77,88]
# x2 = [1,6,12,18,28, 40, 52, 65]
# fig = plt.figure()
# ax = fig.add_axes([0.1, 0.15, 0.85, 0.8]) # [left, bottom, width, height] So the units of this is %, the sum of left + width can never be higher than 1 
# l1 = ax.plot(x1,y,'ys-') # solid line with yellow colour and square marker
# l2 = ax.plot(x2,y,'go--') # dash line with green colour and circle marker
# ax.legend(labels = ('tv', 'Smartphone'), loc = 'lower right') # legend placed at lower right
# ax.set_title("Advertisement effect on sales")
# ax.set_xlabel('medium')
# ax.set_ylabel('sales')
