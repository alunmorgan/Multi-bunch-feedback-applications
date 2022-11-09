function varargout = mbf_PPRE_capture(mbf_axis, excitation_gain, excitation_frequency, varargin)
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
%
% Example: data =  mbf_PPRE_capture('y','excitation_gain', -30, 'save_to_archive', 'no');

% Define input and default values
binary_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

tunes = get_all_tunes(mbf_axis);
leftSB = tunes.([mbf_axis, '_tune']).lower_sideband;
default_excitation_frequency = leftSB;
default_excitation_gain = -60; %dB

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation_gain', default_excitation_gain, validScalarNum);
addParameter(p, 'excitation_frequency',default_excitation_frequency, validScalarNum);
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'harmonic', 0, validScalarNum);
addParameter(p, 'repeat_datapoints', 10, validScalarNum);
parse(p, mbf_axis, excitation_gain, excitation_frequency, varargin{:});

% Set up MBF environment
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};

%% Get environment data

% getting general environment data.
PPRE = machine_environment;

% Add the axis label to the data structure.
PPRE.ax_label = mbf_axis;

% construct name and add it to the structure
PPRE.base_name = ['PPRE_' PPRE.ax_label '_axis'];

% Excitation frequency and gain
PPRE.excitation_gain = excitation_gain;
PPRE.excitation_frequency = excitation_frequency;
PPRE.harmonic = p.Results.harmonic;

% Tune sweeps (do we need all of these?)
PPRE.tune_x_sweep = lcaGet('SR23C-DI-TMBF-01:X:TUNE:DMAGNITUDE');
PPRE.tune_x_sweep_model = lcaGet('SR23C-DI-TMBF-01:X:TUNE:MMAGNITUDE');
PPRE.tune_x_scale = lcaGet('SR23C-DI-TMBF-01:X:TUNE:SCALE');
PPRE.tune_y_sweep = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:DMAGNITUDE');
PPRE.tune_y_sweep_model = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:MMAGNITUDE');
PPRE.tune_y_scale = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:SCALE');
PPRE.tunes = get_all_tunes('xys');

%% Set up MBF excitation

mbf_name = mbf_axis_to_name(mbf_axis);
mbf_emittance_setup(mbf_axis, 'excitation', excitation_gain(1),...
    'excitation_frequency',excitation_frequency(1), 'harmonic', p.Results.harmonic)

%% Do measurement
orig_gain = lcaGet([mbf_name, 'NCO2:GAIN_DB_S']);
orig_freq = lcaGet([mbf_name, 'NCO2:FREQ_S']);

% gain scan
if length(p.Results.excitation_gain) > 1
    for whd = 1:length(p.Results.excitation_gain)
        fprintf('Measurement %d\n',whd);
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.excitation_gain(whd));
        pause(1)
        PPRE.scan{whd} = PPRE_aquisition(p.Results.repeat_datapoints);
    end %for
    
    % frequency scan
elseif length(p.Results.excitation_frequency) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.harmonic(1) + p.Results.excitation_frequency(nwa));
        pause(1)
        PPRE.scan{nwa} = PPRE_aquisition(p.Results.repeat_datapoints);
    end %for
    % harmonic scan
elseif length(p.Results.harmonic) > 1
    for nwa = 1:length(p.Results.excitation_frequency)
        fprintf('Measurement %d\n',nwa);
        lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
        lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.harmonic(nwa) + p.Results.excitation_frequency(1));
        pause(1)
        PPRE.scan{nwa} = PPRE_aquisition(p.Results.repeat_datapoints);
    end %for
else
    lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);
    pause(1) % Wait for emittance to stablise
    PPRE.scan{1} = PPRE_aquisition(p.Results.repeat_datapoints);
end %if

lcaPut([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain)
lcaPut([mbf_name, 'NCO2:FREQ_S'], orig_freq)
lcaPut([mbf_name, 'NCO2:ENABLE_S'], 0)
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
