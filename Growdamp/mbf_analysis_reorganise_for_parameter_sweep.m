function [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, param, parameter_step_size)
% Takes a set of results and a vector of the corresponding 
% parameter values (given by param). Sorts them into oder 
% and averages those data sets which are closer that the parameter step, 
% as defined by parameter_step_size
%
% example: [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, 'current', 20)

last_step = param(1);
section_indicies = 1;
direction_of_slope = 1; % assume parameter is increasing
test = find(param > last_step + parameter_step_size, 1, 'first');
if isempty(test)
    test = find(param < last_step - parameter_step_size, 1, 'first');
    if ~isempty(test)
        direction_of_slope = -1; % parameter is in fact decreasing
    end %if
end %if
if direction_of_slope == 1
    for ns = 1:length(param)
        next_ind = find(param > last_step + parameter_step_size, 1, 'first');
        if isempty(next_ind)
            break
        end %if
        section_indicies = cat(2, section_indicies, next_ind);
        last_step = param(next_ind);
    end %for
elseif direction_of_slope == -1
    for ns = 1:length(param)
        next_ind = find(param < last_step - parameter_step_size, 1, 'first');
        if isempty(next_ind)
            break
        end %if
        section_indicies = cat(2, section_indicies, next_ind);
        last_step = param(next_ind);
    end %for
end %if

section_indicies = cat(2, section_indicies, length(param));

% Take the mean of all the data sets within one parameter step. 
for ess = length(section_indicies) - 1:-1:1
    out_param(ess) = (median(param(section_indicies(ess):section_indicies(ess+1))));
    out_dr(ess,:) = nonanmean(dr(section_indicies(ess):section_indicies(ess+1),:));
end %for
