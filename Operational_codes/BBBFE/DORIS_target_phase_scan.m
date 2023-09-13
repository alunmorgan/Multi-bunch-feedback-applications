function data = DORIS_target_phase_scan(single_bunch_location)
% Scans the phase of the DORIS unit upstream of the MBF frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      single_bunch_location (int): the location of the single bunch.
%
% Machine setup: (manual for the time being...)
% fill some charge in bunch 1 (0.2nC)
%
% Example: DORIS_target_phase_scan(400)

BBBFE_detector_setup('X', single_bunch_location)
BBBFE_detector_setup('Y', single_bunch_location)
[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

% getting general environment data.
tunes.x_tune=NaN;
tunes.y_tune=NaN;
tunes.s_tune=NaN;
data = machine_environment('tunes', tunes);
data.time = datevec(datetime("now"));
data.base_name = 'doris_phase_scan';

data.mbf_pv_x = pv_names.hardware_names.x;
data.mbf_pv_y = pv_names.hardware_names.y;
data.doris_pv = pv_names.doris.phase;
original_setting = lcaGet(data.doris_pv);

% moving to starting point in scan
lcaPut(data.doris_pv, -180)

% measurement
data.phase = [-180:5:180 160:-5:-180];
data.side1_x = NaN(length(data.phase), 1);
data.main_x = NaN(length(data.phase), 1);
data.side2_x = NaN(length(data.phase), 1);
data.side1_y = NaN(length(data.phase), 1);
data.main_y = NaN(length(data.phase), 1);
data.side2_y = NaN(length(data.phase), 1);
for dbf = 1:length(data.phase)
    lcaPut(data.doris_pv, data.phase(dbf))
    pause(2)
    data.side1_x(dbf) = max(lcaGet([data.mbf_pv_x, pv_names.tails.Detector.det1.power]));
    data.main_x(dbf) = max(lcaGet([data.mbf_pv_x, pv_names.tails.Detector.det2.power]));
    data.side2_x(dbf) = max(lcaGet([data.mbf_pv_x, pv_names.tails.Detector.det3.power]));
    data.side1_x(dbf) = max(lcaGet([data.mbf_pv_y, pv_names.tails.Detector.det1.power]));
    data.main_x(dbf) = max(lcaGet([data.mbf_pv_y, pv_names.tails.Detector.det2.power]));
    data.side2_x(dbf) = max(lcaGet([data.mbf_pv_y, pv_names.tails.Detector.det3.power]));
end %for

% move back to the original setting
lcaPut(data.doris_pv, original_setting)

BBBFE_detector_restore('X')
BBBFE_detector_restore('Y')

%% saving the data to a file
save_to_archive(root_string, data)
%% plotting
DORIS_phase_scan_plotting(data)
