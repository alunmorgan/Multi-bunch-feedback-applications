function BBBFE_detector_setup(mbf_axis, single_bunch_location)

mbf_axis = lower(mbf_axis);
[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

% press tune only
setup_operational_mode(mbf_axis, "TuneOnly")
if single_bunch_location == 0
    prior_bunch = 935;
else
    prior_bunch = single_bunch_location -1;
end %if
    
% set up the individual tune detectors to run on 1,2,3

set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.enable], 1)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.scale], 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.bunch_select] ,'0:935');
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.reset_selection] ,1);
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.bunch_select], num2str(prior_bunch));
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det1.set_selection], 1);

set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.enable], 1)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.scale], 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.bunch_select], '0:935');
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.reset_selection], 1);
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.bunch_select], num2str(single_bunch_location));
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det2.set_selection], 1);

set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.enable], 1)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.scale], 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.bunch_select], '0:935');
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.reset_selection], 1);
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.bunch_select], num2str(single_bunch_location +1));
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det3.set_selection], 1);

% set sweep gain to -18
set_variable([mbf_names.(mbf_axis), pv_names.tails.Sequencer.seq1.gaindb], '-18');
% set detector fixed gain