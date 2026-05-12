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

% Find the name of each stage.
[recorded_stage_names, samples_of_stage, turns_of_stage] = get_stage_details(exp_data);
% conditioning names to conform to current scheme.
recorded_stage_names = regexprep(recorded_stage_names, 'excitation', 'growth');
recorded_stage_names = regexprep(recorded_stage_names, 'act$', 'active');
recorded_stage_names = regexprep(recorded_stage_names, 'nat$', 'passive');

% growth_mag_fit = zeros(n_modes, 2);
% growth_delta = zeros(n_modes, 1);
% growth_phase_fit = zeros(n_modes, 2);
% active_mag_fit = zeros(n_modes, 2);
% active_delta = zeros(n_modes, 1);
% active_phase_fit = zeros(n_modes, 2);
% passive_mag_fit = zeros(n_modes, 2);
% passive_delta = zeros(n_modes, 1);
% passive_phase_fit = zeros(n_modes, 2);

% The 'noise' floor.
for ksew = 1:length(recorded_stage_names)
    threshold_value_part(ksew,:) = min(exp_data.data(:, samples_of_stage{ksew}),[], 2);
end %for
threshold_value = min(threshold_value_part);

if inputs.Results.debug == 1
    % In a separate loop otherwise all the chexks really slow the code down.
    for nq = 1:n_modes
        for ksew = 1:length(recorded_stage_names)
            make_debug_graphs(nq, ksew, turns_of_stage{ksew}, stage_data, ...
                exp_data.filename, inputs.Results.keep_debug_graphs)
        end %if
    end %for
end %for

for nq = 1:n_modes
    growth_ck = 1;
    active_ck = 1;
    passive_ck = 1;
    for ksew = 1:length(recorded_stage_names)
        single_data = exp_data.data(nq, samples_of_stage{ksew});
        if contains(recorded_stage_names{ksew}, 'growth')
            % Growth
            [growth_mag_fit, growth_delta, growth_phase_fit] =...
                get_growth(1:turns_of_stage(ksew), single_data);
            output_data.([recorded_stage_names{ksew}, num2str(growth_ck)]).damping_rate(nq) = growth_mag_fit(1);
            output_data.([recorded_stage_names{ksew}, num2str(growth_ck)]).offset(nq) = growth_mag_fit(2);
            output_data.([recorded_stage_names{ksew}, num2str(growth_ck)]).error(nq) = growth_delta;
            output_data.([recorded_stage_names{ksew}, num2str(growth_ck)]).frequency_shift(nq) = growth_phase_fit(1);
            growth_ck =  growth_ck + 1;
        elseif contains(recorded_stage_names{ksew}, 'active')
            % Active damping
            [active_mag_fit, active_delta, active_phase_fit] =...
                get_damping(1:turns_of_stage(ksew), single_data,...
                inputs.Results.active_override, inputs.Results.length_averaging,...
                inputs.Results.advanced_fitting, threshold_value(nq));
            output_data.([recorded_stage_names{ksew}, num2str(active_ck)]).damping_rate(nq) = active_mag_fit(1);
            output_data.([recorded_stage_names{ksew}, num2str(active_ck)]).offset(nq) = active_mag_fit(2);
            output_data.([recorded_stage_names{ksew}, num2str(active_ck)]).error(nq) = active_delta;
            output_data.([recorded_stage_names{ksew}, num2str(active_ck)]).frequency_shift(nq) = active_phase_fit(1);
            active_ck = active_ck +1;
        elseif contains(recorded_stage_names{ksew}, 'passive')
            % Passive damping
            [passive_mag_fit, passive_delta, passive_phase_fit] =...
                get_damping(1:turns_of_stage(ksew), single_data,...
                inputs.Results.passive_override, inputs.Results.length_averaging,...
                inputs.Results.advanced_fitting, threshold_value(nq));
            output_data.([recorded_stage_names{ksew}, num2str(passive_ck)]).damping_rate(nq) = passive_mag_fit(1);
            output_data.([recorded_stage_names{ksew}, num2str(passive_ck)]).offset(nq) = passive_mag_fit(2);
            output_data.([recorded_stage_names{ksew}, num2str(passive_ck)]).error(nq) = passive_delta;
            output_data.([recorded_stage_names{ksew}, num2str(passive_ck)]).frequency_shift(nq) = passive_phase_fit(1);
            passive_ck = passive_ck + 1;
        end %if
    end %for
end %for