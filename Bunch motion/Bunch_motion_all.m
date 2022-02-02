function Bunch_motion_all
mbf_tools

% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode("x", "TuneOnly")
setup_operational_mode("y", "TuneOnly")
setup_operational_mode("s", "TuneOnly")

mbf_bunch_motion_setup
bunch_motion = mbf_bunch_motion_capture;
mbf_bunch_motion_plotting(bunch_motion)