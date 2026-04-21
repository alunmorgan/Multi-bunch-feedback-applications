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
fprintf('\n')
for nq = 1:n_modes
    for ksew = 1:length(recorded_stage_names)
        stage_data = exp_data.data(nq, samples_of_stage{ksew});
        stage_label = recorded_stage_names{ksew};
        threshold_value = min(stage_data); % The 'noise' floor.
        % FIXME make it possible to have multiple of each stage.
        if contains(stage_label, 'excitation') || contains(stage_label, 'growth')
            stage_label = 'growth';
            % growth
            mag_fit = polyfit(1:turns_of_stage(ksew), log(abs(stage_data)),1);
            c1 = polyval(mag_fit, 1:turns_of_stage(ksew));
            delta = mean(abs(c1 - log(abs(stage_data)))./c1);
            temp = unwrap(angle(stage_data)) / (2*pi);
            phase_fit = polyfit(1:turns_of_stage(ksew),temp,1);
        elseif contains(stage_label, 'active') || contains(stage_label, 'act')
            stage_label = 'active';
            %active damping
            [mag_fit, delta, phase_fit] = get_damping(1:turns_of_stage(ksew), ...
                stage_data, inputs.Results.active_override,...
                inputs.Results.length_averaging, ...
                inputs.Results.advanced_fitting,threshold_value);
        elseif contains(stage_label, 'passive') || contains(stage_label, 'nat')
            stage_label = 'passive';
            % passive damping
            [mag_fit, delta, phase_fit] = get_damping(1:turns_of_stage(ksew), ...
                stage_data, inputs.Results.passive_override,...
                inputs.Results.length_averaging, ...
                inputs.Results.advanced_fitting,threshold_value);
        end %if
        output_data.(stage_label).damping_rate(nq) = mag_fit(1);
        output_data.(stage_label).offset(nq) = mag_fit(2);
        output_data.(stage_label).error(nq) = delta;
        output_data.(stage_label).frequency_shift(nq) = phase_fit(1);
        if inputs.Results.debug == 1
            make_debug_graphs(nq, ksew, turns_of_stage{ksew}, stage_data, ...
                exp_data.filename, inputs.Results.keep_debug_graphs)
        end %if
    end %for
end %for