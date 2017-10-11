function mbf_growdamp_archival_analysis(data_requested, anal_type, sweep_parameter, parameter_step_size)
% Takes the data extracted by mbf_growdamp_archival_retreval and averages
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
[~, harmonic_number] = mbf_system_config;

for nd = length(data_requested):-1:1
    [s_poly_data, ~] = mbf_growdamp_analysis(data_requested{nd});
    dr(nd,:) = fftshift(squeeze(-s_poly_data(:,2,1))');
    if strcmp(anal_type, 'parameter_sweep') && nargin >2
        param(nd) = data_requested{jes}.(sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')

graph_title = 'Damping rates for different modes';
if nargin == 1
    disp('No analysis type set -- assuming collate')
elseif nargin == 2
    if strcmp(anal_type, 'average')
        dr = mean(dr,1);
    end %if
    if strcmp(anal_type, 'parameter_sweep')
        error('Not enough parameters set for a parameter sweep')
    end %if
elseif nargin == 3
    error('Wrong number of parameters. Should be two or four')
elseif nargin == 4
    if strcmp(anal_type, 'parameter_sweep')
        [dr, param] = mbf_analysis_reorganise_for_parameter_sweep(dr, param, parameter_step_size);
        graph_title = {'Damping rates for different modes';...
            ['as a function of', sweep_parameter];...
            ['Using a step size of ', num2str(current_step_size)]};
    elseif strcmp(anal_type, 'average')
        warning('Ignoring the last two parameters as "average" is set')
        dr = mean(dr,1);
    elseif strcmp(anal_type, 'collate')
        warning('Ignoring the last two parameters as "collate" is set')
    end %if
end %if

figure
hold on
x_plt_axis = (1:harmonic_number) - harmonic_number/2;
y_max = max(max(dr));
y_min = min(min(dr));
plot(x_plt_axis, dr)
xlim([x_plt_axis(1) x_plt_axis(end)])
ylim([y_min y_max])
title(graph_title)
xlabel('Mode')
ylabel('Damping rates (1/turns)')

% add labels if it is a parameter sweep.
if nargin == 4 && strcmp(anal_type, 'parameter_sweep')
    for tb = length(param):-1:1
        labels{tb} = num2str(param(tb));
    end %for
    legend(labels)
end %if

