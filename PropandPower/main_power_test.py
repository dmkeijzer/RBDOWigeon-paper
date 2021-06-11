import Final_optimization.constants_final as const
import battery as bat

sp_en_den = const.sp_en_den
vol_en_den = const.vol_en_den
bat_cost = const.bat_cost
DoD = const.DoD
P_den = const.P_den

energy = 1
P_max = 1

bat = bat.Battery(sp_en_den, vol_en_den, energy, bat_cost, DoD, P_den, P_max)

print(bat.mass())

