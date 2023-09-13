function [spec_data, times, experimental_setup] = ...
    mbf_spectra_archival_analysis(data_requested, varargin)
% Takes the data extracted by mbf_growdamp_archival_retreval and operates
% across all datasets. Then plots the results.
%
% Args:
%       data_requested (cell array of structures) : Data to be analysed.
%       analysis_type (str): To select the type of analysis
%                       (collate, average, parameter_sweep)
%       sweep_parameter (str): Parameter to be used. This name must exist
%                              in the data structure. (only needed if
%                              anal_type set to 'parameter sweep')
%       parameter_step_size (float): Defines the spacing of the steps in
%                                    the parameter sweep.
%                                    Multiple data sets which are on the same
%                                    step will be averaged. (only needed if
%                                    anal_type set to 'parameter sweep')
%       overrides (list of ints): Two values setting the number of turns to
%                                    analyse (passive, active)
%       debug(int): if 1 then outputs graphs of individual modes to allow
%                                    selection nof appropriate overrides.
%
% Returns:
%         data_magnitude (numeric matrix):
%         data_phase (numeric matrix):
%         times (numeric vector): Datetimes of the datasets.
%         experimental_setup (structure): The setup parameters for the
%                                         analysis.
%
% Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

default_sweep_parameter = 'current';
default_parameter_step_size = 0.1;

p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p, 'data_requested',@iscell);
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);

p.PartialMatching = false;

parse(p,data_requested, varargin{:});
for fnd = length(data_requested):-1:1
    nturns_all(fnd) = data_requested{fnd}.n_turns;
end %for
max_turns = max(nturns_all);
for nd = length(data_requested):-1:1
    times(nd) = datetime(data_requested{nd}.time);
    spec_data{nd}  = mbf_spectrum_analysis(data_requested{nd}, max_turns);
    if strcmp(p.Results.analysis_type, 'parameter_sweep')
        param(nd) = data_requested{nd}.(p.Results.sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')

experimental_setup.anal_type = p.Results.analysis_type;
fnames = fieldnames(spec_data{1});
for sbd = 1:length(fnames)
    spec_data_temp.(fnames{sbd}) = NaN(1,1,2);%Forcing it to use 3 dimensions.
    for brs = 1:length(data_requested)
        data_size = size(spec_data{brs}.(fnames{sbd}));
        target_size = size(spec_data_temp.(fnames{sbd}));
        spec_data_temp.(fnames{sbd}) = padarray(spec_data_temp.(fnames{sbd}),[0,data_size(1) - target_size(2), data_size(2) - target_size(3)], NaN, 'post');
        spec_data_temp.(fnames{sbd})(brs, 1:data_size(1),1:data_size(2)) = permute(spec_data{brs}.(fnames{sbd}), [3,1,2]);
    end %for
end %for
spec_data = spec_data_temp;
if strcmp(p.Results.analysis_type, 'parameter_sweep')
    experimental_setup.sweep_parameter = p.Results.sweep_parameter;
    experimental_setup.parameter_step_size = p.Results.parameter_step;
    for sbd = 1:length(fnames)
        [spec_data.(fnames{sbd}), experimental_setup.param] = ...
            mbf_analysis_reorganise_for_parameter_sweep(...
            spec_data.(fnames{sbd}), param, p.Results.parameter_step);
    end %for
elseif strcmp(p.Results.analysis_type, 'average')
    warning('Archive:Spectra:setting','Ignoring the last two parameters as "average" is set')
    for sbd = 1:length(fnames)
        spec_data.(fnames{sbd}) = mean((fnames{sbd}), 1, 'omitnan');
    end %for
end %if


