function tunescan_over_modes_all(mbf_axis, varargin)
% top level function to run the tunescan for all modes in the selected plane.


% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_axis_string = @(x) any(validatestring(x, {'x', 'y', 's'}));
valid_boolean_string = @(x) any(validatestring(x, {'yes', 'no'}));

addRequired(p, 'mbf_axis', valid_axis_string);
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', valid_boolean_string );
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'n_captures', 1001); % 1001 takes ~ 3 minutes
addParameter(p, 'start_mode', 0);
addParameter(p, 'drive_bunches', 0:935);
addParameter(p, 'feedback_state', 'on', valid_boolean_string );
addParameter(p, 'start_frequency', 0);
addParameter(p, 'end_frequency', 0.5);

parse(p, mbf_axis, varargin{:});

[root_string, harmonic_number, pv_names] = mbf_system_config;

pv_head = pv_names.hardware_names.(mbf_axis);

if strcmp(p.Results.auto_setup, 'yes')
% Programatically press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")
end %if

% getting general environment data
tunescan = machine_environment;

% Add the extra data to the data structure.
tunescan.ax_label = mbf_axis;
tunescan.base_name = ['tunescan_' tunescan.ax_label '_axis'];
tunescan.harmonic_number = harmonic_number;
input_fieldnames = fieldnames(p.Results);
for ns = 1: length(input_fieldnames)
    tunescan.(input_fieldnames{ns}) = p.Results.(input_fieldnames{ns});
end %for

mbf_tunescan_over_modes_setup(tunescan);
pause(2)
captured_data = mbf_tunescan_over_modes_capture(mbf_axis, pv_names);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    tunescan.(data_fields{je}) = captured_data.(data_fields{je});
end %for
% reset the sweep
%%%%Is this section needed or does the TuneOnly script take care of things?
configure_tune_sweep(mbf_axis , 0:harmonic_number -1, 1, 1, 0, 0, 0)
set_variable([pv_head pv_names.tails.triggers.mode],'Rearm')
set_variable([pv_head pv_names.tails.Sequencer.reset],1)
%%%%%%%

if strcmp(p.Results.auto_setup, 'yes')
% Programatically press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")
end %if

%% saving the data to a file
save_to_archive(root_string, tunescan)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, tunescan)
end %if

if strcmp(p.Results.plotting, 'yes')
    mbf_tunescan_over_modes_archival_retrieval(mbf_axis, [tunescan.time tunescan.time],...
        filter_conditions)
end %if

