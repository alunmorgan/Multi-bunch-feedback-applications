function growthrates = growthrates_all(mbf_axis, varargin)
% Top level function to run the growth rates measurements on the
% selected plane
%   Args:
%       mbf_axis(str): 'x','y', or 's'
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%       is yes.
%       tunes (structure or NaN): Tune data from a previous measurement. 
%                                 Defaults to Nan.
%   Returns:
%       growthrates(structure): The data captured from all the relevant systems.
%
% Example: growthrates = growthrates_all('x')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

default_plotting = 'yes';
default_auto_setup = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;

[tunes, orig_fir_gain] = mbf_growthrates_setup(mbf_axis, ...
    'auto_setup', p.Results.auto_setup, 'tunes', p.Results.tunes);
growthrates = mbf_growthrates_capture(mbf_axis, 'tunes', tunes);

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the Feedback and tune button on each system
    % and set the feedback gain to the operational value.
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)
end %if

if strcmp(p.Results.plotting, 'yes')
    [poly_data, frequency_shifts] = mbf_growthrates_analysis(growthrates);
    mbf_growthrates_plot_summary(poly_data, frequency_shifts, growthrates, ...
        'outputs', 'both')
end %if