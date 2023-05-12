function growdamp = growdamp_all(mbf_axis, varargin)
% Top level function to run the growdamp measurements on the
% selected plane
%   Args:
%       mbf_axis(str): 'x','y', or 's'
%   Returns:
%       growdamp(structure): The data captured from all the relevant systems.
%
% Example: growdamp = growdamp_all('x')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

default_plotting = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));

parse(p, mbf_axis);

[~, ~, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;

[tunes, orig_fir_gain] = mbf_growdamp_setup(mbf_axis);
growdamp = mbf_growdamp_capture(mbf_axis, 'tunes', tunes);

% Programatically press the Feedback and tune button on each system
% and set the feedback gain to the operational value.
setup_operational_mode(mbf_axis, "Feedback")

% Setting the FIR gain to its original value.
lcaPut([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)

if strcmp(p.Results.plotting, 'yes')
    [poly_data, frequency_shifts] = mbf_growdamp_analysis(growdamp);
    mbf_growdamp_plot_summary(poly_data, frequency_shifts, growdamp.data, ...
        'outputs', 'both')
end %if