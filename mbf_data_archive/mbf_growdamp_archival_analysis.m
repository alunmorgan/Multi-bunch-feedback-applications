function [dr_passive, dr_active, error_passive, error_active, times, experimental_setup] = ...
    mbf_growdamp_archival_analysis(data_requested, varargin)
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
%         dr_passive (numeric matrix): Passive damping rate.
%                                      (bunches vs datasets)
%         dr_active (numeric matrix): Passive damping rate.
%                                      (bunches vs datasets)
%         error_passive (numeric matrix): Error of the fit for the passive
%                                         damping rate.
%         error_active (numeric matrix): Error of the fit for the active
%                                        damping rate.
%         times (numeric vector): Datenums of the datasets.
%         experimental_setup (structure): The setup parameters for the
%                                         analysis.
%
% Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

default_sweep_parameter = 'current';
default_parameter_step_size = 0.1;
defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;


p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p, 'data_requested',@iscell);
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);
addParameter(p, 'overrides', defaultOverrides);
addParameter(p,'advanced_fitting', defaultAnalysisSetting, @isnumeric);
addParameter(p, 'debug', 0);
p.PartialMatching = false;

parse(p,data_requested, varargin{:});

anal_type = p.Results.analysis_type;
sweep_parameter = p.Results.sweep_parameter;
parameter_step_size = p.Results.parameter_step;
overrides = p.Results.overrides;
debug = p.Results.debug;
advanced_fitting = p.Results.advanced_fitting;

%condition the data in order to harmonise data changes made over time.
for nd = length(data_requested):-1:1
    data_requested{nd} = growdamp_archive_data_conditioning(data_requested{nd});
end

for nd = length(data_requested):-1:1
    [s_poly_data, ~] = mbf_growdamp_analysis(data_requested{nd},...
        'override', overrides,...
        'advanced_fitting',advanced_fitting, ...
        'debug', debug);
    times(nd) = datenum(data_requested{nd}.time);
    dr_passive(nd,:) = fftshift(squeeze(-s_poly_data(:,2,1))');
    dr_active(nd,:) = fftshift(squeeze(-s_poly_data(:,3,1))');
    error_passive(nd,:) = squeeze(-s_poly_data(:,2,3))';
    error_active(nd,:) = squeeze(-s_poly_data(:,3,3))';
    if isfield(data_requested{nd}, 'I_dcct5')
        data_requested{nd}.current = data_requested{nd}.I_dcct5;
    end %if
    if strcmp(anal_type, 'parameter_sweep') && nargin >2
        param(nd) = data_requested{nd}.(sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')

% Removing datasets whose mean error is < 0.02 for the passive section.
error_av_p = mean(error_passive,2,'omitnan');
% error_av_a = mean(error_active,2,'omitnan');
wanted = find(abs(error_av_p) < 0.01);
% wanted2 = find(abs(error_av_a) < 0.01);
% wanted = intersect(wanted1, wanted2);
dr_passive = dr_passive(wanted,:);
dr_active = dr_active(wanted,:);
error_passive = error_passive(wanted,:);
error_active = error_active(wanted,:);
times = times(wanted);
if strcmp(anal_type, 'parameter_sweep')
    param = param(wanted);
end %if


experimental_setup.anal_type = anal_type;
if strcmp(anal_type, 'parameter_sweep')
    experimental_setup.sweep_parameter = sweep_parameter;
    experimental_setup.parameter_step_size = parameter_step_size;
    if isempty(dr_passive)
        disp('No data left. Try changing analysis settings.')
        return
    else
        [dr_passive, experimental_setup.param] = mbf_analysis_reorganise_for_parameter_sweep(dr_passive, param, parameter_step_size);
        [dr_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(dr_active, param, parameter_step_size);
        [error_passive, ~] = mbf_analysis_reorganise_for_parameter_sweep(error_passive, param, parameter_step_size);
        [error_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(error_active, param, parameter_step_size);
    end %if
elseif strcmp(anal_type, 'average')
    warning('Ignoring the last two parameters as "average" is set')
    dr_passive = mean(dr_passive,1, 'omitnan');
    dr_active = mean(dr_active,1, 'omitnan');
    error_passive = mean(error_passive,1, 'omitnan'); %is it OK to just average the errors?
    error_active = mean(errorr_active,1, 'omitnan');
end %if


