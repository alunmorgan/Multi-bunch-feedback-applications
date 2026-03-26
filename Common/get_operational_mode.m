function return_state = get_operational_mode(mbf_axis)

if strcmp(mbf_axis, 'x')
    state =get_variable('SR23C-DI-TMBF-01:X:BUN:MODE');
elseif strcmp(mbf_axis, 'y')
    state =get_variable('SR23C-DI-TMBF-01:Y:BUN:MODE');
elseif strcmp(mbf_axis, 's')
    state =get_variable('SR23C-DI-LMBF-01:IQ:BUN:MODE');
else
    error('common:get_operational_mode','Unexpected axis.')
end %if

if contains(state, 'Feedback on')
    return_state = "Feedback";
else
    return_state = "TuneOnly";
end %if