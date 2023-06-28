% function [bunch_data, tune_data] = mbf_spectrum_analysis(raw_data, fold)
function data = mbf_spectrum_analysis(input_data, fold_data)

% Analysis the raw time data from the mbf system in order to
% generate a spectrogram of all bunches.
%
% Args:
%       raw_data (cell array): Multiple sets of time data.
%       fold (int): The number of times to fold the data along the
%                   frequency axis. This enhances power resolution
%                   at the cost of frequency resolution.
% Returns:
%           data (structure): analysed data.
%
% Example: data = mbf_spectrum_analysis(raw_data, 1)

% for k=1:raw_data.repeat
%     data_length=length(raw_data.raw_data{k});
for k=1:input_data.repeat
    data_length=length(input_data.raw_data{k});
    %turn into matrix bunches x turns
    xx = reshape(input_data.raw_data{k}, input_data.harmonic_number, []);
    %subtract the average position per bunch
    xx = xx-repmat(mean(xx,2), 1, input_data.n_turns);
    % find the overall spectrum of the motion across all bunches with the static position offsets removed.
    motion_only = reshape(xx, 1, []); %stretch out again
    xf1 = abs(fft(hannwin(xx), [], 2))/input_data.n_turns;
    % This enhances power resolution at the cost of frequency resolution.
    folded_motion = reshape(motion_only, data_length/fold_data, fold_data);
    %calculate spectrum over all bunches
    s = 2*sqrt(mean(abs(fft(hannwin(folded_motion)) / (data_length/fold_data)) .^2, 2));
        %fold into tune x modes
    ss1 = reshape(s, input_data.n_turns/fold_data, input_data.harmonic_number);
    
        if k==1
            mode_data = ss1;
            bunch_data = xf1;
        else
        mode_data = mode_data + ss1; % accumulating.
            bunch_data = bunch_data + xf1; % accumulating
        end %if
end % for

data.bunch_data = bunch_data;
data.bunch_bunches = sum(bunch_data.^2,1);
data.bunch_tune = sum(bunch_data.^2,2);

data.tune_data = fftshift(mode_data, 2);
data.mode_modes = sum(bunch_data.^2,1);
data.mode_tune = sum(mode_data(:,1:end/2).^2, 1);

data.tune_axis = linspace(0,.5,length(data.bunch_tune));
data.bunch_axis = 1:input_data.harmonic_number;
data.mode_axis = -input_data.harmonic_number/2 : (input_data.harmonic_number/2 -1) ;
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
