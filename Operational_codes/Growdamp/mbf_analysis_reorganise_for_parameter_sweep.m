function [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, param, parameter_step_size)
% Takes a set of results and a vector of the corresponding
% parameter values (given by param). Sorts them into order
% and averages those data sets which are closer that the parameter step,
% as defined by parameter_step_size
%
% example: [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, 'current', 20)

% ensure the ordering
[param, I] = sort(param);
dr = dr(I, :, :);
acc = 1;
section_indicies = NaN(length(param),1);
for ns = param(1):parameter_step_size:param(end)
    ind = find(param >= ns & param < ns + parameter_step_size);
    if isempty(ind)
        continue
    end %if
    section_indicies(ind) = acc;
    acc = acc +1;
end %for

% Take the mean of all the data sets within one parameter step.
for ess = acc -1:-1:1
    out_param(ess) = round((median(param(section_indicies==ess)))./parameter_step_size) .* parameter_step_size;
    out_dr(ess,:, :) = nonanmean(dr(section_indicies==ess,:, :),1);
end %for
