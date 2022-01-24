function [x_tune, y_tune, s_tune] = get_all_tunes
% captures the current tune on all MBF systems.
% if the value is NaN the code will try again for up to 20 tries.
%
% Example: [x_tune, y_tune, s_tune] = get_all_tunes

% The while loops are there as for low currents the tune value is not always good.
x_tune.tune = NaN;
count_x = 0;
while isnan(x_tune.tune)
    x_tune.tune = lcaGet('SR23C-DI-TMBF-01:X:TUNE:CENTRE:TUNE');
    x_tune.lower_sideband = lcaGet('SR23C-DI-TMBF-01:X:TUNE:LEFT:TUNE');
    x_tune.upper_sideband = lcaGet('SR23C-DI-TMBF-01:X:TUNE:RIGHT:TUNE');
    count_x = count_x + 1;
    if count_x > 20
        disp('Unable to get X axis tune value')
        break
    end %if
    if isnan(x_tune.tune)
        pause(0.3)
    end %if
end %while
y_tune.tune = NaN;
count_y = 0;
while isnan(y_tune.tune)
    y_tune.tune = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:CENTRE:TUNE');
    y_tune.lower_sideband = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:LEFT:TUNE');
    y_tune.upper_sideband = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:RIGHT:TUNE');
    count_y = count_y + 1;
    if count_y > 20
        disp('Unable to get Y axis tune value')
        break
    end %if
    if isnan(y_tune.tune)
        pause(0.3)
    end %if
end %while
s_tune.tune = NaN;
count_s = 0;
while isnan(s_tune.tune)
    s_tune.tune = lcaGet('SR23C-DI-LMBF-01:IQ:TUNE:TUNE');
    try
    s_tune.lower_sideband = lcaGet('SR23C-DI-LMBF-01:IQ:LEFT:TUNE');
    catch
        s_tune.lower_sideband = NaN;
    end %try
    try
    s_tune.upper_sideband = lcaGet('SR23C-DI-LMBF-01:IQ:RIGHT:TUNE');
    catch
        s_tune.upper_sideband = NaN;
    end %try
    count_s = count_s + 1;
    if count_s > 20
        disp('Unable to get S axis tune value')
        break
    end %if
    if isnan(s_tune.tune)
        pause(0.3)
    end %if
end %while