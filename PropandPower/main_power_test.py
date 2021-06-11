import Final_optimization.constants_final as const
import battery as bat

sp_en_den = const.sp_en_den
vol_en_den = const.vol_en_den
bat_cost = const.bat_cost
DoD = const.DoD
P_den = const.P_den
EOL_C = const.EOL_C

energy = 1000
P_max = 500
safety = 1.2

bat = bat.Battery(sp_en_den, vol_en_den, energy, bat_cost, DoD, P_den, P_max, safety, EOL_C)

# # Comment out below just in case Javier gets aggressive
# print("mass", bat.mass())
# print()
# print("volume", bat.volume())
# print()
# print("cost", bat.price())
#
#
