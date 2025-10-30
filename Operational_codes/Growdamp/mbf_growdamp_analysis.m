function output_data = mbf_growdamp_analysis(exp_data, varargin)
% takes the data from mbf growdamp capture and fits it with a series of
% linear fits to get the damping times for each mode.
%
%   Args:
%       exp_data (structure): Contains the systems setup and the data
%                             captured.
%       active_override (int|NaN): Sets the number of turns to analyse.
%       passive_override (int|NaN): Sets the number of turns to analyse.
%       advanced_fitting (bool): switches between simple (0)
%                                and advanced fitting (1).
%       length_averaging(int): Determines the strength of the filtering out
%                              of high frequecies in the data.
%       debug(int): if 1 then outputs graphs of individual modes to allow
%                                    selection of appropriate overrides.
%       debug_modes(list of ints): the modes to output the debug graphs for.
%       keep_debug_graphs(bool): selects if the debug graphs are overwritten (0) or
%                                kept (1).
%
%   Returns:
%       output_data (struct): data is structured as [stage].[mesurement]
%                               measurements are: damping time, offset, 
%                               error relative to fit, frequency shift.
%                               all measurements are a vector the length of the
%                               number of modes.
%
% Example: output_data = tmbf_growdamp_analysis(exp_data)

harmonic_number = length(exp_data.fill_pattern);

defaultAnalysisSetting = 0;
defaultLengthAveraging = 20;
defaultDebug = 0;
defaultDebugModes = 1:harmonic_number;
defaultKeepDebugGraphs = 0;

inputs = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(inputs,'exp_data', @isstruct);
addOptional(inputs,'active_override',NaN);
addOptional(inputs,'passive_override',NaN);
addParameter(inputs,'advanced_fitting',defaultAnalysisSetting, @isnumeric);
addParameter(inputs,'length_averaging',defaultLengthAveraging, validScalarPosNum);
addParameter(inputs,'debug',defaultDebug, @isnumeric);
addParameter(inputs,'debug_modes',defaultDebugModes);
addParameter(inputs,'keep_debug_graphs',defaultKeepDebugGraphs, @isnumeric);
parse(inputs,exp_data,varargin{:});

passive_override = inputs.Results.passive_override;
active_override = inputs.Results.active_override;
adv_fitting = inputs.Results.advanced_fitting;
length_averaging = inputs.Results.length_averaging;

if ~isfield(exp_data, 'data') && isfield(exp_data, 'gddata')
    exp_data.data = exp_data.gddata;
end %if
if ~isfield(exp_data, 'data')
    return
end %if
% Sometimes there is a problem with data transfer. By truncating the data
% length to a multiple of the harmonic number the analysis can proceed.
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = reshape(exp_data.data,[],harmonic_number)';
n_modes = size(exp_data.data,1);

% Find the idicies for the end of each period.
% change the ordering so that the first stage in time is at index 1.
stage_names = flip(exp_data.exp_state_names);
nstages = length(stage_names);
for jjse = 1:nstages
    length_of_stage(jse) = exp_data.([exp_data.exp_state_names{jjse}, '_turns']);
    dwell_of_stage(jjse) = exp_data.([exp_data.exp_state_names{jjse}, '_dwell']);
    if jjse == 1
        end_of_stage(jjse) = length_of_stage(jjse);
        samples_of_stage{jjse} = (1:end_of_stage(jjse));
        turns_of_stage{jjse} = samples_of_stage{jjse} .* dwell_of_stage(jjse);
    else
        end_of_stage(jjse) = end_of_stage(jjse -1) + length_of_stage(jjse);
        samples_of_stage{jjse} = (end_of_stage(jjse -1) + 1): end_of_stage(jjse);
        turns_of_stage{jjse} = turns_of_stage{jjse -1} + (samples_of_stage{jjse}...
            - samples_of_stage{jjse - 1}(end)) .* dwell_of_stage(jjse);
    end %if
end %for

if size(exp_data.data, 2) < end_of_stage(end)
    warning('growdamp:analysis:noValidData', ['No valid data for ', exp_data.base_name])
    return
end %if

for nq = 1:n_modes
    for ksew = 1:nstages
        stage_data = exp_data.data(nq,samples_of_stage{ksew});
        stage_name = stage_names{ksew};
        threshold_value = min(stage_data); % The 'noise' floor.

        if contains(stage_name, 'growth')
            % growth
            mag_fit = polyfit(turns_of_stage{ksew}, log(abs(stage_data)),1);
            c1 = polyval(mag_fit, turns_of_stage{ksew});
            delta = mean(abs(c1 - log(abs(stage_data)))./c1);
            temp = unwrap(angle(stage_data)) / (2*pi);
            phase_fit = polyfit(x_data,temp,1);
        elseif contains(stage_name, 'active')
            % passive damping
            [mag_fit, delta, phase_fit] = get_damping(turns_of_stage{ksew}, ...
                stage_data, passive_override, length_averaging, ...
                adv_fitting,threshold_value);
        elseif contains(stage_name, 'passive')
            %active damping
            [mag_fit, delta, phase_fit] = get_damping(turns_of_stage{ksew}, ...
                stage_data, active_override, length_averaging, ...
                adv_fitting,threshold_value);
        end %if
        output_data.(stage_name).damping_time(nq) = mag_fit(1);
        output_data.(stage_name).offset(nq) = mag_fit(2);
        output_data.(stage_name).error(nq) = delta;
        output_data.(stage_name).frequency_shift(nq) = phase_fit(1);

        if inputs.Results.debug == 1
            make_debug_graphs(nq, ksew, turns_of_stage{ksew}, stage_data, ...
                exp_data.filename, inputs.Results.keep_debug_graphs)
        end %if
    end %for
end %for