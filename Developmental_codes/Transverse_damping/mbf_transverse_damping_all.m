function td = mbf_transverse_damping_all(mbf_axis, varargin)
% Top level function to run the transverse damping measurements on the 
% selected plane
%   Args:
%       mbf_axis(str): 'x','y', or 's'
%       mbf_mode(int): The mode the set up to operate at. Sometimes the
%                      signal to noise is better at higher modes.
%   Returns:
%       td(structure): The data captured from all the relavent systems.
%
% Example: td = mbf_transverse_damping_all('x')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};


addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'mbf_mode', NaN, valid_number);
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));

parse(p, mbf_axis, varargin{:});

mbf_tools

% Get the tunes
 tunes = get_all_tunes(mbf_axis);
tune = tunes.([mbf_axis,'_tune']);

if isnan(tune.upper_sideband)
    disp('Could not get the tune values')
    return
end %if

mbf_growdamp_setup(mbf_axis, tune.upper_sideband, 'single_mode', p.Results.mbf_mode)

td = mbf_transverse_damping_capture(mbf_axis);
 
% Programatically press the Feedback and tune button on each system
% and set the feedback gain to 0dB.
setup_operational_mode(mbf_axis, "Feedback")
% FIXME - remove hard coded paths.
lcaPut(['SR23C-DI-TMBF-01:',upper(mbf_axis),':FIR:GAIN_S', '0dB'])


