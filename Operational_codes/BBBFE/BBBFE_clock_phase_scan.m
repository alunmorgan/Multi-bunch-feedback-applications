function BBBFE_clock_phase_scan(mbf_ax, single_bunch_location)
% Scans one of the clock phase shifts in the bunch by bunch frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      ax (str): Specifies which axis.
%      single_bunch_location (int): the location of the single bunch.
%
% Machine setup: (manual for the time being...)
% fill some charge in bunch 1 (0.2nC)
%
% Example: BBBFE_clock_phase_scan('X', 400)

[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
mbf_ax = lower(mbf_ax);
orig_gain = get_variable([pv_names.hardware_names.(mbf_ax), pv_names.tails.Sequencer.seq1.gaindb]);
BBBFE_detector_setup(mbf_ax, single_bunch_location)

% getting general environment data.
tunes.x_tune=NaN;
tunes.y_tune=NaN;
tunes.s_tune=NaN;
data = machine_environment('tunes', tunes);
data.time = datevec(datetime("now"));
data.base_name = ['clock_phase_scan_', mbf_ax, '_axis'];

if strcmpi(mbf_ax, 'Y')
    mbf_pv = pv_names.hardware_names.y;
    fe_phase_pv = [pv_names.frontend.base pv_names.frontend.clock_phase.y];
elseif strcmpi(mbf_ax, 'X')
    mbf_pv = pv_names.hardware_names.x;
    fe_phase_pv = [pv_names.frontend.base pv_names.frontend.clock_phase.x];
elseif strcmpi(mbf_ax, 'S')
    mbf_pv = pv_names.hardware_names.s;
    fe_phase_pv = [pv_names.frontend.base pv_names.frontend.clock_phase.s];
else
    error('BBBFE:axiserror','Please use input axes X, Y or S')
end %if

original_setting = get_variable(fe_phase_pv);

% moving to starting point in scan
for pp = original_setting:-20:-180
    set_variable(fe_phase_pv, pp)
    pause(.5)
end %for

% measurement
data.phase = [-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase), 1);
data.main = NaN(length(data.phase), 1);
data.side2 = NaN(length(data.phase), 1);
data.adc_phase = NaN(length(data.phase), 1);

for x = 1:length(data.phase)
    set_variable(fe_phase_pv, data.phase(x))
    pause(2)
    data.side1(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det1.power]));
    data.main(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det2.power]));
    data.side2(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det3.power]));
    if strcmpi(mbf_ax, 'S')
        data.adc_phase(x) = max(get_variable([mbf_pv, pv_names.tails.adc.phase.mean]));
    end %if
end %for

% move back to the original setting
for pp = -180:20:original_setting
    set_variable(fe_phase_pv, pp)
    pause(.5)
end %for

BBBFE_detector_restore(mbf_ax)
set_variable([pv_names.hardware_names.(mbf_ax), pv_names.tails.Sequencer.seq1.gaindb], orig_gain);

%% saving the data to a file
save_to_archive(root_string, data)
%% plotting
BBBFE_clock_phase_scan_plotting( mbf_ax, data)
