function data = mbf_spectrum_analysis(raw_data, n_turns, fold, repeat)
% Analysis the raw time data from the mbf system in order to 
% generate a spectrogram of all bunches.
%
% Args:
%       raw_data (cell array): Multiple sets of time data.
%       fold (int): The number of times to fold the data along the
%                   frequency axis. This enhances power resolution
%                   at the cost of frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
% Returns:
%           data (structure): analysed data.
%
% Example: data = mbf_spectrum_analysis(raw_data, 1, 10)

[~, harmonic_number, ~, ~] = mbf_system_config;

for k=1:repeat    
    % remove everything that is constant each revolotion
    xx = reshape(raw_data{k}, harmonic_number, []); %turn into matrix bunches x turns
    xx = xx-repmat(mean(xx,2), 1, n_turns); %subtract the average position per bunch
    motion_only = reshape(xx, 1, []); %stretch out again
    % This enhances power resolution at the cost of frequency resolution.
    folded_motion = reshape(motion_only, data_length/fold, fold);
    %calculate spectrum over all bunches
    s = 2*sqrt(mean(abs(fft(hannwin(folded_motion)) / (data_length/fold)) .^2, 2));
    ss1 = reshape(s, n_turns/fold, harmonic_number);%fold into tune x modes
    mode_data = mode_data.^2 + ss1.^2; % accumulating.
    xf1 = abs(fft(hannwin(xx), [], 2))/n_turns;
    % only taking the lower half of the FFT
    bunch_data = bunch_data.^2 + (xf1(:,1:end/2).').^2; % accumulating
end % for

data.bunch_data = bunch_data;
data.bunch_bunches = sum(bunch_data.^2,1);
data.bunch_tune = sum(bunch_data.^2,2);

data.tune_data = fftshift(mode_data, 2);
data.mode_modes = sum(bunch_data.^2,1);
data.mode_tune = sum(mode_data(1:end/2,:).^2, 2);

data.tune_axis = linspace(0,.5,length(data.bunch_tune));
data.bunch_axis = 1:harmonic_number;
data.mode_axis = -harmonic_number/2 : (harmonic_number/2 -1) ;
end

function data_windowed=hannwin(data,dim)
s=size(data);
if nargin<2
    [~,dim]=max(s);
end
rh=s;
rh(dim)=1;
t=linspace(0,2*pi,s(dim)+1);
t=t(1:end-1);
h=(1-cos(t));
data_windowed=data.*(repmat(shiftdim(h,dim),rh));
end
