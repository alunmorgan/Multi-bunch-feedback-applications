function modscan_all(x_tune, y_tune, s_tune)
% top level function to run the modescan for all planes sequentially.

% Ideally want to programatiaclly press the tune only button on each system
% then get the tunes
mbf_tools

mbf_modescan_setup('x', x_tune)
modescan_x = mbf_modescan_capture('x');
mbf_modescan_plotting(modescan_x)

mbf_modescan_setup('y', y_tune)
modescan_y = mbf_modescan_capture('y');
mbf_modescan_plotting(modescan_y)

mbf_modescan_setup('s', s_tune)
modescan_s = mbf_modescan_capture('s');
mbf_modescan_plotting(modescan_s)

% Ideally want to programatiaclly press the tune only button on each system