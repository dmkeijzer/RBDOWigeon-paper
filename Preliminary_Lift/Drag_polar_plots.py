import numpy as np
import matplotlib.pyplot as plt
from Preliminary_Lift.Drag import CD0, C_D, e_factor

C_L = np.linspace(-0.5, 1.5,151)
C_D0 = CD0(4 ,0.0045)

e_ref = 0.85
e_tandem = e_factor('tandem',0.2, 1, e_ref)
e_box = e_factor('box',0.2, 1, e_ref)
C_D_n8 = []
C_D_n9 = []
C_D_n10 = []
C_D_t6 = []
C_D_t7 = []
C_D_t8 = []
C_D_b6 = []
C_D_b7 = []
C_D_b8 = []

for i in C_L :
    C_D_n8.append(C_D(i, C_D0, 8, e_ref ))
    C_D_n9.append(C_D(i, C_D0, 9, e_ref))
    C_D_n10.append(C_D(i, C_D0, 10, e_ref))
    C_D_t6.append(C_D(i, C_D0, 6, e_tandem))
    C_D_t7.append(C_D(i, C_D0, 7, e_tandem))
    C_D_t8.append(C_D(i, C_D0, 8, e_tandem))
    C_D_b6.append(C_D(i, C_D0, 6, e_box))
    C_D_b7.append(C_D(i, C_D0, 7, e_box))
    C_D_b8.append(C_D(i, C_D0, 8, e_box))
fig , ax = plt.subplots(2,2)
ax[0,0].plot(C_D_n8, C_L, color = 'red', label = 'Wing A = 8')
ax[0,0].plot(C_D_n9, C_L, color = 'red', alpha = 0.7, label = 'Wing A = 9')
ax[0,0].plot(C_D_n10, C_L, color = 'red', alpha = 0.4, label = 'Wing A = 10')
ax[0,1].plot(C_D_t6, C_L, color = 'blue', label = 'Tandem A = 6')
ax[0,1].plot(C_D_t7, C_L, color = 'blue', alpha = 0.7,  label = 'Tandem A = 7')
ax[0,1].plot(C_D_t8, C_L, color = 'blue', alpha = 0.4, label = 'Tandem A = 8')
ax[1,0].plot(C_D_b6, C_L, color = 'green',  label = 'Box Wing A = 6')
ax[1,0].plot(C_D_b7, C_L, color = 'green', alpha = 0.7, label = 'Box Wing A = 7')
ax[1,0].plot(C_D_b8, C_L, color = 'green', alpha = 0.4, label = 'Box Wing A = 8')
ax[1,1].plot(C_D_n8, C_L, color = 'red', label = 'Wing A = 8')
ax[1,1].plot(C_D_t8, C_L, color = 'blue', alpha = 0.4, label = 'Tandem A = 8')
ax[1,1].plot(C_D_b8, C_L, color = 'green', alpha = 0.4, label = 'Box Wing A = 8')
ax[0,0].legend()
ax[0,1].legend()
ax[1,0].legend()
ax[1,1].legend()
plt.show()
