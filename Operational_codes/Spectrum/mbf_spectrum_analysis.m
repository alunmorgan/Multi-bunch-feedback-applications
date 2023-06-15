function [bunch_data, tune_data] = mbf_spectrum_analysis(raw_data, fold)
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
% Example: data = mbf_spectrum_analysis(raw_data, 1, 10)

for k=1:raw_data.repeat    
    data_length=length(raw_data.raw_data{k});
    % First find the spectrum of each bunch.
    % remove everything that is constant each revolotion
    xx = reshape(raw_data.raw_data{k}, raw_data.harmonic_number, []); %turn into matrix bunches x turns
    if size(xx,2) > 1
        xx = xx-repmat(mean(xx,2), 1, raw_data.n_turns); %subtract the average position per bunch
        xf1 = abs(fft(hannwin(xx), [], 2))/raw_data.n_turns;
    xf1 = (xf1(:,1:end/2).');% only taking the lower half of the FFT
    else
        xf1 = zeros(raw_data.harmonic_number,1);
    end %if
    % find the overall spectrum of the motion across all bunches with the static position offsets removed.
    motion_only = reshape(xx, 1, []); %stretch out again
    % This enhances power resolution at the cost of frequency resolution.
    folded_motion = reshape(motion_only, data_length/fold, fold);
    %calculate spectrum over all bunches
    s = 2*sqrt(mean(abs(fft(hannwin(folded_motion)) / (data_length/fold)) .^2, 2));
    ss1 = reshape(s, raw_data.n_turns/fold, raw_data.harmonic_number);%fold into tune x modes

    if k==1
        mode_data = ss1;
        bunch_data = xf1;
    else
    mode_data = mode_data + ss1; % accumulating.
        bunch_data = bunch_data + xf1; % accumulating
    end %if

end % for
bunch_data = bunch_data ./ raw_data.repeat;
mode_data = mode_data ./ raw_data.repeat;
tune_data = fftshift(mode_data, 2);
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
