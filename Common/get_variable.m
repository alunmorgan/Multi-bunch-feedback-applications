function [value, varargout] = get_variable(variable_names, varargin)
% function to get a set of variables. This abstraction allows easier porting
% between EPICS and TANGO (and potentially others)

if ~isempty(varargin)
    if strcmp(varargin{end}, 'EPICS')
        system_type = varargin{end};
    elseif strcmp(varargin{end}, 'TANGO')
        system_type = varargin{end};
    else
        system_type = 'EPICS'; % Default value FIXME eventualy it should be in a settings file.
    end %if
else
    system_type = 'EPICS'; % Default value FIXME eventualy it should be in a settings file.
end %if

if strcmpi(system_type, 'EPICS')
    if ~isempty(varargin)
        if ~ischar(varargin{1})
            [value, timestamp] = lcaGet(variable_names, varargin{1}, varargin{2});
        else
            [value, timestamp] = lcaGet(variable_names);
        end %if
    else
        [value, timestamp] = lcaGet(variable_names);
    end %if
elseif strcmpi(system_type, 'TANGO')
    error('getVariable:systemTypeError', 'Tango calls are not yet implemented')
else
    error('getVariable:systemTypeError', 'alternative sytem calls are not yet implemented')
end %if
varargout{1} = timestamp;