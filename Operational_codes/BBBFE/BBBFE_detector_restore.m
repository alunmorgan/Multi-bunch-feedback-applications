function BBBFE_detector_restore(mbf_axis, detector_setup)

mbf_axis = lower(mbf_axis);
[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
detector = pv_names.tails.Detector;
% set up the individual tune detectors to run on 1,2,3

for ms = 1:3
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).enable],...
        detector_setup.(['det', num2str(ms)]).enable)
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).scale],...
        detector_setup.(['det', num2str(ms)]).scale)
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).bunch_select] ,'0:935');
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).reset_selection] ,1);
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).bunch_select],...
        num2str(detector_setup.(['det', num2str(ms)]).bunch_select));
    set_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).set_selection], 1);
end %for

