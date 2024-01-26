function [value, varargout] = get_variable(variable_names, varargin)
% function to get a set of variables. This abstraction allows easier porting
% between EPICS and TANGO (and potentially others)

if ~isempty(varargin)
    system_type = varargin{1};
else
    system_type = 'EPICS'; % Default value FIXME eventualy it should be in a settings file.
end %if

if strcmpi(system_type, 'EPICS')
    [value, timestamp] = lcaGet(variable_names);
elseif strcmpi(system_type, 'TANGO')
    error('getVariable:systemTypeError', 'Tango calls are not yet implemented')
else
    error('getVariable:systemTypeError', 'alternative sytem calls are not yet implemented')
end %if
varargout{1} = timestamp;