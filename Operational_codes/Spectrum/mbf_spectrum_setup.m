function tunes = mbf_spectrum_setup(mbf_axis,  varargin)
% sets up the hardware ready to capture data for a spectrum.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       tunes (structure or NaN): Tune data from a previous measurement. 
%                                 Defaults to Nan.
%
% Example mbf_spectrum_setup('x')

default_auto_setup = 'yes';

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'mbf_axis');
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

mbf_tools
[~, ~, pv_names, trigger_inputs] = mbf_system_config;

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

if isnan(p.Results.tunes)
% Get the tunes
tunes = get_all_tunes('xys');
else
    tunes = p.Results.tunes;
end %if

% Disarm the sequencer and memory triggers
lcaPut([pv_names.hardware_names.(mbf_axis) pv_names.tails.triggers.SEQ.disarm], 1)
lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.disarm], 1)

for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).enable_status], 'Ignore');
    lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).blanking_status], 'All');

end %for
% Set the trigger to one shot
lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.mode], 'One Shot');

% Set the triggering to External only
lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.('EXT').enable_status], 'Enable')

%  set up the memory buffer to capture ADC data.
lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.MEM.channel_select], 'ADC0/ADC1')