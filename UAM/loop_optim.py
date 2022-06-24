def loop_optim(x) 
A_ur(1)=x(1);
A_ur(2)=x(2);
A_ur(3)=x(3);
A_ur(4)=x(4);
A_ur(5)=x(5);
A_ur(6)=x(6);
A_lr(1)=x(7);
A_lr(2)=x(8);
A_lr(3)=x(9);
A_lr(4)=x(10);
A_lr(5)=x(11);
A_lr(6)=x(12);
A_ut(1)=x(13);
A_ut(2)=x(14);
A_ut(3)=x(15);
A_ut(4)=x(16);
A_ut(5)=x(17);
A_ut(6)=x(18);
A_lt(1)=x(19);
A_lt(2)=x(20);
A_lt(3)=x(21);
A_lt(4)=x(22);
A_lt(5)=x(23);
A_lt(6)=x(24);
twist_k=x(25);
twist_t=x(26);
b=x(27);
c_r=x(28);
lambda=x(29);
sweep_in=x(30);
sweep_out=x(31);

    #Initial guess for output of discipline 3 & 4
    W_w_i = 10657;
    MTOW_i=73500;
    
    #call MDA coordinator
    error=1e-6;
   [MTOW,W_w,Y,L,M,aero_eff,counter, MTOW_c,W_w_c] = MDA(A_ur,A_lr,A_ut,A_lt,twist_k,twist_t,b,c_r,lambda,sweep_in,sweep_out,W_w_i,MTOW_i,error)
   
    f = assignment_objective(W_w,MTOW);

    global couplings;
    
    vararg = {MTOW,W_w,Y,L,M,aero_eff,counter, MTOW_c,W_w_c};
    couplings.MTOW = MTOW;
    couplings.W_w = W_w;
    couplings.Y = Y;
    couplings.L = L;
    couplings.M = M;
    couplings.aero_eff = aero_eff;
    
return f,vararg
