function Bunch_motion_all(varargin)

[root_string, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
mbf_tools
% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);

parse(p, varargin{:});

% getting general environment data
bunch_motion = machine_environment;

% Add the extra data to the data structure.
bunch_motion.base_name = 'Bunch_motion';
bunch_motion.harmonic_number = harmonic_number;

if strcmp(p.Results.auto_setup, 'yes')
    % Get the current FIR gains
    orig_fir_gain_x = get_variable([pv_names.hardware_names.('x'), Bunch_bank.FIR_gains]);
    orig_fir_gain_y = get_variable([pv_names.hardware_names.('y'), Bunch_bank.FIR_gains]);
    orig_fir_gain_s = get_variable([pv_names.hardware_names.('s'), Bunch_bank.FIR_gains]);

    % Programatically press the tune only button on each system.
    setup_operational_mode('x', "TuneOnly")
    setup_operational_mode('y', "TuneOnly")
    setup_operational_mode('s', "TuneOnly")
end %if

bunch_motion.mbf_state_x = get_operational_mode('x');
bunch_motion.mbf_state_y = get_operational_mode('y');
bunch_motion.mbf_state_s = get_operational_mode('s');

mbf_bunch_motion_setup(pv_names, trigger_inputs)
captured_data = mbf_bunch_motion_capture(pv_names);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    bunch_motion.(data_fields{je}) = captured_data.(data_fields{je});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode('x', "Feedback")
    set_variable([pv_names.hardware_names.('x'), Bunch_bank.FIR_gains], orig_fir_gain_x)
        setup_operational_mode('y', "Feedback")
    set_variable([pv_names.hardware_names.('y'), Bunch_bank.FIR_gains], orig_fir_gain_y)
        setup_operational_mode('s', "Feedback")
    set_variable([pv_names.hardware_names.('s'), Bunch_bank.FIR_gains], orig_fir_gain_s)
end %if

%% saving the data to a file
save_to_archive(root_string, bunch_motion)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, bunch_motion)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_bunch_motion_archival_retrieval([bunch_motion.time bunch_motion.time],...
        filter_conditions)
end %if
