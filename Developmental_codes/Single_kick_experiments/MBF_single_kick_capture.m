function varargout = MBF_single_kick_capture(mbf_axis, excitation_gain, excitation_frequency, varargin)
% Sets up the FLL with an additional excitation at a user defined gain and
% frequency/tune.
%   Args:
%       mbf_axis(str): 'x', or 'y'
%       excitation_gain(vector of floats): the magnitude of the excitation in dB.
%       excitation_frequency(vector of floats): The tune value of the additional excitation
%       harmonic(vector of ints): The tune harmonic to operate on.
%       BPM_data_capture_length(float): Amount of FA data to capture from
%                                       the BPMs in seconds
%       save_to_archive(str): 'yes' or 'no'
%       additional_save_location(str): if specified the data will be saved
%                                      to this location.
%   Returns:
%       single_kick(struct): data captured from the BPMs.
%
% Example: data = MBF_single_kick_capture('x', -18, 0.27, 'save_to_archive', 'no');


% Define input and default values
binary_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addRequired(p, 'excitation_gain');
addRequired(p, 'excitation_frequency');
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'harmonic', 0, validScalarNum);
addParameter(p, 'excitation_delay', 1, validScalarNum);
addParameter(p, 'BPMs_to_capture', 1:173);
addParameter(p, 'repeat_points', 10, validScalarNum);
parse(p, mbf_axis, excitation_gain, excitation_frequency, varargin{:});

% Set up MBF environment
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};

%% Get environment data

% getting general environment data.
single_kick = machine_environment;

% Add the axis label to the data structure.
single_kick.ax_label = mbf_axis;

% construct name and add it to the structure
single_kick.base_name = ['single_kick_' single_kick.ax_label '_axis'];

% Excitation frequency and gain
single_kick.excitation_gain = excitation_gain;
single_kick.excitation_frequency = excitation_frequency;
single_kick.harmonic = p.Results.harmonic;
single_kick.excitation_delay = p.Results.excitation_delay;

%% Set up MBF excitation
mbf_name = mbf_axis_to_name(mbf_axis);
orig_seq = get_variable([mbf_name, 'TRG:SEQ:MODE_S']);

%% Set up BPM capture
% bpm_capture_length = 1024; %Turns
% setup_BPM_TbT_capture(nbpms, bpm_capture_length)
%% Do measurements
input_settings = p.Results;
% gain scan
if length(p.Results.excitation_gain) > 1
    for whd = 1:length(p.Results.excitation_gain)
        fprintf('Measurement %d\n',whd);
        input_settings.excitation_gain = p.Results.excitation_gain(whd);
        input_settings.excitation_frequency = p.Results.excitation_frequency(1);
        input_settings.harmonic = p.Results.harmonic(1);
        single_kick.scan_label = 'Gain';
        single_kick.bpm_data{whd} = single_kick_aquisition(mbf_axis, input_settings);
    end %for
    % frequency scan
elseif length(p.Results.excitation_frequency) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        input_settings.excitation_gain = p.Results.excitation_gain(1);
        input_settings.excitation_frequency = p.Results.excitation_frequency(nwa);
        input_settings.harmonic = p.Results.harmonic(1);
        single_kick.scan_label = 'Frequency';
        single_kick.bpm_data{nwa} = single_kick_aquisition(mbf_axis, input_settings);
    end %for
    % harmonic scan
elseif length(p.Results.harmonic) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        input_settings.excitation_gain = p.Results.excitation_gain(1);
        input_settings.excitation_frequency = p.Results.excitation_frequency(1);
        input_settings.harmonic = p.Results.harmonic(nwa);
        single_kick.scan_label = 'Harmonic';
        single_kick.bpm_data{nwa} = single_kick_aquisition(mbf_axis, input_settings);
    end %for
else
    input_settings.excitation_gain = p.Results.excitation_gain(1);
    input_settings.excitation_frequency = p.Results.excitation_frequency(1);
    input_settings.harmonic = p.Results.harmonic(1);
    single_kick.scan_label = '';
    single_kick.bpm_data{1} = single_kick_aquisition(mbf_axis, input_settings);
end %if

set_variable([mbf_name, 'TRG:SEQ:MODE_S'], orig_seq);

%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, single_kick)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, single_kick)
    end %if
end %if

if nargout == 1
    varargout{1} = single_kick;
end %if


