function [dr_passive, dr_active, error_passive, error_active, times, setup, extents] = ...
    mbf_growdamp_archival_analysis(data_requested, anal_type, sweep_parameter, parameter_step_size)
% Takes the data extracted by mbf_growdamp_archival_retreval and operates
% across all datasets. Then plots the results.
%
% Args:
%       data_requested (cell array of structures) : Data to be analysed.
%       anal_type (str): To select the type of analysis
%                       (collate, average, parameter_sweep)
%       sweep_parameter (str): Parameter to be used. This name must exist
%                              in the data structure. (only needed if
%                              anal_type set to 'parameter sweep')
%       parameter_step_size (float): Defines the spacing of the steps in
%                                    the parameter sweep.
%                                    Multiple data sets which are on the same
%                                    step will be averaged. (only needed if
%                                    anal_type set to 'parameter sweep')
%
% Example: mbf_growdamp_archival_analysis(data_requested, 'average')

% Getting the desired system setup parameters.
% [~, harmonic_number, ~] = mbf_system_config;

extents = struct;
for nd = length(data_requested):-1:1
    [s_poly_data, ~] = mbf_growdamp_analysis(data_requested{nd});
    f_nms = fieldnames(data_requested{nd});
    for kef = 1:length(f_nms)
        if ~isfield(extents, f_nms{kef})
            extents.(f_nms{kef}){1} = data_requested{nd}.(f_nms{kef});
            extents.(f_nms{kef}){2} = data_requested{nd}.(f_nms{kef});
        else
            if ~iscell(data_requested{nd}.(f_nms{kef}))
                extents.(f_nms{kef}){1} = max(data_requested{nd}.(f_nms{kef}), extents.(f_nms{kef}){1});
                %START HERE... need to rename setup
                extents.(f_nms{kef}){2} = min(data_requested{nd}.(f_nms{kef}), extents.(f_nms{kef}){2});
            end %if
        end %if
    end %for
    times(nd) = datenum(data_requested{nd}.time);
    dr_passive(nd,:) = fftshift(squeeze(-s_poly_data(:,2,1))');
    dr_active(nd,:) = fftshift(squeeze(-s_poly_data(:,3,1))');
    error_passive(nd,:) = squeeze(-s_poly_data(:,2,3))';
    error_active(nd,:) = squeeze(-s_poly_data(:,3,3))';
    if strcmp(anal_type, 'parameter_sweep') && nargin >2
        param(nd) = data_requested{nd}.(sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')
setup.anal_type = anal_type;
if nargin == 1
    disp('No analysis type set -- assuming collate')
elseif nargin == 2
    if strcmp(anal_type, 'average')
        dr_passive = mean(dr_passive,1);
        dr_active = mean(dr_active,1);
    end %if
    if strcmp(anal_type, 'parameter_sweep')
        error('Not enough parameters set for a parameter sweep')
    end %if
elseif nargin == 3
    error('Wrong number of parameters. Should be two or four')
elseif nargin == 4
    if strcmp(anal_type, 'parameter_sweep')
        setup.sweep_parameter = sweep_parameter;
        setup.parameter_step_size = parameter_step_size;
        [dr_passive, setup.param] = mbf_analysis_reorganise_for_parameter_sweep(dr_passive, param, parameter_step_size);
        [dr_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(dr_active, param, parameter_step_size);
    elseif strcmp(anal_type, 'average')
        warning('Ignoring the last two parameters as "average" is set')
        dr_passive = mean(dr_passive,1);
        dr_active = mean(dr_active,1);
    elseif strcmp(anal_type, 'collate')
        warning('Ignoring the last two parameters as "collate" is set')
    end %if
end %if