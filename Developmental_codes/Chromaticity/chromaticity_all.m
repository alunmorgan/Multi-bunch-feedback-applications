function chromaticity_all(mbf_axis, varargin)
% Top level function to run the chromaticity for selected plane.
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
%
% Example  chromaticity_all('x')

[root_string, harmonic_number, pv_names] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
valid_positive_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'n_repeats', 10, valid_positive_number);
addParameter(p, 'n_trys', 5, valid_positive_number);
addParameter(p, 'with_measchro', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, mbf_axis, varargin{:});

% getting general environment data
chromaticity = machine_environment;

% Add the extra data to the data structure.
chromaticity.ax_label = mbf_axis;
chromaticity.base_name = ['chromaticity_' mbf_axis '_axis'];
chromaticity.harmonic_number = harmonic_number;

input_fields = fieldnames(p.Results);
for jltf = 1:length(input_fields)
    chromaticity.(input_fields{jltf}) = p.Results.(input_fields{jltf});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

chromaticity.mbf_state = get_operational_mode(mbf_axis);

% Capturing data.
captured_data = mbf_modescan_capture(chromaticity, pv_names);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    chromaticity.(data_fields{je}) = captured_data.(data_fields{je});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, ':FIR:GAIN_S'], chromaticity.fir_gain)
else
    reestablish_tune_measurement(mbf_axis)
end %if

disp(['Chromaticity for ', mbf_axis, ' is ', num2str(chromaticity.mean),...
    ' with an uncertainty of ', num2str(chromaticity.std)])

if strcmp(p.Results.with_measchro, 'yes')
    [chro_temp, ~] = measchro;
    if strcmpi(mbf_axis, 'x')
        chromaticity.measchro = chro_temp(1);
        disp('measchro returns ', chromaticity.measchro)
    elseif strcmpi(mbf_axis, 'y')
        chromaticity.measchro = chro_temp(2);
        disp('measchro returns ', chromaticity.measchro)
    else
        disp('measchro only returns data for x and y')
    end %if
end %if

%% saving the data to a file
save_to_archive(root_string, chromaticity)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, chromaticity)
end %if

