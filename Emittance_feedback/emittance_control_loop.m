function emittance_control_loop(selected_axis, emittance_target)
% This changes the gain of the excitation for the selected axis in order to
% reach the requested emittance target.
% This presumes that mbf_emittance_setup has been run beforehand.
%   Args:
%       selected_axis(str): 'X' or 'Y'
%       emittance_target(float): nm rad for horizontal, pm rad for vertical. 
%
% Example: emittance_control_loop('Y', 9)

if strcmp(selected_axis, 'X')
    em_axis = 'H';
elseif strcmp(selected_axis, 'Y')
    em_axis = 'V';
else
    error('Invalid axis selected for emittance control loop')
end %if
slew_rate_limit = 0.2;
low_limit = -78;
while true
    % Check the status of the frequency locked loop.
    error_user = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':PLL:CTRL:STOP:STOP']);
    error_detector_overflow = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':PLL:CTRL:STOP:DET_OVF']);
    error_offset = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':PLL:CTRL:STOP:OFFSET_OVF']);
    error_magnitude = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':PLL:CTRL:STOP:MAG_ERROR']);
    if ~strcmp(error_detector_overflow{1}, 'Ok') ||...
            ~strcmp(error_offset{1}, 'Ok') ||...
            ~strcmp(error_magnitude{1}, 'Ok') ||...
            ~strcmp(error_user{1}, 'Ok')
        error([selected_axis,' frequency locked loop has stopped']);
    end %if
    
    tune = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':TUNE:CENTRE:TUNE']);
    emit=lcaGet(['SR-DI-EMIT-01:',em_axis,'EMIT_MEAN']);
    power=lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_DB_S']);
    % Too much excitation causes the tune value to be lost. The solution is
    % to reduce the exciation value
    if isnan(tune)
        lcaPut(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_DB_S'],power-0.2);
    else
        emit_error=log10(emit / emittance_target);
        if abs(emit_error) > slew_rate_limit
            emit_error = sign(emit_error) * slew_rate_limit;
        end %if
        if power - emit_error > low_limit
            lcaPut(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_DB_S'], power - emit_error);
        end %if
    end %if
    pause(0.5)
end %while
end %function
