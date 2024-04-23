function BBBFE_detector_restore(mbf_axis)

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;  
% set up the individual tune detectors to run on 1,2,3

set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.enable], 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.enable], 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.enable], 0)

% press tune only
setup_operational_mode(mbf_axis, "TuneOnly")