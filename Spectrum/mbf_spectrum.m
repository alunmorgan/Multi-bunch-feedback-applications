function data = mbf_spectrum(mbf_axis, n_turns, fold, repeat)
% generates an spectragram of all bunches.
%
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
%                       requesting
%       n_turns (int): The number of turns to capture.
%       fold (int): The number of times to fold the data along the
%                   frequency axis. This enhances power resolution
%                   at the cost of frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
%
% Example: mbf_spectrum('x',10000)

%% Getting the desired system setup parameters.
[root_string, harmonic_number, pv_names] = mbf_system_config;
root_string = root_string{1};

if ~exist('fold','var')
    fold=1;
end
if ~exist('repeat','var')
    repeat=1;
end

if strcmpi(mbf_axis, 'x')
    ax = 1;
    data.axis_label = 'X axis';
elseif strcmpi(mbf_axis, 'y')
    ax = 2;
    data.axis_label = 'Y axis';
elseif strcmpi(mbf_axis, 's')
    ax = 3;
    data.axis_label = 'S axis';
end %if

mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_input],'ADC');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_trigger_select],'Hardware');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_external_trigger_enable_status],'Ignore');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_post_mortem_trigger_enable_status],'Ignore');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_ADC_trigger_enable_status],'Ignore');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_sequencer_trigger_enable_status],'Enable');
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_system_clock_trigger_enable_status],'Ignore');
mbf_get_then_put([ax2dev(ax) pv_names.tails.Sequencer_trigger_state],0);
mbf_get_then_put([ax2dev(ax) pv_names.tails.MEM_trigger_mode],'One Shot');
mode_data = zeros(n_turns/fold, harmonic_number);
bunch_data = zeros(n_turns/2, harmonic_number);

for k=1:repeat
    lcaPut([ax2dev(ax) pv_names.tails.MEM_arm],1);
    raw_data = mbf_read_mem(ax2dev(ax), n_turns,'channel', 0, 'lock', 60);
    data_length=length(raw_data);
    
    % remove everything that is constant each revolotion
    xx = reshape(raw_data, harmonic_number, []); %turn into matrix bunches x turns
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
[~,pi] = max(data.mode_tune);

data.tune_axis = linspace(0,.5,length(data.bunch_tune));
data.bunch_axis = 1:harmonic_number;
data.mode_axis = -harmonic_number/2 : (harmonic_number/2 -1) ;

graph_handles(1) = figure;
ax1 = subplot('position',[.02 .35 .7 .6]);
imagesc(data.bunch_axis,...
    data.tune_axis,...
    log10(data.bunch_data),...
    [-3 0]+log10(max(max(data.bunch_data))));
set(ax1,'YAxisLocation','right');
set(ax1,'YDir','normal')
set(ax1, 'XTick', [])
set(ax1, 'YTick', [])
title(data.axis_label)

% Frequencies graph
ax2 = subplot('position',[.72 .35 .18 .6]);
plot(data.bunch_tune ,data.tune_axis);
set(ax2,'YAxisLocation','right');
set(ax2,'XAxisLocation','top')
set(ax2, 'XTick', [])
ylabel('Fractional tune')
axis tight

% bunches graph
ax3 = subplot('position',[.02 .11 .7 .24]);
plot(data.bunch_data(pi,:))
xlabel(sprintf('Bunches at peak tune %3.3f',data.tune_axis(pi)))
set(ax3, 'YTick', [])
axis tight

linkaxes([ax1, ax3], 'x')
linkaxes([ax1, ax2], 'y')

graph_handles(2) = figure;
ax4 = subplot('position',[.02 .35 .7 .6]);
imagesc(data.mode_axis,...
    data.tune_axis,...
    log10(data.tune_data(1:end/2,:)),...
    [-3 0]+log10(max(max(data.tune_data(1:end/2,:)))));
set(ax4,'YAxisLocation','right');
set(ax4,'YDir','normal')
set(ax4, 'XTick', [])
set(ax4, 'YTick', [])

ax5 = subplot('position',[.72 .35 .18 .6]);
plot(data.mode_tune,data.tune_axis);
set(gca,'YAxisLocation','right');
set(gca,'XAxisLocation','top')
set(ax5, 'XTick', [])
ylabel('Fractional tune')
axis tight

ax6 = subplot('position',[.02 .11 .7 .24]);
plot(data.mode_axis.',data.tune_data(pi,:))
xlabel(sprintf('Modes at peak tune %3.3f',data.tune_axis(pi)))
set(ax6, 'YTick', [])
axis tight

linkaxes([ax4, ax6], 'x')
linkaxes([ax4, ax5], 'y')

data.time = clock;
data.base_name = ['Spectrum_', mbf_axis, '_axis'];
%% saving the data to a file
save_to_archive(root_string, data, graph_handles)
mbf_restore_all
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
