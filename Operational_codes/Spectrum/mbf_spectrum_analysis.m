% function [bunch_data, tune_data] = mbf_spectrum_analysis(raw_data, fold)
function data = mbf_spectrum_analysis(input_data, turns_override)

% Analysis the raw time data from the mbf system in order to
% generate a spectrogram of all bunches.
%
% Args:
%       raw_data (cell array): Multiple sets of time data.
%       turns_override(int): Forces the analysis to use a certain number of
%                            turns in the analysis. This is useful for
%                            comparing different datasets.
%                            Time domain data is eihter padded or trimmed
%                            as needed.
% Returns:
%           data (structure): analysed data.
%
% Example: data = mbf_spectrum_analysis(raw_data, 1)

if nargin <2
    turns = input_data.n_turns;
else
    turns = turns_override;
end %if

% for k=1:raw_data.repeat
%     data_length=length(raw_data.raw_data{k});
for k=1:input_data.repeat
    % Individual bunch analysis.
    %turn into matrix bunches x turns
    xx = reshape(input_data.raw_data{k}, input_data.harmonic_number, []);
    %subtract the average position per bunch
    xx = xx-repmat(mean(xx,2), 1, input_data.n_turns);

    motion_only = reshape(xx, 1, []); %stretch out again
    motion_only_windowed = hannwin(motion_only);
    motion_only_windowed_padded = padarray(motion_only_windowed, [0,(input_data.harmonic_number * turns) - length(motion_only_windowed)] , 0, 'post');
    motion_only_windowed_padded = reshape(motion_only_windowed_padded', input_data.harmonic_number, []);
    % find the overall spectrum of the motion for each individual bunch with the static position offsets removed.
    xf1 = abs(fft(motion_only_windowed_padded, [], 2))./input_data.n_turns;

    if k==1
        bunch_motion = motion_only_windowed_padded;
        bunch_motion_spectrum = xf1;
    else
        bunch_motion_spectrum = bunch_motion_spectrum + xf1; % accumulating
        bunch_motion = bunch_motion + xx;  % accumulating
    end %if
end % for

% Generating the frquency scales
frev = input_data.RF / input_data.harmonic_number;
timescale = (1:turns) ./ frev; %sec
timestep = timescale(2) - timescale(1);
bunch_motion_f_scale = 1./timestep .* (-(turns/2)+1:(turns/2)) ./turns; %Hz

data.bunch_motion = bunch_motion;
data.bunch_motion_timescale = timescale;

data.bunch_f_data = bunch_motion_spectrum;
data.bunch_f_bunches = sum(bunch_motion_spectrum.^2,2)';
data.bunch_f = sum(bunch_motion_spectrum.^2,1);
data.bunch_f_scale = bunch_motion_f_scale;
data.bunch_tune_scale = bunch_motion_f_scale ./ (input_data.RF ./ input_data.harmonic_number);
