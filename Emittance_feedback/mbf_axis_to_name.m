function name = mbf_axis_to_name(mbf_axis)
if strcmpi(mbf_axis, 'x')
    name = 'SR23C-DI-TMBF-01:X:';
elseif strcmpi(mbf_axis, 'y')
    name = 'SR23C-DI-TMBF-01:Y:';
elseif strcmpi(mbf_axis, 's')
    name = 'SR23C-DI-LMBF-01:IQ:';
end %if