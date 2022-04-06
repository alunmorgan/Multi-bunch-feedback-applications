function varargout = MBF_beam_excitation(mbf_axis, excitation_gain, excitation_frequency, varargin)
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
% Example: data = MBF_beam_excitation('x', -18, 0.27, 'save_to_archive', 'no');


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

% Tune sweeps (do we need all of these?)
emittance_blowup.tune_x_sweep = lcaGet('SR23C-DI-TMBF-01:X:TUNE:DMAGNITUDE');
emittance_blowup.tune_x_sweep_model = lcaGet('SR23C-DI-TMBF-01:X:TUNE:MMAGNITUDE');
emittance_blowup.tune_x_scale = lcaGet('SR23C-DI-TMBF-01:X:TUNE:SCALE');
emittance_blowup.tune_y_sweep = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:DMAGNITUDE');
emittance_blowup.tune_y_sweep_model = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:MMAGNITUDE');
emittance_blowup.tune_y_scale = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:SCALE');
emittance_blowup.tunes = get_all_tunes('xys');

%% Set up MBF excitation

mbf_name = mbf_axis_to_name(mbf_axis);
mbf_emittance_setup(mbf_axis, 'excitation', excitation_gain(1),...
    'excitation_frequency',excitation_frequency(1), 'harmonic', p.Results.harmonic)

%% Capture data
% % There is an additional 5 second delay in the BPM capture function.
% Move this inside loop
% emittance_blowup.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
% emittance_blowup.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
% emittance_blowup.pinhole1_image = get_Pinhole_image('SR01C-DI-DCAM-04');
% emittance_blowup.pinhole2_image = get_Pinhole_image('SR01C-DI-DCAM-05');

%plotting
% plot_BPM_FA_data(emittance_blowup.bpm_data)
% plot_pinhole_image(emittance_blowup.pinhole1_image)
% plot_pinhole_image(emittance_blowup.pinhole2_image)

%% Do measurement

if length(p.Results.excitation_gain) > 1
    orig_gain = lcaGet([mbf_name, 'NCO2:GAIN_DB_S']);
    
    for whd = 1:length(p.Results.excitation_gain)        
        lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.harmonic + p.Results.excitation_gain(whd));        
        % There is an additional 5 second delay in the BPM capture function.
        emittance_blowup.scan{whd}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
        emittance_blowup.scan{whd}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
        %emittance_blowup.gain_scan{whd}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
        %emittance_blowup.gain_scan{whd}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
        % emittance_blowup.pinhole1_image = get_Pinhole_image('SR01C-DI-DCAM-04');
        % emittance_blowup.pinhole2_image = get_Pinhole_image('SR01C-DI-DCAM-05');
    end %for
    
    lcaPut([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain)
    
elseif length(p.Results.excitation_frequency) > 1
    orig_freq = lcaGet([mbf_name, 'NCO2:FREQ_S']);
    
    for nwa = 1:length(p.Results.excitation_frequency)        
        lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.excitation_frequency(nwa));        
        % There is an additional 5 second delay in the BPM capture function.
        emittance_blowup.scan{nwa}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
        emittance_blowup.scan{nwa}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');   
    end %for
    
    lcaPut([mbf_name, 'NCO2:FREQ_S'], orig_freq)
    
else
    emittance_blowup.scan{1}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
    emittance_blowup.scan{1}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
%     emittance_blowup.pinhole1_image = get_Pinhole_image('SR01C-DI-DCAM-04');
%     emittance_blowup.pinhole2_image = get_Pinhole_image('SR01C-DI-DCAM-05');
    
end %if

%% optional loop for gain scan
% if length(p.Results.excitation_gain) > 1
%     orig_gain = lcaGet([mbf_name, 'NCO2:GAIN_DB_S']);
%     for whd = 1:length(p.Results.excitation_gain)
%         lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.harmonic + p.Results.excitation_gain(whd));
%         % There is an additional 5 second delay in the BPM capture function.
%         emittance_blowup.gain_scan{whd}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
%         emittance_blowup.gain_scan{whd}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
%     end %for
%     lcaPut([mbf_name, 'NCO2:GAIN_DB_S'], orig_gain)
% end %if

%% optional loop for frequency scan
% if length(p.Results.excitation_frequency) > 1
%     orig_freq = lcaGet([mbf_name, 'NCO2:FREQ_S']);
%     for nwa = 1:length(p.Results.excitation_frequency)
%         lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.excitation_frequency(nwa));
%         % There is an additional 5 second delay in the BPM capture function.
%         emittance_blowup.freq_scan{nwa}.bpm_data = get_BPM_FA_data(p.Results.BPM_data_capture_length);
%         emittance_blowup.freq_scan{nwa}.pinhole_data = pinhole_cal_capture('pinhole3', 'no','save_data', 'no');
%     end %for
%     lcaPut([mbf_name, 'NCO2:FREQ_S'], orig_freq)
% end %if

%% Calculate output

bpm_nr = 1;

for i = 1:length(scan)
        
    emittance_blowup.beam_oscillation_x(i) = std(emittance_blowup.scan{i}.bpm_data.X(bpm_nr,:));
    emittance_blowup.beam_oscillation_y(i) = std(emittance_blowup.scan{i}.bpm_data.Y(bpm_nr,:));
    
    emittance_blowup.emittance_x(i) = emittance_blowup.scan{i}.pinhole_data.hemit;
    emittance_blowup.emittance_y(i) = emittance_blowup.scan{i}.pinhole_data.veimt;
    
end

%% Plot results

figure(1)
yyaxis left
plot(excitation_frequency,emittance_blowup.beam_oscillation_x.*1e-3,'.-')
xlabel('Excitation frequency [tune]')
ylabel('Hor. RMS oscillation [\mum]')
yyaxis right
plot(excitation_frequency,emittance_blowup.emittance_x,'.-')
ylabel('Hor. emittance [nm rad]')

figure(2)
yyaxis left
plot(excitation_frequency,emittance_blowup.beam_oscillation_y.*1e-3,'.-')
xlabel('Excitation frequency [tune]')
ylabel('Ver. RMS oscillation [\mum]')
yyaxis right
plot(excitation_frequency,emittance_blowup.emittance_y,'.-')
ylabel('Ver. emittance [pm rad]')

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