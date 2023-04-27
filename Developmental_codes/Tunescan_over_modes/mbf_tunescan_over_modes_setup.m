function mbf_tunescan_over_modes_setup(mbf_axis, varargin)
% Sets up the MBF system to be ready for a tunescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       drive_bunch = 0:2:935;    % starts at 0
%       drive_bunch = 123;
%       fb_on_off = 1;      % 0 => off, 1 => on
% 
% example: mbf_tunescan_over_modes_setup('x')

if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y')
    default_drive_bunches = 123;
    default_fb_on_off = 1;
elseif strcmpi(mbf_axis, 's')
    default_drive_bunches = 123;
    default_fb_on_off = 1;
end %if
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'drive_bunches', default_drive_bunches);
addParameter(p, 'fb_on_off', default_fb_on_off, valid_number);
addParameter(p, 'start_mode', default_fb_on_off, valid_number);
addParameter(p, 'start_frequency', default_fb_on_off, valid_number);
addParameter(p, 'end_frequency', default_fb_on_off, valid_number);
addParameter(p, 'n_captures', default_fb_on_off, valid_number);

parse(p, mbf_axis, varargin{:});

mbf_tools

[~, harmonic_number, pv_names] = mbf_system_config;
Detector = pv_names.tails.Detector;
Sequencer = pv_names.tails.Sequencer;
Bunch_bank = pv_names.tails.Bunch_bank;

% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);

% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode(mbf_axis, "TuneOnly")

detect_bunch = drive_bunches;

% Only sweep selected bunch
drive_wf = zeros(1, harmonic_number);
drive_wf(drive_bunches + 1) = 1;

% chose which bunches to monitor the response
detect_wf_1 = zeros(1,936);
detect_wf_1(sort(mod(detect_bunch + 0, harmonic_number)+1)) = 1;
detect_wf_2 = zeros(1,936);
detect_wf_2(sort(mod(detect_bunch + 1, harmonic_number)+1)) = 1;
detect_wf_3 = zeros(1,936);
detect_wf_3(sort(mod(detect_bunch + 2, harmonic_number)+1)) = 1;

% write to the TMBF on which bunches to perform the sweep
lcaPut([pv_head ':BUN:1' Bunch_bank.SEQ_enable], drive_wf);

% Configure FIR enable (whether feedback is on or off)
lcaPut([pv_head ':BUN:1' Bunch_bank.FIR_enable], fb_on_off * ones(1,harmonic_number));

% Detector 0 grabs everything
lcaPut([pv_head Detector.det0.bunch_selection], ones(1,harmonic_number));
lcaPut([pv_head Detector.det0.enable], 'Enabled');

% Detector 1 only observes active bunches
lcaPut([pv_head Detector.det1.bunch_selection], detect_wf_1);
lcaPut([pv_head Detector.det1.enable], 'Enabled');

% Detector 2 only observes 1 bunch behind driven bunches
lcaPut([pv_head Detector.det2.bunch_selection], detect_wf_2);
lcaPut([pv_head Detector.det2.enable], 'Enabled');

% Detector 3 only observes 2 bunches behind driven bunches
lcaPut([pv_head Detector.det3.bunch_selection], detect_wf_3);
lcaPut([pv_head Detector.det3.enable], 'Enabled');

% arm the TMBF as one-shot rather than continuous
lcaPut([pv_head pv_names.tails.triggers.mode],'One Shot')
lcaPut([pv_head Sequencer.Base Sequencer.reset],1)

% set the super-sequencer to have the correct number of modes
lcaPut([pv_head pv_names.tails.Super_sequencer_reset],1)
lcaPut([pv_head pv_names.tails.Super_sequencer_count],harmonic_number)

% change the number of captures to speed things up (normally 4096)
lcaPut([pv_head Sequencer.Base ':1', Sequencer.count],p.Results.n_captures)

% select the tune sweep frequency / mode
lcaPut([pv_head Sequencer.Base ':1', Sequencer.start_frequency],p.Results.start_mode + p.Results.start_frequency)
lcaPut([pv_head Sequencer.Base ':1', Sequencer.end_frequency],  p.Results.start_mode + p.Results.end_frequency)