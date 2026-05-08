function [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, param, parameter_step_size)
% Takes a set of results and a vector of the corresponding
% parameter values (given by param). Sorts them into order
% and averages those data sets which are closer that the parameter step,
% as defined by parameter_step_size
%
% example: [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, [5,6,7], 20)

% ensure the ordering
[param, I] = sort(param);

section_indicies = NaN(length(param),1);
acc = 1;
for ns = param(1):parameter_step_size:param(end)
    ind = find(param >= ns & param < ns + parameter_step_size);
    if isempty(ind)
        continue
    end %if
    section_indicies(ind) = acc;
    acc = acc +1;
end %for

out_param = zeros(acc -1, 1);
for ess = 1:acc -1
    out_param(ess) = round((median(param(section_indicies==ess)))./parameter_step_size) .* parameter_step_size;
end %for

dr =sort_data_in_stucture(dr, I, 1);

% Take the mean of all the data sets within one parameter step.
out_dr = mean_steps_data_in_stucture(dr, section_indicies, acc);

