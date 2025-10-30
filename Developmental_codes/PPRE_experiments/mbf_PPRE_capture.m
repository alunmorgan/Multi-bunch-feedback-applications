function varargout = mbf_PPRE_capture(mbf_axis, varargin)
% Sets up the FLL with an additional excitation at a user defined gain and
% frequency/tune.
%   Args:
%       mbf_axis(str): 'x', or 'y'
%       excitation_gain(vector of floats): the magnitude of the excitation in dB.
%       excitation_frequency(vector of floats): The tune value of the additional excitation
%       harmonic(int): The tune harmonic to operate on.
%       BPM_data_capture_length(float): Amount of FA data to capture from
%                                       the BPMs in seconds
%       save_to_archive(str): 'yes' or 'no'
%       additional_save_location(str): if specified the data will be saved
%                                      to this location.
%   Returns:
%       PPRE(struct): data captured from the MBF system and the cameras.
%       PPRE.scan contains a 3D cell array of scans: axis 1 is gain, axis 2 is
%       frequency, axis 3 is harmonic.
%
% Example: data =  mbf_PPRE_capture('y','excitation_gain', -30, 'save_to_archive', 'no');

[root_string, harmonic_number, pv_names, ~] = mbf_system_config;

% Define input and default values
binary_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

tunes = get_all_tunes;
leftSB = tunes.([mbf_axis, '_tune']).lower_sideband;
default_excitation_frequency = leftSB;
default_excitation_gain = -60; %dB
default_excitation_pattern = ones(harmonic_number,1);
default_harmonic = 0;
default_repeat_datapoints = 20;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation_gain', default_excitation_gain);
addParameter(p, 'excitation_frequency',default_excitation_frequency);
addParameter(p, 'excitation_pattern', default_excitation_pattern);
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'harmonic', default_harmonic);
addParameter(p, 'repeat_datapoints', default_repeat_datapoints, validScalarNum);
parse(p, mbf_axis, varargin{:});

% Set up MBF environment

root_string = root_string{1};
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

%% Get environment data

% getting general environment data.
PPRE = machine_environment;

% Add the axis label to the data structure.
PPRE.ax_label = mbf_axis;

% construct name and add it to the structure
PPRE.base_name = ['PPRE_' PPRE.ax_label '_axis'];

% Excitation frequency and gain
PPRE.excitation_gain = p.Results.excitation_gain;
PPRE.excitation_frequency = p.Results.excitation_frequency;
PPRE.harmonic = p.Results.harmonic;

% Tune sweeps (do we need all of these?)
PPRE.tune_x_sweep = get_variable([mbf_names.x, ':TUNE:DMAGNITUDE']);
PPRE.tune_x_sweep_model = get_variable([mbf_names.x, ':TUNE:MMAGNITUDE']);
PPRE.tune_x_scale = get_variable([mbf_names.x, ':TUNE:SCALE']);
PPRE.tune_y_sweep = get_variable([mbf_names.y, ':TUNE:DMAGNITUDE']);
PPRE.tune_y_sweep_model = get_variable([mbf_names.y, ':TUNE:MMAGNITUDE']);
PPRE.tune_y_scale = get_variable([mbf_names.y, ':TUNE:SCALE']);
PPRE.tunes = get_all_tunes;

%% Set up MBF excitation

PPRE.excitation_pattern = mbf_emittance_setup(mbf_axis, ...
    'excitation', p.Results.excitation_gain(1),...
    'excitation_frequency',p.Results.excitation_frequency(1),...
    'excitation_pattern', p.Results.excitation_pattern, ...
    'harmonic', p.Results.harmonic(1));

%% Setup cameras
set_variable('SR01C-DI-DCAM-05:IMAGEWIDTH', 1024)
set_variable('SR01C-DI-DCAM-04:IMAGEWIDTH', 1024)
set_variable('SR01C-DI-PINH-01:POS1', -2.5)
set_variable('SR01C-DI-PINH-02:POS1', -2.5)

%% Do measurement
orig_gain = get_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db]);
orig_freq = get_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency]);


% gain scan
for whd = 1:length(p.Results.excitation_gain)
    fprintf('\n');
    % frequency scan
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('\n');
        % harmonic scan
        for kef = 1:length(p.Results.harmonic)
            fprintf('.');
            set_variable(pv_names.Hardware_trigger, 0);
            set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db],p.Results.excitation_gain(whd));
            set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency], p.Results.harmonic(1) + p.Results.excitation_frequency(nwa));
            set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency], p.Results.harmonic(kef) + p.Results.excitation_frequency(1));
            pause(10)
            PPRE.scan{whd, nwa, kef} = PPRE_aquisition(p.Results.repeat_datapoints);
        end %for
    end %for
end %for

set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db], orig_gain)
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency], orig_freq)
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.enable], 0)
%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, PPRE)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, PPRE)
    end %if
end %if

if nargout == 1
    varargout{1} = PPRE;
end %if
