
current = lcaGet('SR-DI-DCCT-01:SIGNAL');
ebpm_list = generate_ebpm_list;
output = BPM_SA_get_data(ebpm_list, 'all_channels', 'yes');

for n = 1:length(ebpm_list)
scale_names{n} = char(strcat(ebpm_list{n}, ':CF:ISCALE_S'));
end 

ebpm_scales = lcaGet(scale_names');

for hww = 1:length(ebpm_list)
fractional_errors(hww,1) = mean(output.(regexprep(ebpm_list{hww}, '-', '_')).CURRENT ./ current);
new_scales(hww,1) = ebpm_scales(hww) *fractional_errors(hww,1);
end

% for js  = 1:length(ebpm_list)
% lcaPut(scale_names{js}, new_scales(js))
% end