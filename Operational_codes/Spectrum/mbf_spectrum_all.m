function mbf_spectrum_all(mbf_axis, varargin)
% Top level function to run all spectral measurements on selected plane.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the 
%                                      main archive.
%       n_turns (int): number of turns to capture. Default is 1000.
%       repeat (int): Number of repeat points. Default is 1.
%
% Example mbf_spectrum_all

[root_string, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;

% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};
axis_string = {'x', 'y', 's'};
valid_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'n_turns', 1000, valid_number);
addParameter(p, 'repeat', 1, valid_number);


parse(p, mbf_axis, varargin{:});

% getting general environment data.
spectrum = machine_environment;

% Add the extra data to the data structure.
spectrum.ax_label = mbf_axis;
spectrum.base_name = ['Spectrum_',mbf_axis '_axis'];
spectrum.harmonic_number = harmonic_number;
spectrum.n_turns = p.Results.n_turns;
spectrum.repeat = p.Results.repeat;
spectrum.time = datevec(datetime("now"));


if  strcmp(p.Results.auto_setup, 'yes')
            % Get the current FIR gain
    orig_fir_gain = get_variable([pv_head, Bunch_bank.FIR_gains]);
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

spectrum.mbf_state = get_operational_mode(mbf_axis);

mbf_spectrum_setup(mbf_axis, pv_names, trigger_inputs);

spectrum.raw_data  = mbf_spectrum_capture(mbf_axis, pv_names, p.Results.n_turns,...
    p.Results.repeat);

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)
end %if

%% saving the data to a file
save_to_archive(root_string, spectrum)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, spectrum)
end %if

if strcmp(p.Results.plotting, 'yes')
    mbf_spectra_archival_retrieval(mbf_axis, [spectrum.time spectrum.time],...
        filter_conditions)
end %if