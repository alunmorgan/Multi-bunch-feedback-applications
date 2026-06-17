function BBBFE_detector_restore(mbf_axis, detector_setup)

mbf_axis = lower(mbf_axis);
[~, ~, pv_names] = mbf_system_config;
mbf_names = pv_names.hardware_names;
detector = pv_names.tails.Detector;
% set up the individual tune detectors to run on 1,2,3

for ms = 1:3
    det_name = ['det', num2str(ms)];
    set_variable([mbf_names.(mbf_axis), detector.(det_name).enable],...
        detector_setup.(det_name).enable)
    set_variable([mbf_names.(mbf_axis), detector.(det_name).scale],...
        detector_setup.(det_name).scale)
    set_variable([mbf_names.(mbf_axis), detector.(det_name).bunch_select] ,'0:935');
    set_variable([mbf_names.(mbf_axis), detector.(det_name).reset_selection] ,1);
    set_variable([mbf_names.(mbf_axis), detector.(det_name).bunch_select],...
        detector_setup.(det_name).bunch_select{1});
    set_variable([mbf_names.(mbf_axis), detector.(det_name).set_selection], 1);
end %for

