%Booz-E Customer Simulation

%Parameters
m_dot_p = 700/60; %Pump flow rate, in ml/s
c_n = 160;  %Customers to Serve
u_u = c_n/4; %Usage Unit

%Starting volumes
vols(1).drink = ingredients(1).id;
vols(2).drink = ingredients(1).id;
vols(3).drink = ingredients(5).id;
vols(4).drink = ingredients(5).id;
vols(5).drink = ingredients(6).id;
vols(6).drink = ingredients(9).id;
vols(7).drink = ingredients(2).id;
vols(8).drink = ingredients(3).id;
vols(9).drink = ingredients(4).id;
vols(10).drink = ingredients(6).id;
vols(11).drink = ingredients(7).id;
vols(12).drink = ingredients(8).id;

vols(1).volume = zeros(1, u_u);
vols(2).volume = zeros(1, u_u);
vols(3).volume = zeros(1, u_u);
vols(4).volume = zeros(1, u_u);
vols(5).volume = zeros(1, u_u);
vols(6).volume = zeros(1, u_u);
vols(7).volume = zeros(1, u_u);
vols(8).volume = zeros(1, u_u);
vols(9).volume = zeros(1, u_u);
vols(10).volume = zeros(1, u_u);
vols(11).volume = zeros(1, u_u);
vols(12).volume = zeros(1, u_u);

vols(1).volume(1) = 2000;
vols(2).volume(1) = 2000;
vols(3).volume(1) = 2000;
vols(4).volume(1) = 2000;
vols(5).volume(1) = 2000;
vols(6).volume(1) = 2000;
vols(7).volume(1) = 1000;
vols(8).volume(1) = 1000;
vols(9).volume(1) = 1000;
vols(10).volume(1) = 1000;
vols(11).volume(1) = 1000;
vols(12).volume(1) = 1000;

%Customer Picking


