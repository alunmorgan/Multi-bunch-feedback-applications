function mbf_get_then_put(pv_name, new_value)
% retrieves the value before the set_variable and then write the new value to the
% PV.
%
% example: mbf_get_then_put(pv_name, new_value)

[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};

if iscell(pv_name)
    for hse = 1:length(pv_name)
        original_value = get_variable(pv_name{hse});
        set_variable(pv_name, new_value)
        save(fullfile(root_string, 'captured_config', pv_name{hse}), 'original_value')
    end %for
else
    original_value = get_variable(pv_name);
    set_variable(pv_name, new_value)
    save(fullfile(root_string, 'captured_config', pv_name), 'original_value')
end %if
