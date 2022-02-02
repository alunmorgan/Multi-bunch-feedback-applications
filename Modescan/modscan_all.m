function modscan_all
% top level function to run the modescan for all planes sequentially.

mbf_tools
% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode("x", "TuneOnly")
x_tune = lcaGet('SR23C-DI-TMBF-01:X:TUNE:TUNE');
setup_operational_mode("y", "TuneOnly")
y_tune =  lcaGet('SR23C-DI-TMBF-01:Y:TUNE:TUNE');
setup_operational_mode("s", "TuneOnly")
s_tune = lcaGet('SR23C-DI-LMBF-01:IQ:TUNE:TUNE');

mbf_modescan_setup('x', x_tune)
modescan_x = mbf_modescan_capture('x');
mbf_modescan_plotting(modescan_x)

mbf_modescan_setup('y', y_tune)
modescan_y = mbf_modescan_capture('y');
mbf_modescan_plotting(modescan_y)

mbf_modescan_setup('s', s_tune)
modescan_s = mbf_modescan_capture('s');
mbf_modescan_plotting(modescan_s)

% Programatiaclly press the tune only button on each system
setup_operational_mode("x", "TuneOnly")
setup_operational_mode("y", "TuneOnly")
setup_operational_mode("s", "TuneOnly")