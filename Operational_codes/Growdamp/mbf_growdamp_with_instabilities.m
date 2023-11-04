function mbf_growdamp_with_instabilities
% Runs the x and y growdamp measurements
% Does not use the blue buttons


fir_gain_x = lcaGet('SR23C-DI-TMBF-01:X:FIR:GAIN_S');
fir_gain_y = lcaGet('SR23C-DI-TMBF-01:Y:FIR:GAIN_S');

% Get the tunes
tunes = get_all_tunes;

try
    lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', '0dB')
    [~] = growdamp_all('x',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', fir_gain_x)
catch
    disp('Problem with Growdamp in X axis')
end %try
try
    lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', '0dB')
    [~] = growdamp_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', fir_gain_y)
catch
    disp('Problem with Growdamp in Y axis')
end %try

reestablish_tune_measurement('x')
reestablish_tune_measurement('y')
