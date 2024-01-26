function set_variable(variable_names, variable_values, varargin)
% function to set a group of variables. This abstraction allows easier porting
% between EPICS and TANGO (and potentially others)

if ~isempty(varargin)
    system_type = varargin{1};
else
    system_type = 'EPICS'; % Default value FIXME eventualy it should be in a settings file.
end %if

if strcmpi(system_type, 'EPICS')
    lcaPut(variable_names, variable_values);
elseif strcmpi(system_type, 'TANGO')
    error('setVariable:systemTypeError', 'Tango calls are not yet implemented')
else
    error('setVariable:systemTypeError', 'alternative sytem calls are not yet implemented')
end %if
