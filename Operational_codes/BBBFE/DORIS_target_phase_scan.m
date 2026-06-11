function data = DORIS_target_phase_scan(single_bunch_location, varargin)
% Scans the phase of the DORIS unit upstream of the MBF frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      single_bunch_location (int): the location of the single bunch.
%
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the
%                                      main archive.
%       sweep_start(int): phase value in degrees to start the sweep.
%       sweep_step(int):  phase scan step in degrees.
%       sweep_end(int):   phase value in degreees to stop the sweep.
%
% Machine setup: (manual for the time being...)
% fill some charge in bunch 1 (0.2nC)
%
% Example: DORIS_target_phase_scan(400)

[root_string, ~, pv_names] = mbf_system_config;
detector = pv_names.tails.Detector;
doris_pv = pv_names.doris.phase;
mbf_pv_x = pv_names.hardware_names.x;
mbf_pv_y = pv_names.hardware_names.y;
mbf_pv_s = pv_names.hardware_names.s;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = @(x) any(validatestring(x, {'yes', 'no'}));
valid_bunch_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);
valid_number = @(x) isnumeric(x) && isscalar(x);

addRequired(p, 'single_bunch_location', valid_bunch_number);
addParameter(p, 'auto_setup', 'yes', boolean_string);
addParameter(p, 'plotting', 'yes', boolean_string);
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'sweep_start', -180, valid_number);
addParameter(p, 'sweep_step', 5, valid_number);
addParameter(p, 'sweep_end', 180, valid_number);

parse(p, single_bunch_location, varargin{:});

% getting general environment data.
data = machine_environment;

% Add the extra data to the data structure.
data.base_name = 'doris_phase_scan';
data.original_setting = get_variable(doris_pv);
data.orig_gain_x = get_variable([mbf_pv_x, sequencer1.gaindb]);
data.orig_gain_y = get_variable([mbf_pv_y, sequencer1.gaindb]);
data.orig_gain_s = get_variable([mbf_pv_s, sequencer1.gaindb]);
input_fields = fieldnames(p.Results);
for jltf = 1:length(input_fields)
    data.(input_fields{jltf}) = p.Results.(input_fields{jltf});
end %for

% set up the sweep
data.phase = [data.sweep_start:data.sweep_step:data.sweep_end ...
    data.sweep_end - data.sweep_step:-data.sweep_step:data.sweep_start];

% prealloacation
data.side1_x = NaN(length(data.phase), 1);
data.main_x = NaN(length(data.phase), 1);
data.side2_x = NaN(length(data.phase), 1);
data.side1_y = NaN(length(data.phase), 1);
data.main_y = NaN(length(data.phase), 1);
data.side2_y = NaN(length(data.phase), 1);

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode('x', "TuneOnly")
    setup_operational_mode('y', "TuneOnly")
    setup_operational_mode('s', "TuneOnly")
end %if

detector_setup_x = BBBFE_detector_setup('x', single_bunch_location);
detector_setup_y = BBBFE_detector_setup('y', single_bunch_location);
detector_setup_s = BBBFE_detector_setup('s', single_bunch_location);

% moving to starting point in scan
set_variable(doris_pv, -180)
for dbf = 1:length(data.phase)
    set_variable(doris_pv, data.phase(dbf))
    pause(2)
    data.side1_x(dbf) = max(get_variable([data.mbf_pv_x, detector.det1.power]));
    data.main_x(dbf) = max(get_variable([data.mbf_pv_x, detector.det2.power]));
    data.side2_x(dbf) = max(get_variable([data.mbf_pv_x, detector.det3.power]));
    data.side1_x(dbf) = max(get_variable([data.mbf_pv_y, detector.det1.power]));
    data.main_x(dbf) = max(get_variable([data.mbf_pv_y, detector.det2.power]));
    data.side2_x(dbf) = max(get_variable([data.mbf_pv_y, detector.det3.power]));
    fprintf('.')
end %for

% move back to the original setting
set_variable(doris_pv, data.original_setting)

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode('x', "TuneOnly")
    set_variable([mbf_pv_x, sequencer1.gaindb], data.orig_gain_x);
     setup_operational_mode('y', "TuneOnly")
    set_variable([mbf_pv_y, sequencer1.gaindb], data.orig_gain_y);
     setup_operational_mode('s', "TuneOnly")
    set_variable([mbf_pv_s, sequencer1.gaindb], data.orig_gain_s);
end %if

BBBFE_detector_restore('x', detector_setup_x)
BBBFE_detector_restore('y', detector_setup_y)
BBBFE_detector_restore('s', detector_setup_s)

%% saving the data to a file
save_to_archive(root_string, data)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, data)
end %if

%% plotting
if strcmp(p.Results.plotting, 'yes')
    DORIS_phase_scan_plotting(data)
end %if