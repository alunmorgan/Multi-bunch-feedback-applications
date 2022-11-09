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
slew_rate_limit = 0.2; % in pm rad for Y and nm rad for X
fraction_to_apply = 0.075;
low_power_limit = 0.00098; %~-60dB
high_power_limit = 0.0625; %~-20dB
start_power_level = 0.004; %~-46dB
output_lim = 1;
lcaPut(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_SCALAR_S'], start_power_level);
emit_old = lcaGet(['SR-DI-EMIT-01:',em_axis,'EMIT']);

while true
    % The ~=0 accounts for the -1 when topup is turned off as well as the usual countdown when it is on.
    if lcaGet('SR-CS-FILL-01:COUNTDOWN') ~= 0  && lcaGet('SR-DI-DCCT-01:SIGNAL') > 10 && strcmp(lcaGet('SR-DI-EMIT-01:STATUS'), 'Successful')
        if output_lim >100
            fprintf('.\n')
            output_lim = 1;
        else
            fprintf('.')
            output_lim = output_lim +1;
        end %if
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
        if ~strcmp(lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:ENABLE_S']), 'On')
            error('Excitation manually terminated')
        end %if

        tune = lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':TUNE:CENTRE:TUNE']);
        emit = lcaGet(['SR-DI-EMIT-01:',em_axis,'EMIT']);
        emit_mean = lcaGet(['SR-DI-EMIT-01:',em_axis,'EMIT_MEAN']);
        power=lcaGet(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_SCALAR_S']);

        if isnan(tune)
            % pause if tune value is invalid.
            pause(1)
        else
            %             emit_error= 1E-3 * log10(emit / emittance_target);
            %             if abs(emit_error) > slew_rate_limit
            %                 emit_error = sign(emit_error) * slew_rate_limit;
            %             end %if
            %             if power - emit_error > low_power_limit && power - emit_error < high_power_limit
            %                 lcaPut(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_SCALAR_S'], power - emit_error);
            %             end %if
            if abs(emit - emit_mean) <0.01
                emit = emit_mean;
            end %if
            emit_error = emittance_target - emit;
            if abs(emit_error) > slew_rate_limit
                emit_error = sign(emit_error) * slew_rate_limit;
            end %if
            power_error = sign(emit_error) * 1E-3 * log10(abs(emit_error)) * fraction_to_apply;
            if power - power_error > low_power_limit && power - power_error < high_power_limit
                lcaPut(['SR23C-DI-TMBF-01:',selected_axis,':NCO2:GAIN_SCALAR_S'], power - power_error);
            end %if
            emit_old = emit;
        end %if
        pause(0.5)
    else
        % pause if top up is running or the current is below 10mA or the
        % beam is injecting.
        pause(1)
        if output_lim >100
            fprintf('*\n')
            output_lim = 1;
        else
            fprintf('*')
            output_lim = output_lim +1;
        end %if
    end %while
end %function
