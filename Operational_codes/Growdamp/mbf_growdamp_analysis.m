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

output_data.('growth').damping_rate = NaN(n_modes, 1);
output_data.('growth').offset = NaN(n_modes, 1);
output_data.('growth').error = NaN(n_modes, 1);
output_data.('growth').frequency_shift = NaN(n_modes, 1);
output_data.('active').damping_rate = NaN(n_modes, 1);
output_data.('active').offset = NaN(n_modes, 1);
output_data.('active').error = NaN(n_modes, 1);
output_data.('active').frequency_shift = NaN(n_modes, 1);
output_data.('passive').damping_rate = NaN(n_modes, 1);
output_data.('passive').offset = NaN(n_modes, 1);
output_data.('passive').error = NaN(n_modes, 1);
output_data.('passive').frequency_shift = NaN(n_modes, 1);
% FIXME make it possible to have multiple of each stage.
for ksew = 1:length(recorded_stage_names)
    if contains(recorded_stage_names{ksew}, 'excitation') ||...
            contains(recorded_stage_names{ksew}, 'growth')
        growth_samples = samples_of_stage{ksew};
        growth_turns = turns_of_stage(ksew);
        growth = exp_data.data(:, growth_samples);
    elseif contains(recorded_stage_names{ksew}, 'active') ||...
            contains(recorded_stage_names{ksew}, 'act')
        active_samples = samples_of_stage{ksew};
        active_turns = turns_of_stage(ksew);
        active = exp_data.data(:, active_samples);
    elseif contains(recorded_stage_names{ksew}, 'passive') ||...
            contains(recorded_stage_names{ksew}, 'nat')
        passive_samples = samples_of_stage{ksew};
        passive_turns = turns_of_stage(ksew);
        passive = exp_data.data(:, passive_samples);
    end %if
end %for

% if inputs.Results.debug == 1
%     make_debug_graphs(nq, ksew, turns_of_stage{ksew}, stage_data, ...
%         exp_data.filename, inputs.Results.keep_debug_graphs)
% end %if

active_override = inputs.Results.active_override;
passive_override = inputs.Results.passive_override;
length_averaging = inputs.Results.length_averaging;
advanced_fitting = inputs.Results.advanced_fitting;
growth_mag_fit = zeros(n_modes, 2);
growth_delta = zeros(n_modes, 1);
growth_phase_fit = zeros(n_modes, 2);
active_mag_fit = zeros(n_modes, 2);
active_delta = zeros(n_modes, 1);
active_phase_fit = zeros(n_modes, 2);
passive_mag_fit = zeros(n_modes, 2);
passive_delta = zeros(n_modes, 1);
passive_phase_fit = zeros(n_modes, 2);
for nq = 1:n_modes
    threshold_value = min([min(growth(nq,:)), min(active(nq,:)), min(passive(nq,:))]); % The 'noise' floor.
    % Growth
    growth_mag_fit(nq,:) = polyfit(1:growth_turns, log(abs(growth(nq,:))),1);
    c1 = polyval(growth_mag_fit(nq,:), 1:growth_turns);
    growth_delta(nq, 1) = mean(abs(c1 - log(abs(growth(nq,:))))./c1);
    temp = unwrap(angle(growth(nq,:))) / (2*pi);
    growth_phase_fit(nq,:) = polyfit(1:growth_turns,temp,1);
    % Active damping
    [active_mag_fit(nq,:), active_delta(nq, 1), active_phase_fit(nq,:)] = get_damping(1:active_turns, ...
        active(nq,:), active_override, length_averaging, advanced_fitting, threshold_value);
    % Passive damping
    [passive_mag_fit(nq,:), passive_delta(nq, 1), passive_phase_fit(nq,:)] = get_damping(1:passive_turns, ...
        passive(nq,:), passive_override, length_averaging, advanced_fitting, threshold_value);
end %for

output_data.growth.damping_rate = growth_mag_fit(:,1);
output_data.growth.offset = growth_mag_fit(:,2);
output_data.growth.error = growth_delta;
output_data.growth.frequency_shift = growth_phase_fit(:,1);
output_data.active.damping_rate = active_mag_fit(:,1);
output_data.active.offset = active_mag_fit(:,2);
output_data.active.error = active_delta;
output_data.active.frequency_shift = active_phase_fit(:,1);
output_data.passive.damping_rate = passive_mag_fit(:,1);
output_data.passive.offset = passive_mag_fit(:,2);
output_data.passive.error = passive_delta;
output_data.passive.frequency_shift = passive_phase_fit(:,1);