function modescan_all(mbf_axis, varargin)
% Top level function to run the modescan for all selected plane.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the
%                                      main archive.
%       n_repeats(int): How many times to repeat each measurement point.
%       dwell (int): How many turns to stay at each measurement point.
%       excitation_gain(float): level of the excitation.
%
% Example  modscan_all('x')

[root_string, harmonic_number, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;

% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);
valid_positive_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'n_repeats', 10, valid_positive_number);
addParameter(p, 'dwell', 500, valid_positive_number);
addParameter(p, 'excitation_gain', -30, validScalarNum);

parse(p, mbf_axis, varargin{:});

% getting general environment data
modescan = machine_environment;

% Add the extra data to the data structure.
modescan.ax_label = mbf_axis;
modescan.base_name = ['Modescan_' mbf_axis '_axis'];
modescan.harmonic_number = harmonic_number;
modescan.n_repeats = p.Results.n_repeats;
modescan.dwell = p.Results.dwell;
modescan.excitation_gain = p.Results.excitation_gain;

if strcmp(p.Results.auto_setup, 'yes')
    % Get the current FIR gain
    orig_fir_gain = get_variable([pv_head, Bunch_bank.bank1.FIR.gainwf]);
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

modescan.mbf_state = get_operational_mode(mbf_axis);

% Setup the MBF ready for the measurement.
mbf_modescan_setup(mbf_axis, pv_names, harmonic_number, p.Results.dwell, ...
    modescan.tunes.([mbf_axis,'_tune']).tune,...
    p.Results.excitation_gain)
pause(2)

% Capturing data.
captured_data = mbf_modescan_capture(mbf_axis, pv_names, p.Results.n_repeats);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    modescan.(data_fields{je}) = captured_data.(data_fields{je});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.bank1.FIR.gainwf], orig_fir_gain)
end %if

%% saving the data to a file
save_to_archive(root_string, modescan)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, modescan)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_modescan_archival_retrieval(mbf_axis, [modescan.time, modescan.time],...
        filter_conditions)
end %if

