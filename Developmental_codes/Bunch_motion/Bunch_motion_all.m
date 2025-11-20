function Bunch_motion_all
mbf_tools

% % Programatiaclly press the tune only button on each system.
% setup_operational_mode("x", "TuneOnly")
% setup_operational_mode("y", "TuneOnly")
% setup_operational_mode("s", "TuneOnly")

mbf_bunch_motion_setup
bunch_motion = mbf_bunch_motion_capture;
% mbf_bunch_motion_plotting(bunch_motion)
% 
% figure
% plot(reshape(bunch_motion.y, 936, []))
% figure
% imagesc(reshape(bunch_motion.y, 936, []))
