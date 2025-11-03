function mbf_checkout_setup(mbf_axis, varargin)
% Sets the MBF system specified to have the desired signals passing
% through the system.
%
% Example: mbf_checkout_setup('x')

mbf_p = inputParser;
mbf_p.StructExpand = false;
mbf_p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

addRequired(mbf_p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(mbf_p, 'tune', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'nco1', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'nco2', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'loopback', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'fir', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'fir_gain', '-42dB');
addParameter(mbf_p, 'nco1_gain', '-36dB');
addParameter(mbf_p, 'nco2_gain', '-36dB');
addParameter(mbf_p, 'tune_gain', '-42dB');

% parse(p, mbf_axis);
parse(mbf_p, mbf_axis, varargin{:});

