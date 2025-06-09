function varargout = MBF_excitation_capture(mbf_axis, excitation_gain, varargin)
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

% Define input and default values
binary_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addRequired(p, 'excitation_gain');
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'harmonic', 0, validScalarNum);
addParameter(p, 'BPM_data_capture_length', 1, validScalarNum);
parse(p, mbf_axis, excitation_gain, varargin{:});

% Set up MBF environment
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};

%% Get environment data

% getting general environment data.
emittance_blowup = machine_environment;

% Add the axis label to the data structure.
emittance_blowup.ax_label = mbf_axis;

% construct name and add it to the structure
emittance_blowup.base_name = ['emittance_gain_scan_' emittance_blowup.ax_label '_axis'];

emittance_blowup.harmonic = p.Results.harmonic;

%% Set up MBF excitation

mbf_name = mbf_axis_to_name(mbf_axis);
mbf_emittance_setup(mbf_axis, 'excitation', excitation_gain(1),...
    'harmonic', p.Results.harmonic)

%% Do measurement
orig_gain = get_variable([mbf_name, 'NCO2:GAIN_DB_S']);

% gain scan
for whd = 1:length(p.Results.excitation_gain)
    fprintf('Measurement %d\n',whd);
    set_variable([mbf_name, 'NCO2:ENABLE_S'], 0);
    set_variable([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.excitation_gain(whd));
    pause(2)
    for nds = 1:160
        if nds >= 40 && nds < 120
            set_variable([mbf_name, 'NCO2:ENABLE_S'], 1)
            excitation_gain = p.Results.excitation_gain(whd);
        else
            set_variable([mbf_name, 'NCO2:ENABLE_S'], 0);
            excitation_gain = 0;
        end %if
        pause(0.25)
        while ~strcmp('Fit Forced',get_variable('SR-DI-EMIT-01:STATUS')) && ~strcmp('Successful',get_variable('SR-DI-EMIT-01:STATUS'))
            pause(0.2);
        end
        emittance_blowup.scan{whd}{nds}.emittance = emittance_get_data;
        emittance_blowup.excitation_gain{whd}{nds} = excitation_gain;
    end %for
end %for

set_variable([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain)
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
