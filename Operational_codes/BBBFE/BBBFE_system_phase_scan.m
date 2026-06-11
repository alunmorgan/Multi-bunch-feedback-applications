function BBBFE_system_phase_scan(mbf_ax, single_bunch_location, varargin)
% Scans one of the individual axis system phase shifts in the
% bunch by bunch frontend and records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%       mbf_axis(str): 'x','y', or 's'
%       single_bunch_location(int): location of the target bunch.
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the
%                                      main archive.
%
% Machine setup
% fill some charge in bunch 'single_bunch_location' (0.2nC)
%
% Example: BBBFE_system_phase_scan('x', 400)

[root_string, ~, pv_names] = mbf_system_config;
detector = pv_names.tails.Detector;
adc =  pv_names.tails.adc;
frontend = pv_names.frontend.base;
fe_system_phase = pv_names.frontend.system_phase;
sequencer1 = pv_names.tails.Sequencer.seq1;

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
addParameter(p, 'sweep_start', -180, valid_number);
addParameter(p, 'sweep_step', 20, valid_number);
addParameter(p, 'sweep_end', 180, valid_number);

parse(p, mbf_axis, single_bunch_location, varargin{:});

mbf_pv = pv_names.hardware_names.(mbf_axis);
if strcmpi(mbf_axis,'x') || strcmpi(mbf_axis, 'y')
    fe_phase_pv = [pv_names.frontend.base fe_system_phase.(mbf_axis)];
else
    fe_phase_pv = [frontend fe_system_phase.sI];
    fe_phase_pvQ = [frontend fe_system_phase.sQ];
end %if

% getting general environment data.
data = machine_environment;

% Add the extra data to the data structure.
data.ax_label = mbf_axis;
data.base_name = ['system_phase_scan_', mbf_ax, '_axis'];
data.orig_gain = get_variable([pv_names.hardware_names.(mbf_ax), sequencer1.gaindb]);
data.original_setting=get_variable(fe_phase_pv);
if strcmpi(mbf_axis, 's')
    data.original_settingQ=get_variable(fe_phase_pvQ);
end %if

input_fields = fieldnames(p.Results);
for jltf = 1:length(input_fields)
    data.(input_fields{jltf}) = p.Results.(input_fields{jltf});
end %for

% set up the sweep
data.phase = [data.sweep_start:data.sweep_step:data.sweep_end ...
    data.sweep_end - data.sweep_step:-data.sweep_step:data.sweep_start];

%prealloacation
data.side1 = NaN(length(data.phase), 1);
data.main = NaN(length(data.phase), 1);
data.side2 = NaN(length(data.phase), 1);
data.adc_phase = NaN(length(data.phase), 1);

if strcmp(p.Results.auto_setup, 'yes')
    original_detector_setup = BBBFE_detector_setup(mbf_ax, single_bunch_location);
    setup_operational_mode(mbf_ax, "TuneOnly")
end %if

% moving to starting point in scan
for pp = data.original_setting:-p.Results.sweep_step:p.Results.sweep_start
    set_variable(fe_phase_pv, pp)
    pause(.5)
end %for
if strcmpi(mbf_axis, 's')
    % I and Q must be in quadrature
    for pp=data.original_settingQ:-p.Results.sweep_step:p.Results.sweep_start + 90
        set_variable(fe_phase_pvI, pp)
        pause(.5)
    end %for
end %if

% measurement
for x = 1:length(data.phase)
    set_variable(fe_phase_pv, data.phase(x))
    if scrcmpi(mbf_axis, 's')
        set_variable(fe_phase_pvQ, data.phase(x) + 90)
    end %if
    pause(2)
    data.side1(x) = max(get_variable([mbf_pv, detector.det1.power]));
    data.main(x) = max(get_variable([mbf_pv, detector.det2.power]));
    data.side2(x) = max(get_variable([mbf_pv, detector.det3.power]));
    data.adc_phase(x) = max(get_variable([mbf_pv, adc.phase.mean]));
    data.adc_mean(x) = max(get_variable([mbf_pv, adc.mean]));
    data.adc_max(x) = max(get_variable([mbf_pv, adc.max]));
    data.adc_min(x) = max(get_variable([mbf_pv, adc.min]));
end

% move back to the original setting
for pp = data.sweep_start:data.sweep_step:data.original_setting
    set_variable(fe_phase_pv, pp)
    pause(.5)
end %for
if strcmpi(mbf_axis, 's')
    % move back to the original setting
    for pp=data.sweep_start + 90:data.sweep_step:data.original_settingQ
        set_variable(fe_phase_pvQ, pp)
        pause(.5)
    end
end %if

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_ax, "TuneOnly")
    BBBFE_detector_restore(mbf_ax, original_detector_setup)
    set_variable([pv_names.hardware_names.(mbf_ax), sequencer1.gaindb], orig_gain);
end %if

%% saving the data to a file
save_to_archive(root_string, data)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, data)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_frontend_system_phase_scan_archival_retrieval(mbf_axis,...
        [data.time data.time], filter_conditions)
end %if
