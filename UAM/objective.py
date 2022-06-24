def objective(W_w,MTOW,aero_eff)
    W_Aw=43957;
    W_f= MTOW-W_w-W_Aw;
    %ct=1.8639e-4
    %v=245;
    %R=5000000;
    %W_f=(1-0.938*exp(-ct*R/(v*aero_eff)))*MTOW;
    return P
