function emittance_control_loop_dd_pid_v1(selected_axis, emittance_target, varargin)
% This changes the gain of the excitation for the selected axis in order to
% reach the requested emittance target.
% This presumes that mbf_emittance_setup has been run beforehand.
%   Args:
%       selected_axis(str): 'X' or 'Y'
%       emittance_target(float): nm rad for horizontal, pm rad for vertical.
%
% Example: emittance_control_loop('Y', 9)
% Example with DD-PID: emittance_control_loop('Y', 9, 'use_data_driven', true, 'database_file', 'emittance_dd_database.mat')

[~, ~, pv_names] = mbf_system_config;
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

% Data-Driven PID Defaults
default_use_data_driven = true;
default_database_file = char(strcat('emittance_dd_database_',selected_axis,'.mat'));
default_k_neighbors = 5;
default_pid_gains = [1e-4, 5e-5, 2e-5]; % [Kp, Ki, Kd] default baseline

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
valid_bool = @(x) islogical(x) || (isnumeric(x) && (x==0 || x==1));
valid_str_or_struct = @(x) ischar(x) || isstring(x) || isstruct(x);

addRequired(p, 'selected_axis');
addRequired(p, 'emittance_target');
addParameter(p, 'slew_rate_limit', default_slew_rate_limit, valid_number);
addParameter(p, 'fraction_to_apply', default_fraction_to_apply, valid_number);
addParameter(p, 'low_power_limit', default_low_power_limit, valid_number);
addParameter(p, 'high_power_limit', default_high_power_limit, valid_number);
addParameter(p, 'start_power_level', default_start_power_level, valid_number);

% Data-Driven PID Parameters
addParameter(p, 'use_data_driven', default_use_data_driven, valid_bool);
addParameter(p, 'database_file', default_database_file, valid_str_or_struct);
addParameter(p, 'k_neighbors', default_k_neighbors, valid_number);
addParameter(p, 'fixed_pid_gains', default_pid_gains, valid_number);

parse(p, selected_axis, emittance_target, varargin{:});

mbf_device = mbf_names.(p.Results.selected_axis);

% Load Data-Driven Database if enabled
use_dd = p.Results.use_data_driven;
if use_dd
    if isstruct(p.Results.database_file)
        dd_db = p.Results.database_file;
    elseif isfile(p.Results.database_file)
        dd_db = load(p.Results.database_file);
        fprintf('Loaded Data-Driven PID database: %s\n', p.Results.database_file);
    else
        warning('EmittanceControl:DD_PID', 'Database file %s not found. Falling back to baseline PID.', p.Results.database_file);
        use_dd = false;
    end
end

% Initialize historical state variables for PID & Query vector
emit_prev  = NaN;
emit_prev2 = NaN;
power_prev = p.Results.start_power_level;

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
        emit = get_variable(pv_names.emittance.(selected_axis).val);
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

        % Initialize past history if first valid step
        if isnan(emit_prev)
            emit_prev = emit;
            emit_prev2 = emit;
        end

        % Get the error term
        emit_error = p.Results.emittance_target - emit;

        % Apply slew rate limit.
        if abs(emit_error) > p.Results.slew_rate_limit
            emit_error = sign(emit_error) * p.Results.slew_rate_limit;
        end %if

        if use_dd
            %% DATA-DRIVEN PID CONTROLLER (Step 1 & Step 2)
            % Form query vector: phi_query = [r(t+1), r(t), y(t), y(t-1), u(t-1)]
            phi_query = [p.Results.emittance_target, p.Results.emittance_target, emit, emit_prev, power_prev];
            
            % Step 1: Calculate L1 normalized distance to database items
            N_db = size(dd_db.DB_phi, 1);
            range_val = dd_db.phi_max - dd_db.phi_min;
            range_val(range_val < 1e-12) = 1.0;
            
            diff_norm = abs(dd_db.DB_phi - repmat(phi_query, N_db, 1)) ./ repmat(range_val, N_db, 1);
            d = sum(diff_norm, 2);
            
            % Find k-nearest neighbors
            [sorted_d, sorted_idx] = sort(d, 'ascend');
            k_eff = min(p.Results.k_neighbors, N_db);
            knn_idx = sorted_idx(1:k_eff);
            knn_dist = sorted_d(1:k_eff);
            
            % Step 2: Compute weights and interpolate adaptive PID gains
            if knn_dist(1) < 1e-10
                weights = zeros(k_eff, 1);
                weights(1) = 1.0;
            else
                inv_d = 1.0 ./ knn_dist;
                weights = inv_d / sum(inv_d);
            end
            
            K_t = sum(repmat(weights, 1, 3) .* dd_db.DB_K(knn_idx, :), 1);
            Kp = K_t(1); Ki = K_t(2); Kd = K_t(3);
            
            % Velocity PID increments
            dy  = emit - emit_prev;
            d2y = emit - 2 * emit_prev + emit_prev2;
            
            delta_power = Ki * emit_error - Kp * dy - Kd * d2y;
            power_new = power_input + delta_power;
        else
            %% ORIGINAL LOGARITHMIC CONTROL LAW (Fallback)
            % error scaling from emittance to output power.
            power_error = sign(emit_error) * 1E-3 * log10(abs(emit_error));
            % fraction to apply
            power_error = power_error * p.Results.fraction_to_apply;
            % power monitor
            power_new = power_input - power_error;
        end %if

        % Update historical state variables
        emit_prev2 = emit_prev;
        emit_prev  = emit;
        power_prev = power_input;

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