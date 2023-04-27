function configure_tune_sweep(axis, drive_bunch, fb_on_off, d0flag, d1flag, d2flag, d3flag)

% drive_bunch = 0:2:935;    % starts at 0
% drive_bunch = 123;
% fb_on_off = 1;      % 0 => off, 1 => on

detect_bunch = drive_bunch;

% Only sweep selected bunch
drive_wf = zeros(1, 936);
drive_wf(drive_bunch + 1) = 1;

% chose which bunches to monitor the response
detect_wf_1 = zeros(1,936);
detect_wf_1(sort(mod(detect_bunch + 0,936)+1)) = 1;
detect_wf_2 = zeros(1,936);
detect_wf_2(sort(mod(detect_bunch + 1,936)+1)) = 1;
detect_wf_3 = zeros(1,936);
detect_wf_3(sort(mod(detect_bunch + 2,936)+1)) = 1;

% write to the TMBF on which bunches to perform the sweep
lcaPut(['SR23C-DI-TMBF-01:' axis ':BUN:1:SEQ:ENABLE_S'], drive_wf);

% Configure FIR enable (whether feedback is on or off)
lcaPut(['SR23C-DI-TMBF-01:' axis ':BUN:1:FIR:ENABLE_S'], fb_on_off * ones(1,936));

% Detector 0 grabs everything
if d0flag
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:0:BUNCHES_S'], ones(1,936));
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:0:ENABLE_S'], 'Enabled');
else
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:0:ENABLE_S'], 'Disabled');
end

% Detector 1 only observes active bunches
if d1flag
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:1:BUNCHES_S'], detect_wf_1);
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:1:ENABLE_S'], 'Enabled');
else
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:1:ENABLE_S'], 'Disabled');
end

% Detector 2 only observes 1 bunch behind driven bunches
if d2flag
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:2:BUNCHES_S'], detect_wf_2);
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:2:ENABLE_S'], 'Enabled');
else
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:2:ENABLE_S'], 'Disabled');
end

% Detector 3 only observes 2 bunches behind driven bunches
if d3flag
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:3:BUNCHES_S'], detect_wf_3);
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:3:ENABLE_S'], 'Enabled');
else
    lcaPut(['SR23C-DI-TMBF-01:' axis ':DET:3:ENABLE_S'], 'Disabled');
end
