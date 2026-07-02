function BBBFE_gain_scan(mbf_ax, varargin)
% Scans one of the individual axis gains in the
% bunch by bunch frontend and records the strength of the ADC signal.
% Restores the original value after the scan.
%
% Args:
%       mbf_axis(str): 'x','y', or 's'
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the
%                                      main archive.
%       sweep_start(int): level value to start the sweep.
%       sweep_step(int):  level step.
%       sweep_end(int):   level value to stop the sweep.
%
% Machine setup
% machien to nominal conditions
%
% Example: BBBFE_gain_scan('x')

[root_string, ~, pv_names] = mbf_system_config;
adc =  pv_names.tails.adc;
frontend = pv_names.frontend.base;
fe_gain = pv_names.frontend.gain;
sequencer1 = pv_names.tails.Sequencer.seq1;
mbf_pv = pv_names.hardware_names.(mbf_ax);
fe_gain_pv = [frontend fe_gain.(mbf_ax)];


% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = @(x) any(validatestring(x, {'yes', 'no'}));
axis_string =  @(x) any(validatestring(x,{'x', 'y', 's'}));
valid_bunch_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);
valid_number = @(x) isnumeric(x) && isscalar(x);

addRequired(p, 'mbf_axis', axis_string);
addRequired(p, 'single_bunch_location', valid_bunch_number);
addParameter(p, 'auto_setup', 'yes', boolean_string);
addParameter(p, 'plotting', 'yes', boolean_string);
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'sweep_start', -40, valid_number);
addParameter(p, 'sweep_step', 5, valid_number);
addParameter(p, 'sweep_end', 10, valid_number);
addParameter(p, 'sweep_speed', 2, valid_number);

parse(p, mbf_ax, single_bunch_location, varargin{:});

% getting general environment data.
data = machine_environment;

% Add the extra data to the data structure.
data.ax_label = mbf_ax;
data.base_name = ['frontend_gain_scan_', mbf_ax, '_axis'];
data.orig_gain = get_variable([mbf_pv, sequencer1.gaindb]);
data.original_setting=get_variable(fe_gain_pv);

input_fields = fieldnames(p.Results);
for jltf = 1:length(input_fields)
    data.(input_fields{jltf}) = p.Results.(input_fields{jltf});
end %for

% set up the sweep
data.gain = [data.sweep_start:data.sweep_step:data.sweep_end ...
    data.sweep_end - data.sweep_step:-data.sweep_step:data.sweep_start];

%prealloacation
data.adc_mean = NaN(length(data.gain), 1);
data.adc_max = NaN(length(data.gain), 1);
data.adc_min = NaN(length(data.gain), 1);

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_ax, "TuneOnly")
end %if

% moving to starting point in scan
for pp = data.original_setting:-p.Results.sweep_step:p.Results.sweep_start
    set_variable(fe_gain_pv, pp)
    pause(.5)
end %for

% measurement
for x = 1:length(data.gain)
    set_variable(fe_gain_pv, data.gain(x))
    pause(p.Results.sweep_speed)
    data.adc_mean(x) = max(get_variable([mbf_pv, adc.mean]));
    data.adc_max(x) = max(get_variable([mbf_pv, adc.max]));
    data.adc_min(x) = max(get_variable([mbf_pv, adc.min]));
end %for

% move back to the original setting
for pp = data.sweep_start:data.sweep_step:data.original_setting
    set_variable(fe_gain_pv, pp)
    pause(.5)
end %for

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_ax, "TuneOnly")
    set_variable([mbf_pv, sequencer1.gaindb], data.orig_gain);
end %if

%% saving the data to a file
save_to_archive(root_string, data)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, data)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_frontend_gain_scan_archival_retrieval(mbf_ax,...
        [data.time data.time], filter_conditions)
end %if
