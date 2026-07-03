function configure_tune_sweep(mbf_axis, drive_bunch, fb_on_off, d0flag, d1flag, d2flag, d3flag)

% drive_bunch = 0:2:935;    % starts at 0
% drive_bunch = 123;
% fb_on_off = 1;      % 0 => off, 1 => on

[~, harmonic_number, pv_names, ~] = mbf_system_config;
head = pv_names.hardware_names.(mbf_axis);
bank1 = pv_names.tails.Bunch_bank.("bank1");
detectors = pv_names.tails.Detector;

detect_bunch = drive_bunch;

% Only sweep selected bunch
drive_wf = zeros(1, harmonic_number);
drive_wf(drive_bunch + 1) = 1;

% chose which bunches to monitor the response
detect_wf_1 = zeros(1,harmonic_number);
detect_wf_1(sort(mod(detect_bunch + 0,harmonic_number)+1)) = 1;
detect_wf_2 = zeros(1,harmonic_number);
detect_wf_2(sort(mod(detect_bunch + 1,harmonic_number)+1)) = 1;
detect_wf_3 = zeros(1,harmonic_number);
detect_wf_3(sort(mod(detect_bunch + 2,harmonic_number)+1)) = 1;

% write to the TMBF on which bunches to perform the sweep
set_variable([head, bank1.SEQ.enablewf], drive_wf);

% Configure FIR enable (whether feedback is on or off)
set_variable([head bank1.FIR.enablewf], fb_on_off * ones(1,harmonic_number));

% Detector 0 grabs everything
if d0flag
    set_variable([head, detectors.("det0").bunch_selection], ones(1,harmonic_number));
    set_variable([head, detectors.("det0").enable], 'Enabled');
else
    set_variable([head, detectors.("det0").enable], 'Disabled');
end

% Detector 1 only observes active bunches
if d1flag
    set_variable([head, detectors.("det1").bunch_selection], detect_wf_1);
    set_variable([head, detectors.("det1").enable], 'Enabled');
else
    set_variable([head, detectors.("det1").enable], 'Disabled');
end

% Detector 2 only observes 1 bunch behind driven bunches
if d2flag
    set_variable([head, detectors.("det2").bunch_selection], detect_wf_2);
    set_variable([head, detectors.("det2").enable], 'Enabled');
else
    set_variable([head, detectors.("det2").enable], 'Disabled');
end

% Detector 3 only observes 2 bunches behind driven bunches
if d3flag
    set_variable([head, detectors.("det3").bunch_selection], detect_wf_3);
    set_variable([head, detectors.("det3").enable], 'Enabled');
else
    set_variable([head, detectors.("det3").enable], 'Disabled');
end
