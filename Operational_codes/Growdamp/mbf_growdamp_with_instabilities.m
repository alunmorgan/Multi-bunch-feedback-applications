function mbf_growdamp_with_instabilities
% Runs the x and y growdamp measurements
% Does not use the blue buttons

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

fir_gain_x = get_variable([mbf_names.x, mbf_vars.FIR.Base, mbf_vars.FIR.gain]);
fir_gain_y = get_variable([mbf_names.y, mbf_vars.FIR.Base, mbf_vars.FIR.gain]);

% Get the tunes
tunes = get_all_tunes;

try
    set_variable([mbf_names.x, mbf_vars.FIR.Base, mbf_vars.FIR.gain], '0dB')
    [~] = growdamp_all('x',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    set_variable([mbf_names.x, mbf_vars.FIR.Base, mbf_vars.FIR.gain], fir_gain_x)
catch
    disp('Problem with Growdamp in X axis')
end %try
try
    set_variable([mbf_names.y, mbf_vars.FIR.Base, mbf_vars.FIR.gain], '0dB')
    [~] = growdamp_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    set_variable([mbf_names.y, mbf_vars.FIR.Base, mbf_vars.FIR.gain], fir_gain_y)
catch
    disp('Problem with Growdamp in Y axis')
end %try

reestablish_tune_measurement('x')
reestablish_tune_measurement('y')
