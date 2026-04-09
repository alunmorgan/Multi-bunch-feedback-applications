function [dataset, times, experimental_setup] = ...
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
%         dataset containing
%         dr_passive (numeric matrix): Passive damping time.
%                                      (bunches vs datasets)
%         dr_active (numeric matrix): Passive damping time.
%                                      (bunches vs datasets)
%         error_passive (numeric matrix): Error of the fit for the passive
%                                         damping rate.
%         error_active (numeric matrix): Error of the fit for the active
%                                        damping rate.
%         times (numeric vector): Datetimes of the datasets.
%         experimental_setup (structure): The setup parameters for the
%                                         analysis.
%
% Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p, 'data_requested',@iscell);
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', 'current', @ischar);
addParameter(p, 'parameter_step', 0.1, validScalarPosNum);
addParameter(p, 'active_override', NaN);
addParameter(p, 'passive_override', NaN);
addParameter(p,'advanced_fitting', 0, @isnumeric);
addParameter(p,'error_threshold', 0.1, @isnumeric);
addParameter(p, 'debug', 0);
p.PartialMatching = false;

parse(p,data_requested, varargin{:});

% %condition the data in order to harmonise data changes made over time.
% for nd = length(data_requested):-1:1
%     data_requested{nd} = growdamp_archive_data_conditioning(data_requested{nd});
% end
ck = 1;
for nd = length(data_requested):-1:1
     if isfield(data_requested{nd}, 'I_dcct5')
        data_requested{nd}.current = data_requested{nd}.I_dcct5;
    end %if
    
    [data, data_state] = mbf_growdamp_analysis(data_requested{nd},...
        'active_override', p.Results.active_override,...
                'passive_override', p.Results.passive_override,...
        'advanced_fitting',p.Results.advanced_fitting, ...
        'debug', p.Results.debug);
    if data_state == 0
        continue
    end %if

    times(ck) = datetime(data_requested{nd}.time);
    if strcmp(p.Results.analysis_type, 'parameter_sweep') && nargin >2
        param(ck) = data_requested{nd}.(p.Results.sweep_parameter);
    end %if
    states = fieldnames(data);
    for st = 1:length(states)
        meass = fieldnames(data.(states{st}));
        for ms = 1:length(meass)
            dataset.(states{st}).(meass{ms})(ck,:) = data.(states{st}).(meass{ms});
        end %for
    end %for
    fprintf('.')
    ck = ck +1;
end %for
fprintf('\n')

% % Removing datasets whose mean error is < error_threshold for the passive section.
% error_av_p = mean(dataset.passive.error,2,'omitnan');
% wanted = find(abs(error_av_p) < p.Results.error_threshold);
% states = fieldnames(dataset);
%     for st = 1:length(states)
%         meass = fieldnames(dataset.(states{st}));
%         for ms = 1:length(meass)
%             dataset.(states{st}).(meass{ms}) = dataset.(states{st}).(meass{ms})(wanted,:);
%         end %for
%     end %for
% times = times(wanted);
% if strcmp(p.Results.analysis_type, 'parameter_sweep')
%     param = param(wanted);
% end %if

experimental_setup.anal_type = p.Results.analysis_type;
if strcmp(p.Results.analysis_type, 'parameter_sweep')
    experimental_setup.sweep_parameter = p.Results.sweep_parameter;
    experimental_setup.parameter_step_size = p.Results.parameter_step;
    if isempty(dataset.passive.damping_time)
        disp('No data left. Try changing analysis settings.')
        return
    else
        [dataset, experimental_setup.param] = ...
            mbf_analysis_reorganise_for_parameter_sweep(dataset, param, ...
            p.Results.parameter_step);
%         [dr_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(dr_active, param, p.Results.parameter_step);
%         [error_passive, ~] = mbf_analysis_reorganise_for_parameter_sweep(error_passive, param, p.Results.parameter_step);
%         [error_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(error_active, param, p.Results.parameter_step);
    end %if
elseif strcmp(p.Results.analysis_type, 'average')
    warning('Archive:Growdamp:setting','Ignoring the last two parameters as "average" is set')
    states = fieldnames(dataset);
    for st = 1:length(states)
        meass = fieldnames(dataset.(states{st}));
        for ms = 1:length(meass)
            dataset.(states{st}).(meass{ms}) = mean(dataset.(states{st}).(meass{ms}),1, 'omitnan');
        end %for
    end %for
end %if


