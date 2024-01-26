function varargout = MBF_beam_excitation_capture(mbf_axis, excitation_gain, excitation_frequency, varargin)
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
%       emittance_blowup(struct): data captured from the BPMs and the cameras.
%
% Example: data = MBF_beam_excitation_capture('x', -18, 0.27, 'save_to_archive', 'no');

n_bpms = [163,164,167,168];
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
emittance_blowup = machine_environment;

% Add the axis label to the data structure.
emittance_blowup.ax_label = mbf_axis;

% construct name and add it to the structure
emittance_blowup.base_name = ['emittance_blowup_' emittance_blowup.ax_label '_axis'];

% Excitation frequency and gain
emittance_blowup.excitation_gain = excitation_gain;
emittance_blowup.excitation_frequency = excitation_frequency;
emittance_blowup.harmonic = p.Results.harmonic;

% Tune sweeps (do we need all of these?)
emittance_blowup.tune_x_sweep = get_variable('SR23C-DI-TMBF-01:X:TUNE:DMAGNITUDE');
emittance_blowup.tune_x_sweep_model = get_variable('SR23C-DI-TMBF-01:X:TUNE:MMAGNITUDE');
emittance_blowup.tune_x_scale = get_variable('SR23C-DI-TMBF-01:X:TUNE:SCALE');
emittance_blowup.tune_y_sweep = get_variable('SR23C-DI-TMBF-01:Y:TUNE:DMAGNITUDE');
emittance_blowup.tune_y_sweep_model = get_variable('SR23C-DI-TMBF-01:Y:TUNE:MMAGNITUDE');
emittance_blowup.tune_y_scale = get_variable('SR23C-DI-TMBF-01:Y:TUNE:SCALE');
emittance_blowup.tunes = get_all_tunes('xys');

%% Set up MBF excitation

mbf_name = mbf_axis_to_name(mbf_axis);
mbf_emittance_setup(mbf_axis, 'excitation', excitation_gain(1),...
    'excitation_frequency',excitation_frequency(1), 'harmonic', p.Results.harmonic)

%% Do measurement
orig_gain = get_variable([mbf_name, 'NCO2:GAIN_DB_S']);
orig_freq = get_variable([mbf_name, 'NCO2:FREQ_S']);

% gain scan
if length(p.Results.excitation_gain) > 1
    for whd = 1:length(p.Results.excitation_gain)
        fprintf('Measurement %d\n',whd);
        set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        set_variable([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.harmonic + p.Results.excitation_gain(whd));
        arm_BPM_TbT_capture
        pause(1)
        %pause(5) % Wait for emittance to stablise
        set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 1);
        while ~strcmp('Fit Forced',get_variable('SR-DI-EMIT-01:STATUS')) && ~strcmp('Successful',get_variable('SR-DI-EMIT-01:STATUS'))
            pause(0.2);
        end
        emittance_blowup.scan{whd}.bpm_data = get_BPM_TbT_data(n_bpms);
        emittance_blowup.scan{whd}.mbf_data_x = get_variable('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
        emittance_blowup.scan{whd}.mbf_data_y = get_variable('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
        emittance_blowup.scan{whd}.pinhole_settings = get_pinhole_settings;
        emittance_blowup.scan{whd}.pinhole1_image = get_pinhole_image('SR01C-DI-DCAM-04');
        emittance_blowup.scan{whd}.pinhole2_image = get_pinhole_image('SR01C-DI-DCAM-05');
        emittance_blowup.scan{whd}.beam_sizes = get_beam_sizes;
        emittance_blowup.scan{whd}.emittance = get_emittance;
    end %for
    
    % frequency scan
elseif length(p.Results.excitation_frequency) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        set_variable([mbf_name, 'NCO2:FREQ_S'], p.Results.excitation_frequency(nwa));
        arm_BPM_TbT_capture
        pause(1)
        set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 1);
        %pause(6) % Wait for emittance to stablise
        while ~strcmp('Fit Forced',get_variable('SR-DI-EMIT-01:STATUS')) && ~strcmp('Successful',get_variable('SR-DI-EMIT-01:STATUS'))
            pause(0.2);
        end
        emittance_blowup.scan{nwa}.bpm_data = get_BPM_TbT_data(n_bpms);
        emittance_blowup.scan{nwa}.mbf_data_x = get_variable('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
        emittance_blowup.scan{nwa}.mbf_data_y = get_variable('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
        emittance_blowup.scan{nwa}.pinhole_settings = get_pinhole_settings;
        emittance_blowup.scan{nwa}.pinhole1_image = get_pinhole_image('SR01C-DI-DCAM-04');
        emittance_blowup.scan{nwa}.pinhole2_image = get_pinhole_image('SR01C-DI-DCAM-05');
        emittance_blowup.scan{nwa}.beam_sizes = get_beam_sizes;
        emittance_blowup.scan{nwa}.emittance = get_emittance;
    end %for
else
    set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 0);
    arm_BPM_TbT_capture
    pause(1) % Wait for emittance to stablise
    set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 1);
    %pause(6) % Wait for emittance to stablise
    while ~strcmp('Fit Forced',get_variable('SR-DI-EMIT-01:STATUS')) && ~strcmp('Successful',get_variable('SR-DI-EMIT-01:STATUS'))
        pause(0.2);
    end    
    emittance_blowup.scan{1}.bpm_data = get_BPM_TbT_data(n_bpms);
    emittance_blowup.scan{1}.mbf_data_x = get_variable('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
    emittance_blowup.scan{1}.mbf_data_y = get_variable('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
    emittance_blowup.scan{1}.pinhole_settings = get_pinhole_settings;
    emittance_blowup.scan{1}.pinhole1_image = get_pinhole_image('SR01C-DI-DCAM-04');
    emittance_blowup.scan{1}.pinhole2_image = get_pinhole_image('SR01C-DI-DCAM-05');
    emittance_blowup.scan{1}.beam_sizes = get_beam_sizes;
    emittance_blowup.scan{1}.emittance = get_emittance;
end %if

set_variable([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain)
set_variable([mbf_name, 'NCO2:FREQ_S'], orig_freq)
set_variable([mbf_name, 'NCO2:ENABLE_S'], 0)
%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, emittance_blowup)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, emittance_blowup)
    end %if
end %if

if nargout == 1
    varargout{1} = emittance_blowup;
end %if
