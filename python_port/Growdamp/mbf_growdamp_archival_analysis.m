function [dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = ...
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
%         extents (structure): Contains the max and min values of the machine operating parameters. 
%
% Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

extents = struct;
for nd = length(data_requested):-1:1
    data_slice = data_requested{nd};
    [s_poly_data, ~] = mbf_growdamp_analysis(data_slice);
    f_nms = fieldnames(data_slice);
    for kef = 1:length(f_nms)
        data_field_name{1} = f_nms{kef};
        if strcmp(data_field_name{1}, 'data') || strcmp(data_field_name{1}, 'filename') ...
                || strcmp(data_field_name{1}, 'modes') || strcmp(data_field_name{1}, 'pinhole')...
                || strcmp(data_field_name{1}, 'injection') || strcmp(data_field_name{1}, 'base_name') 
            continue
        end %if
        % This section is to deal with variations in data naming 
        % and structuring over the years.
        extent_field_name{1} = data_field_name{1};
        if strcmp(data_field_name{1}, 'I_bpm')
            extent_field_name{1} = 'current';
        end %if
        if strcmp(data_field_name{1}, 'fill')
            extent_field_name{1} = 'fill_pattern';
        end %if
        if strcmp(data_field_name{1}, 'id')
            data_field_name{1} = 'i12field';
            extent_field_name{1} = 'wiggler_field_I12';
            data_field_name{2} = 'i15field';
            extent_field_name{2} = 'wiggler_field_I15';
        end %if
          if strcmp(data_field_name{1}, 'life')
                          data_field_name{1} = 'life300sec';
            extent_field_name{1} = 'beam_lifetime';
          end %if
        if strcmp(data_field_name{1}, 'RFread')
            data_field_name{1} = 'RFread';
            extent_field_name{1} = 'cavity1_voltage';
            data_field_name{2} = 'RFread';
            extent_field_name{2} = 'cavity2_voltage';
        end %if
        for haw = 1:length(data_field_name)
            if ~isfield(extents, extent_field_name{haw})
                if strcmp(extent_field_name{haw}, 'beam_lifetime')
                    extents.(extent_field_name{haw}){1} = data_slice.('life').('bpm').(data_field_name{haw});
                    extents.(extent_field_name{haw}){2} = data_slice.('life').('bpm').(data_field_name{haw});  
                elseif strcmp(data_field_name{haw}, 'RFread')
                    extents.(extent_field_name{haw}){1} = data_slice.(data_field_name{haw})(haw);
                    extents.(extent_field_name{haw}){2} = data_slice.(data_field_name{haw})(haw);
                elseif strcmp(data_field_name{haw}, 'i12field') || strcmp(data_field_name{haw}, 'i15field')
                    extents.(extent_field_name{haw}){1} = data_slice.('id').(data_field_name{haw});
                    extents.(extent_field_name{haw}){2} = data_slice.('id').(data_field_name{haw});
                else
                    extents.(extent_field_name{haw}){1} = data_slice.(data_field_name{haw});
                    extents.(extent_field_name{haw}){2} = data_slice.(data_field_name{haw});
                end %if
            else
%                 disp(['nd = ',num2str(nd), 'kef = ', num2str(kef)])
                if strcmp(extent_field_name{haw}, 'beam_lifetime')
                    extents.(extent_field_name{haw}){1} = ...
                        max(data_slice.('life').('bpm').(data_field_name{haw}),...
                        extents.(extent_field_name{haw}){1}, 'omitnan');
                    extents.(extent_field_name{haw}){2} = ...
                        min(data_slice.('life').('bpm').(data_field_name{haw}),...
                        extents.(extent_field_name{haw}){2}, 'omitnan');
                elseif strcmp(data_field_name{1}, 'RFread')
                    extents.(extent_field_name{haw}){1} = ...
                        max(data_slice.(data_field_name{haw})(haw),...
                        extents.(extent_field_name{haw}){1}, 'omitnan');
                    extents.(extent_field_name{haw}){2} = ...
                        min(data_slice.(data_field_name{haw})(haw),...
                        extents.(extent_field_name{haw}){2}, 'omitnan');
                elseif strcmp(data_field_name{haw}, 'i12field') || strcmp(data_field_name{haw}, 'i15field')
                    extents.(extent_field_name{haw}){1} = ...
                        max(data_slice.('id').(data_field_name{haw}),...
                        extents.(extent_field_name{haw}){1}, 'omitnan');
                    extents.(extent_field_name{haw}){2} = ...
                        min(data_slice.('id').(data_field_name{haw}),...
                        extents.(extent_field_name{haw}){2}, 'omitnan');
                else
                    if ~iscell(data_slice.(data_field_name{haw}))
                        extents.(extent_field_name{haw}){1} = ...
                            max(data_slice.(data_field_name{haw}),...
                            extents.(extent_field_name{haw}){1}, 'omitnan');
                        extents.(extent_field_name{haw}){2} = ...
                            min(data_slice.(data_field_name{haw}),...
                            extents.(extent_field_name{haw}){2}, 'omitnan');
                    end %if
                end %if
            end %if
        end %for
        clear extent_field_name data_field_name
    end %for
    times(nd) = datenum(data_slice.time);
    dr_passive(nd,:) = fftshift(squeeze(-s_poly_data(:,2,1))');
    dr_active(nd,:) = fftshift(squeeze(-s_poly_data(:,3,1))');
    error_passive(nd,:) = squeeze(-s_poly_data(:,2,3))';
    error_active(nd,:) = squeeze(-s_poly_data(:,3,3))';
    if strcmp(anal_type, 'parameter_sweep') && nargin >2
        param(nd) = data_slice.(sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')
experimental_setup.anal_type = anal_type;
if nargin == 1
    disp('No analysis type set -- assuming collate')
elseif nargin == 2
    if strcmp(anal_type, 'average')
        dr_passive = mean(dr_passive,1, 'omitnan');
        dr_active = mean(dr_active,1, 'omitnan');
    end %if
    if strcmp(anal_type, 'parameter_sweep')
        error('Not enough parameters set for a parameter sweep')
    end %if
elseif nargin == 3
    error('Wrong number of parameters. Should be two or four')
elseif nargin == 4
    if strcmp(anal_type, 'parameter_sweep')
        experimental_setup.sweep_parameter = sweep_parameter;
        experimental_setup.parameter_step_size = parameter_step_size;
        [dr_passive, experimental_setup.param] = mbf_analysis_reorganise_for_parameter_sweep(dr_passive, param, parameter_step_size);
        [dr_active, ~] = mbf_analysis_reorganise_for_parameter_sweep(dr_active, param, parameter_step_size);
    elseif strcmp(anal_type, 'average')
        warning('Ignoring the last two parameters as "average" is set')
        dr_passive = mean(dr_passive,1);
        dr_active = mean(dr_active,1);
    elseif strcmp(anal_type, 'collate')
        warning('Ignoring the last two parameters as "collate" is set')
    end %if
end %if

% Removing datasets whose mean error is < 0.02 for the passive section.
error_av_p = nonanmean(error_passive,2);
error_av_a = nonanmean(error_active,2);
wanted1 = find(abs(error_av_p) < 0.01);
wanted2 = find(abs(error_av_a) < 0.01);
wanted = intersect(wanted1, wanted2);
dr_passive = dr_passive(wanted,:);
dr_active = dr_active(wanted,:);
error_passive = error_passive(wanted,:);
error_active = error_active(wanted,:);
times = times(wanted);