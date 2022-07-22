def MDA(b_up,b_down,cr_up,cr_down,sweep_up,sweep_down,W_w_c,MTOW_c,error)


    #Convergence loop

    error = 1e-3;


    #for initiation of loop condition:
    MTOW = 1e9;
    W_w=1e9;
    counter = 0;
    while ((abs(MTOW-MTOW_c)/MTOW > error ) & (abs(W_w-W_w_c)/W_w > error)):
        #loop counter
        if (counter > 0):
            MTOW_c = MTOW;
            W_w_c=W_w;

        aero_eff=aerodynamics(MTOW_c,b_up,b_down,cr_up, cr_down,sweep_up,sweep_down,W_w_c);
        [C_L, C_D]=loads(MTOW_c,b_up,b_down,cr_up, cr_down twist_k, twist_t,A_ut,A_ur,A_lt,A_lr,sweep_in,sweep_out);
        W_w=structures(A_ur,A_lr,A_ut,A_lt,b_up,b_down,cr_up,cr_down,sweep_in,sweep_out,W_w_c,MTOW_c,Y,L, M);
        MTOW=performance(W_w,aero_eff);
        counter = counter +1;    


    return [MTOW,W_w,C_L,C_D,aero_eff,counter, M_battery_c,W_w_c] 
