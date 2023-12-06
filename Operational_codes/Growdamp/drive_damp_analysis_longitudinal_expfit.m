function name=drive_damp_analysis_longitudinal_expfit(name)
% Exponential fit function for drive-damp measurements
% Last edit: 28.09.2023 (G.Rehm, A.Matveenko)

aa = reshape(abs(name.iq), name.dampcapture, 400);
time = (1:name.dampcapture) * name.dampdwell / 1.249e6; % s

% fit parameters are amplitude - p(1), damping - p(2), and "zero"-point offset - p(3)
f = @(p, time) (p(1) .* exp(-p(2) .* time) + p(3));

% further "optimisation" of opts can make the fit faster...
opts = optimset('MaxFunEvals', 50000, 'MaxIter', 10000);

for m = 1:400
    OLS = @(p) sum((f(p, time) - aa(:,m).').^2); % sum of squares of model-measurement
    res0 = [aa(1,m);150;aa(300,m)]; % guess-values 
    p(m,1:3) = fminsearch(OLS,res0,opts);
    %[p(m,1:2),stemp]=polyfit(t,log(aa(:,m)),1);
    % stemp is a structure, but we only want to keep the regression coefficient
    % so let's extract that and save in s
    %s(m)=stemp.normr;
    %p(m,1:3)=B(:);
end
name.p = p;
%name.s = s;
name.aa = aa;
