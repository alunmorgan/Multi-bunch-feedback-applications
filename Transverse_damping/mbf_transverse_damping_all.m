function [tdx, tdy] = mbf_transverse_damping_all(mbf_mode)
% Top level function to run all growdamp measurements of each plane
% sequentially.
% Takes in a mode value (int)

mbf_tools

% Get the tunes
 tunes = get_all_tunes('xys');
x_tune = tunes.x_tune;
y_tune = tunes.y_tunes;

if isnan(x_tune.upper_sideband) || ...
    isnan(y_tune.upper_sideband) 
    disp('Could not get all tune values')
    return
end %if

mbf_growdamp_setup('x', x_tune.upper_sideband, 'single_mode', mbf_mode)
mbf_growdamp_setup('y', y_tune.upper_sideband, 'single_mode', mbf_mode)

tdx = mbf_transverse_damping_capture('x');
tdy = mbf_transverse_damping_capture('y');
 
% Programatically press the Feedback and tune button on each system
% and set the feedback gain to 0dB.
setup_operational_mode("x", "Feedback")
lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', '0dB')
setup_operational_mode("y", "Feedback")
lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', '0dB')

