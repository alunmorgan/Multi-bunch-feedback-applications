function [bunch_data, tune_data, times, experimental_setup] = ...
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
%         times (numeric vector): Datenums of the datasets.
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
fold=1;
for nd = length(data_requested):-1:1
    times(nd) = datenum(data_requested{nd}.time);
    [bunch_data(nd,:, :), tune_data(nd,:)]  = mbf_spectrum_analysis(data_requested{nd}, fold);
    if strcmp(p.Results.analysis_type, 'parameter_sweep')
        param(nd) = data_requested{nd}.(p.Results.sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')

experimental_setup.anal_type = p.Results.analysis_type;

if strcmp(p.Results.analysis_type, 'parameter_sweep')
    experimental_setup.sweep_parameter = p.Results.sweep_parameter;
    experimental_setup.parameter_step_size = p.Results.parameter_step;

    [bunch_data, experimental_setup.param] = ...
        mbf_analysis_reorganise_for_parameter_sweep(...
        bunch_data, param, p.Results.parameter_step);
     [tune_data, experimental_setup.param] = ...
        mbf_analysis_reorganise_for_parameter_sweep(...
        tune_data, param, p.Results.parameter_step);


elseif strcmp(p.Results.analysis_type, 'average')
    warning('Ignoring the last two parameters as "average" is set')
    bunch_data = mean(bunch_data, 1, 'omitnan');
    tune_data = mean(tune_data, 1, 'omitnan');
end %if


