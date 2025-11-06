function tunes = mbf_modescan_setup(mbf_axis, varargin)
% Sets up the MBF system to be ready for a modescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       tunes (structure or NaN): Tune data from a previous measurement.
%                                 Defaults to Nan.
%   Returns:
%       tunes (structure): Tunes of the machine.
%
% example: mbf_modescan_setup('x')

if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y')
    default_dwell = 500;
    default_detector_gain = -12; % detector gain in dB.
    default_sequencer_gain = -36; % sequencer gain in dB.
    default_excitation_level = -12; % excitation level in dB.
elseif strcmpi(mbf_axis, 's')
    default_dwell = 500;
    default_detector_gain = -12; % detector gain in dB.
    default_sequencer_gain = -36; % sequencer gain in dB.
    default_excitation_level = -12; % excitation level in dB.
end %if

boolean_string = {'yes', 'no'};

default_auto_setup = 'yes';

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'dwell', default_dwell, valid_number);
addParameter(p, 'detector_gain', default_detector_gain, valid_number);
addParameter(p, 'sequencer_gain', default_sequencer_gain, valid_number);
addParameter(p, 'excitation_level', default_excitation_level, valid_number);
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

if strcmp(p.Results.auto_setup, 'yes')
    % Programatiaclly press the tune only button on each system
    % then get the tunes
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

if isstruct(p.Results.tunes)
    tunes = p.Results.tunes;
else
    % Get the tunes
    tunes = get_all_tunes;
end %if
tune = tunes.([mbf_axis,'_tune']).tune;

if isnan(tune)
    disp('Could not get tune value')
    return
end %if

mbf_tools
[~, harmonic_number, pv_names] = mbf_system_config;
% Generate the base PV name.
system_axis = pv_names.hardware_names.(mbf_axis);
% state 1 of sequencer
seq = pv_names.tails.Sequencer.seq1;

set_variable([system_axis seq.start_frequency], tune);
set_variable([system_axis seq.step_frequency],1);
set_variable([system_axis seq.count], harmonic_number -1);
set_variable([system_axis seq.holdoff], 0);
set_variable([system_axis seq.dwell], p.Results.dwell);
set_variable([system_axis seq.bank_select], 'Bank 1');
set_variable([system_axis seq.capture_state], 'Capture');
set_variable([system_axis seq.windowing_state], 'Disabled');
set_variable([system_axis seq.gaindb], -30);
set_variable([system_axis seq.blanking_state], 'Off');
