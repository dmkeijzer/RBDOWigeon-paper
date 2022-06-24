import scipy as 

#Initial values:
A_ur=ones(1,6);
A_lr=ones(1,6);
A_ut=ones(1,6);
A_lt=ones(1,6);
twist_k=1;
twist_t=1;
b=1;
c_r=1;
lambda=1;
sweep_in=1;
sweep_out=1;

#bounds
airfb=0.7*ones(1,6);
lb = [airfb,airfb,airfb,airfb,-500,-500,0.73,0.58,0.67,0.8,0.8];
ub = [ones(1,6),ones(1,6),ones(1,6),ones(1,6),500,500,1.056,1.8,1.7,1.4,1.4];

x0 = [A_ur,A_lr,A_ut,A_lt,twist_k,twist_t,b,c_r,lambda,sweep_in,sweep_out];
    
% Options for the optimization
options.Display         = 'iter-detailed';
options.Algorithm       = 'sqp';
options.FunValCheck     = 'off';
options.DiffMinChange   = 1e-6;         % Minimum change while gradient searching
options.DiffMaxChange   = 5e-2;         % Maximum change while gradient searching
options.TolCon          = 1e-3;         % Maximum difference between two subsequent constraint vectors [c and ceq]
options.TolFun          = 1e-3;         % Maximum difference between two subsequent objective value
options.TolX            = 1e-3;         % Maximum difference between two subsequent design vectors

options.MaxIter         = 30;           % Maximum iterations
%options = optimset('PlotFcns',@optimplotfval);
tic;
[x,FVAL,EXITFLAG,OUTPUT] = fmincon(@(x) Optim_MDFGauss(x),x0,[],[],[],[],lb,ub,@(x) constraints(x),options);

