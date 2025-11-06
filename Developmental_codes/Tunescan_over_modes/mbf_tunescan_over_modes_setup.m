function mbf_tunescan_over_modes_setup(mbf_axis, exp_setup)
% Sets up the MBF system to be ready for a tunescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       exp_setup (struct): Contains all the setup parameters.
%
% example: mbf_tunescan_over_modes_setup('x', exp_setup)

mbf_tools
if strcmp(exp_setup.feedback_state, 'on')
    fb_on_off =1;
else
    fb_on_off =0;
end %if
[~, harmonic_number, pv_names] = mbf_system_config;
Detector = pv_names.tails.Detector;
Sequencer1 = pv_names.tails.Sequencer.seq1;
Bunch_bank1 = pv_names.tails.Bunch_bank.bank1;

% Generate the base PV name.
system_axis = pv_names.hardware_names.(mbf_axis);

% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode(mbf_axis, "TuneOnly")

detect_bunch = exp_setup.drive_bunches;

% Only sweep selected bunch
drive_wf = zeros(1, harmonic_number);
drive_wf(exp_setup.drive_bunches + 1) = 1;

% chose which bunches to monitor the response
detect_wf_1 = zeros(1,harmonic_number);
detect_wf_1(sort(mod(detect_bunch + 0, harmonic_number)+1)) = 1;
detect_wf_2 = zeros(1,harmonic_number);
detect_wf_2(sort(mod(detect_bunch + 1, harmonic_number)+1)) = 1;
detect_wf_3 = zeros(1,harmonic_number);
detect_wf_3(sort(mod(detect_bunch + 2, harmonic_number)+1)) = 1;

% write to the TMBF on which bunches to perform the sweep
set_variable([system_axis Bunch_bank1.SEQ.enablewf], drive_wf);

% Configure FIR enable (whether feedback is on or off)
set_variable([system_axis Bunch_bank1.FIR.enablewf], fb_on_off * ones(1,harmonic_number));

% Detector 0 grabs everything
set_variable([system_axis Detector.det0.bunch_selection], ones(1,harmonic_number));
set_variable([system_axis Detector.det0.enable], 'Enabled');

% Detector 1 only observes active bunches
set_variable([system_axis Detector.det1.bunch_selection], detect_wf_1);
set_variable([system_axis Detector.det1.enable], 'Enabled');

% Detector 2 only observes 1 bunch behind driven bunches
set_variable([system_axis Detector.det2.bunch_selection], detect_wf_2);
set_variable([system_axis Detector.det2.enable], 'Enabled');

% Detector 3 only observes 2 bunches behind driven bunches
set_variable([system_axis Detector.det3.bunch_selection], detect_wf_3);
set_variable([system_axis Detector.det3.enable], 'Enabled');

% arm the TMBF as one-shot rather than continuous
set_variable([system_axis pv_names.tails.triggers.mode],'One Shot')
set_variable([system_axis pv_names.tails.Sequencer.reset],1)

% set the super-sequencer to have the correct number of modes
set_variable([system_axis pv_names.tails.Super_sequencer_reset],1)
set_variable([system_axis pv_names.tails.Super_sequencer_count],harmonic_number)

% change the number of captures to speed things up (normally 4096)
set_variable([system_axis Sequencer1.count],exp_setup.n_captures)

% select the tune sweep frequency / mode
set_variable([system_axis Sequencer1.start_frequency],exp_setup.start_mode + exp_setup.start_frequency)
set_variable([system_axis Sequencer1.end_frequency],  exp_setup.start_mode + exp_setup.end_frequency)