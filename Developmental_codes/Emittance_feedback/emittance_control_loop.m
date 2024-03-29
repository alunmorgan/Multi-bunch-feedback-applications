function emittance_control_loop(selected_axis, emittance_target, varargin)
% This changes the gain of the excitation for the selected axis in order to
% reach the requested emittance target.
% This presumes that mbf_emittance_setup has been run beforehand.
%   Args:
%       selected_axis(str): 'X' or 'Y'
%       emittance_target(float): nm rad for horizontal, pm rad for vertical.
%
% Example: emittance_control_loop('Y', 9)

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;
selected_axis = lower(selected_axis);
if ~strcmp(selected_axis, 'x') && ~strcmp(selected_axis, 'y')
    error('EmittanceControl:Main','Invalid axis selected for emittance control loop')
end %if

% The time needed to get new data from the underlying hardware.
hardware_update_time = 0.5; %sec

default_slew_rate_limit = 0.2; % in pm rad for Y and nm rad for X
default_fraction_to_apply = 0.075;
default_low_power_limit = 0.00098; %~-60dB
default_high_power_limit = 0.0625; %~-20dB
default_start_power_level = 0.004; %~-46dB

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
addRequired(p, 'selected_axis');
addRequired(p, 'emittance_target');
addParameter(p, 'slew_rate_limit', default_slew_rate_limit, valid_number);
addParameter(p, 'fraction_to_apply', default_fraction_to_apply, valid_number);
addParameter(p, 'low_power_limit', default_low_power_limit, valid_number);
addParameter(p, 'high_power_limit', default_high_power_limit, valid_number);
addParameter(p, 'start_power_level', default_start_power_level, valid_number);
parse(p, selected_axis, emittance_target, varargin{:});

mbf_device = mbf_names.(p.Results.selected_axis);

% start the NCO excitation.
set_variable([mbf_device, mbf_vars.NCO2.gain_scalar], p.Results.start_power_level);

output_lim = 1;
while true
    % The loop holds the existing settings if topup is on
    % The ~=0 accounts for the -1 when topup is turned off as well as the
    % usual countdown when it is on.
    % The loop holds the existing settings if the current drops below 10mA
    % The loop holds the existing settings if it is unable to get an up to date
    % emittance reading.
    if get_variable(pv_names.topup.countdown) ~= 0  &&...
            get_variable(pv_names.current) > 10 &&...
            strcmp(get_variable(pv_names.emittance.status), 'Successful')
        %% heartbeat code
        if output_lim >100
            fprintf('.\n')
            output_lim = 1;
        else
            fprintf('.')
            output_lim = output_lim +1;
        end %if

        %% Check the status of the frequency locked loop.
        error_user = get_variable([mbf_device, mbf_vars.pll.stop_reasons.stop]);
        error_detector_overflow = get_variable([mbf_device, mbf_vars.pll.stop_reasons.detector_overflow]);
        error_offset = get_variable([mbf_device, mbf_vars.pll.stop_reasons.offset_overflow]);
        error_magnitude = get_variable([mbf_device, mbf_vars.pll.stop_reasons.magnitude_error]);
        if ~strcmp(error_detector_overflow{1}, 'Ok') ||...
                ~strcmp(error_offset{1}, 'Ok') ||...
                ~strcmp(error_magnitude{1}, 'Ok') ||...
                ~strcmp(error_user{1}, 'Ok')
            error('EmittanceControl:Main',[mbf_device,' frequency locked loop has stopped']);
        end %if
        if ~strcmp(get_variable([mbf_device, mbf_vars.NCO2.enable]), 'On')
            error('EmittanceControl:Main',[mbf_device, 'Excitation manually terminated'])
        end %if

        %% Get current settings
        % This pause is to allow the hardware to update so we know we have fresh
        % data.
        pause(hardware_update_time)
        tune = get_variable([mbf_device, mbf_vars.tune.centre]);
        emit = get_variable(pv_names.emittance.(selected_axis));
        emit_mean = get_variable(pv_names.emittance.(selected_axis).mean);
        power_input = get_variable([mbf_device, mbf_vars.NCO2.gain_scalar]);
        if isnan(tune)
            % pause if tune value is invalid.
            fprintf('\nTune value is invalid.')
            continue
        end %if

        %% Main feedback function
        % if the difference between the instantaneous emittance value and the
        % mean value is small then use the mean value. This allows faster
        % initial following using the instantainoues values but more stable
        % steady state using the mean values.
        if abs(emit - emit_mean) <0.01
            emit = emit_mean;
        end %if
        % Get the error term
        emit_error = p.Results.emittance_target - emit;
        % Apply slew rate limit.
        if abs(emit_error) > p.Results.slew_rate_limit
            emit_error = sign(emit_error) * p.Results.slew_rate_limit;
        end %if
        % error scaling from emittance to output power.
        power_error = sign(emit_error) * 1E-3 * log10(abs(emit_error));
        % fraction to apply
        power_error = power_error * p.Results.fraction_to_apply;
        % power monitor
        power_new = power_input - power_error;
        % Apply power limits and apply
        if power_new > p.Results.low_power_limit && power_new < p.Results.high_power_limit
            set_variable([mbf_device, mbf_vars.NCO2.gain_scalar], power_new);
        end %if
    else
        % The machine is not in a state for the loop to run so wait and try
        % later.
        pause(1)
        %% heartbeat code
        if output_lim >100
            fprintf('*\n')
            output_lim = 1;
        else
            fprintf('*')
            output_lim = output_lim +1;
        end %if

    end %if
end %while
