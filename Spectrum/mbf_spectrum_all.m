function mbf_spectrum_all
% Top level function to run all spectral measurements of each plane
% sequentially.

mbf_tools

% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode("x", "TuneOnly")
setup_operational_mode("y", "TuneOnly")
setup_operational_mode("s", "TuneOnly")
mbf_axes = {'x', 'y', 's'};

for tk = 1:length(mbf_axes)
 mbf_spectrum_setup(mbf_axes{tk})
 data = mbf_spectrum_capture(mbf_axes{tk}, n_turns, repeat);
 analysed_data = mbf_spectrum_analysis(data, fold);
 mbf_spectrum_plotting(analysed_data, data.meta_data)
end %for

% Programatiaclly press the tune only button on each system
setup_operational_mode("x", "TuneOnly")
setup_operational_mode("y", "TuneOnly")
setup_operational_mode("s", "TuneOnly")