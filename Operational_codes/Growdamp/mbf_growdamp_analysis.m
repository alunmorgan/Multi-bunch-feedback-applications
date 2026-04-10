function [output_data, output_state] = mbf_growdamp_analysis(exp_data, varargin)
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

output_state = 1;

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
if isfield(exp_data, 'state_names')
    stage_names = exp_data.state_names;
elseif isfield(exp_data, ['seq1', '_capture_state'])
    for n = 1:exp_data.start_state
        if contains(exp_data.(['seq' num2str(n), '_capture_state']), 'Discard')
            exp_data.state_names{n} = 'spacer';
        else
            if contains(exp_data.(['seq' num2str(n), '_enable']), 'On')
                exp_data.state_names{n} = 'growth';
            else
                if contains(exp_data.(['seq' num2str(n), '_bank_select']), 'Bank 2')
                    exp_data.state_names{n} = 'active';
                else
                    exp_data.state_names{n} = 'passive';
                end %if
            end %if
        end %if
    end %for
else
    % Old dataset use implict order in structure to order stages.
    test = fieldnames(exp_data);
    names = test(contains(test, '_turns'));
    names = names(~contains(names, 'spacer'));
    expected_length = 0;
    for nrs = 1:length(names)
        expected_length = expected_length + exp_data.(names{nrs});
    end %for
    if expected_length > size(exp_data.data, 2)
        names = names(~contains(names, 'growth2'));
    end %if
    expected_length = 0;
    for nrs = 1:length(names)
        expected_length = expected_length + exp_data.(names{nrs});
    end %for
    if expected_length > size(exp_data.data, 2)
        output_state = 0;
        output_data = NaN;
        return
    end %if
    for hs = 1:length(names)
        stage_names{hs} = regexprep(names{hs}, '_turns', '');
    end

    stage_names = flip(stage_names);
end %if
ck = 1;
for jjse = 1:length(stage_names)
    if ~contains(stage_names{jjse}, 'spacer')
        recorded_stage_name{ck} = stage_names{jjse};
        length_of_stage = exp_data.states{jjse}.duration;
        dwell_of_stage = exp_data.states{jjse}.dwell;
        if ck == 1
            end_of_stage(ck) = length_of_stage;
            samples_of_stage{ck} = (1:end_of_stage(ck));
            turns_of_stage{ck} = samples_of_stage{ck} .* dwell_of_stage;
        else
            end_of_stage(ck) = end_of_stage(ck -1) + length_of_stage;
            samples_of_stage{ck} = (end_of_stage(ck -1) + 1): end_of_stage(ck);
            turns_of_stage{ck} = samples_of_stage{ck}.* dwell_of_stage;
        end %if
        ck = ck +1;
    end %if
end %for

for nq = 1:n_modes
    for ksew = 1:length(recorded_stage_name)
        stage_data = exp_data.data(nq, samples_of_stage{ksew});
        stage_name = recorded_stage_name{ksew};
        threshold_value = min(stage_data); % The 'noise' floor.

        if contains(stage_name, 'excitation')
            % growth
            mag_fit = polyfit(turns_of_stage{ksew}, log(abs(stage_data)),1);
            c1 = polyval(mag_fit, turns_of_stage{ksew});
            delta = mean(abs(c1 - log(abs(stage_data)))./c1);
            temp = unwrap(angle(stage_data)) / (2*pi);
            phase_fit = polyfit(turns_of_stage{ksew},temp,1);
        elseif contains(stage_name, 'active') || contains(stage_name, 'act')
            stage_name = regexprep(stage_name, 'active', 'WWW');
            stage_name = regexprep(stage_name, 'act', 'WWW');
            stage_name = regexprep(stage_name, 'WWW', 'active');
            % passive damping
            [mag_fit, delta, phase_fit] = get_damping(turns_of_stage{ksew}, ...
                stage_data, inputs.Results.active_override,...
                inputs.Results.length_averaging, ...
                inputs.Results.advanced_fitting,threshold_value);
        elseif contains(stage_name, 'passive') || contains(stage_name, 'nat')
            stage_name = regexprep(stage_name, 'nat', 'passive');
            %active damping
            [mag_fit, delta, phase_fit] = get_damping(turns_of_stage{ksew}, ...
                stage_data, inputs.Results.passive_override,...
                inputs.Results.length_averaging, ...
                inputs.Results.advanced_fitting,threshold_value);
        end %if
        output_data.(stage_name).damping_rate(nq) = mag_fit(1);
        output_data.(stage_name).offset(nq) = mag_fit(2);
        output_data.(stage_name).error(nq) = delta;
        output_data.(stage_name).frequency_shift(nq) = phase_fit(1);

        if inputs.Results.debug == 1
            make_debug_graphs(nq, ksew, turns_of_stage{ksew}, stage_data, ...
                exp_data.filename, inputs.Results.keep_debug_graphs)
        end %if
    end %for
end %for