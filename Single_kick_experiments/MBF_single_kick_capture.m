function varargout = MBF_single_kick_capture(mbf_axis, excitation_gain, excitation_frequency, varargin)
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
addParameter(p, 'BPM_data_capture_length', 1, validScalarNum);
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

% Tune sweeps (do we need all of these?)
single_kick.tune_x_sweep = lcaGet('SR23C-DI-TMBF-01:X:TUNE:DMAGNITUDE');
single_kick.tune_x_sweep_model = lcaGet('SR23C-DI-TMBF-01:X:TUNE:MMAGNITUDE');
single_kick.tune_x_scale = lcaGet('SR23C-DI-TMBF-01:X:TUNE:SCALE');
single_kick.tune_y_sweep = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:DMAGNITUDE');
single_kick.tune_y_sweep_model = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:MMAGNITUDE');
single_kick.tune_y_scale = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:SCALE');
single_kick.tunes = get_all_tunes('xys');

%% Set up MBF excitation
mbf_name = mbf_axis_to_name(mbf_axis);
orig_gain = lcaGet([mbf_name, 'NCO2:GAIN_DB_S']);
orig_freq = lcaGet([mbf_name, 'NCO2:FREQ_S']);
orig_seq = lcaGet([mbf_name, 'TRG:SEQ:MODE_S']);
mbf_name = mbf_axis_to_name(mbf_axis);
mbf_single_kick_setup(mbf_axis, 'excitation_gain', excitation_gain(1),...
    'excitation_frequency',excitation_frequency(1), 'harmonic', p.Results.harmonic)

%% Do measurements

% gain scan
if length(p.Results.excitation_gain) > 1
    for whd = 1:length(p.Results.excitation_gain)
        fprintf('Measurement %d\n',whd);
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.harmonic + p.Results.excitation_gain(whd));
        lcaPut([mbf_name, 'NCO2:ENABLE_S'],'On');
        % might need to trigger without capture in order to get the system to
        % honour the settings changes.
        lcaPut([mbf_name, 'TRG:SEQ:ARM_S.PROC'], 1)
        arm_BPM_TbT_capture
        pause(1)
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 1);
        single_kick.gain_scan{whd} = single_kick_dataset_capture;
    end %for
end %if
% frequency scan
if length(p.Results.excitation_frequency) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.excitation_frequency(nwa));
        lcaPut([mbf_name, 'NCO2:ENABLE_S'],'On');
        lcaPut([mbf_name, 'TRG:SEQ:ARM_S.PROC'], 1)
        arm_BPM_TbT_capture
        pause(1)
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 1);
        single_kick.f_scan{nwa} = single_kick_dataset_capture;
    end %for
end %if

if length(p.Results.excitation_frequency) == 1 && ...
        length(p.Results.excitation_gain) == 1
    lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
    lcaPut([mbf_name, 'TRG:SEQ:ARM_S.PROC'], 1)
    arm_BPM_TbT_capture
    pause(1)
    lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 1);
    single_kick = single_kick_dataset_capture;
end %if

lcaPut([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain);
lcaPut([mbf_name, 'NCO2:FREQ_S'], orig_freq);
lcaPut([mbf_name, 'NCO2:ENABLE_S'], 'Off');
lcaPut([mbf_name, 'TRG:SEQ:MODE_S'], orig_seq);

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


