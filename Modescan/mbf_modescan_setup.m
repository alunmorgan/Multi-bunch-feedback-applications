function mbf_modescan_setup(mbf_axis, tune, varargin)
% Sets up the MBF system to be ready for a modescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Tune of the machine.
%
% example: mbf_modescan_setup('x', 0.17)

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
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
addRequired(p, 'mbf_axis');
addRequired(p, 'tune', valid_number);
addParameter(p, 'dwell', default_dwell, valid_number);
addParameter(p, 'detector_gain', default_detector_gain, valid_number);
addParameter(p, 'sequencer_gain', default_sequencer_gain, valid_number);
addParameter(p, 'excitation_level', default_excitation_level, valid_number);

parse(p, mbf_axis, tune, varargin{:});
settings = p.Results;

[~, harmonic_number, pv_names] = mbf_system_config;
Sequencer = pv_names.tails.Sequencer;

% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);

% state 1
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.start_frequency], tune);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.step_frequency],1);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.count], harmonic_number -1);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.holdoff], 0);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.dwell], settings.dwell);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.bank_select], 'Bank 1');
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.capture_state], 'Capture');
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.windowing_state], 'Disabled');
lcaPut([pv_head, Sequencer.Base, ':1',Sequencer.gaindb], -30);
lcaPut([pv_head, Sequencer.Base, ':1', Sequencer.blanking_state], 'Off');
