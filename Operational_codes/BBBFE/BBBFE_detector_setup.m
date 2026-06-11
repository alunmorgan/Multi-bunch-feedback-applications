function detector_setup = BBBFE_detector_setup(mbf_axis, single_bunch_location)

[~, ~, pv_names] = mbf_system_config;
mbf_names = pv_names.hardware_names;
detector = pv_names.tails.Detector;


if single_bunch_location == 0
    prior_bunch = 935;
else
    prior_bunch = single_bunch_location -1;
end %if
    
% read the existing detector states
for ms = 1:3
    detector_setup.(['det', num2str(ms)]).enable = ...
        get_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).enable]);
    detector_setup.(['det', num2str(ms)]).scale = ...
    get_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).scale]);
    detector_setup.(['det', num2str(ms)]).bunch_select = ...
    get_variable([mbf_names.(mbf_axis), detector.(['det', num2str(ms)]).bunch_select]);
end %for

% set up the individual tune detectors to run on 1,2,3

set_variable([mbf_names.(mbf_axis), detector.det1.enable], 1)
set_variable([mbf_names.(mbf_axis), detector.det1.scale], 0)
set_variable([mbf_names.(mbf_axis), detector.det1.bunch_select] ,'0:935');
set_variable([mbf_names.(mbf_axis), detector.det1.reset_selection] ,1);
set_variable([mbf_names.(mbf_axis), detector.det1.bunch_select], num2str(prior_bunch));
set_variable([mbf_names.(mbf_axis), detector.det1.set_selection], 1);

set_variable([mbf_names.(mbf_axis), detector.det2.enable], 1)
set_variable([mbf_names.(mbf_axis), detector.det2.scale], 0)
set_variable([mbf_names.(mbf_axis), detector.det2.bunch_select], '0:935');
set_variable([mbf_names.(mbf_axis), detector.det2.reset_selection], 1);
set_variable([mbf_names.(mbf_axis), detector.det2.bunch_select], num2str(single_bunch_location));
set_variable([mbf_names.(mbf_axis), detector.det2.set_selection], 1);

set_variable([mbf_names.(mbf_axis), detector.det3.enable], 1)
set_variable([mbf_names.(mbf_axis), detector.det3.scale], 0)
set_variable([mbf_names.(mbf_axis), detector.det3.bunch_select], '0:935');
set_variable([mbf_names.(mbf_axis), detector.det3.reset_selection], 1);
set_variable([mbf_names.(mbf_axis), detector.det3.bunch_select], num2str(single_bunch_location +1));
set_variable([mbf_names.(mbf_axis), detector.det3.set_selection], 1);

% set sweep gain to -18
set_variable([mbf_names.(mbf_axis), pv_names.tails.Sequencer.seq1.gaindb], '-18');
% set detector fixed gain