function [fit_curve,gof2] = tune_fit(tune_scale, tune_trace)


% a = width
% b = centre
% c= height scaling
% Lorentz fix with the center locked at the max value.
[start_height, ind] = max(tune_trace);
start_centre = tune_scale(ind);
start_width = 1E-4;
fo = fitoptions('Method','NonlinearLeastSquares',...
               'Lower',[0, 0],...
               'Upper',[Inf, Inf],...
               'StartPoint',[start_width, start_height/2*pi*start_width]);
ft = fittype('c .* ((1 ./ pi) * 0.5 .* a / ((x - n)^2 + (0.5 .* a).^2))','problem', 'n', 'options', fo);
[fit_curve,gof2] = fit(tune_scale, tune_trace, ft, 'problem', start_centre);
% figure
% plot(tune_scale, tune_trace)
% hold on
% plot(fit_curve, 'm')
