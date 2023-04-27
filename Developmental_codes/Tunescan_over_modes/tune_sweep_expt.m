function tune_sweep_expt

% add the matlab paths for MBF tools
mbf_tools;

% experiment parameters
savefile    = appendtimestamp('tmbf_expt');
axis        = 'X';
ncap        = 1001; % 4096; % 1001 takes ~ 3 minutes
startmode   = 0;
drive_bunch = 0:935;
% drive_bunch = 100;
fb_on_off   = 1;

if strcmp(axis,'X')
    start_freq = 0.139;
    end_freq = 0.239;
else
    start_freq = 0.227;
    end_freq = 0.327;
end

%%% configure the sweep 
configure_tune_sweep(axis , drive_bunch, fb_on_off, 1, 1, 1, 1)

% arm the TMBF as one-shot rather than continuous
lcaPut(['SR23C-DI-TMBF-01:' axis ':TRG:SEQ:MODE_S'],'One Shot')
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:RESET_S.PROC'],1)

% set the super-sequencer to have the correct number of modes
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:SUPER:RESET_S.PROC'],1)
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:SUPER:COUNT_S'],936)

% change the number of captures to speed things up (normally 4096)
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:1:COUNT_S'],ncap)

% select the tune sweep frequency / mode
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:1:START_FREQ_S'],startmode + start_freq)
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:1:END_FREQ_S'],  startmode + end_freq)

% start the multi-mode sweep
lcaPut(['SR23C-DI-TMBF-01:' axis ':TRG:SEQ:ARM_S.PROC'], 1)

% download the data
% (Eww.  Convert axis string into 0 or 1.)
det_axis = find('XY' == axis) - 1;
[data, scale] = mbf_read_det('SR23C-DI-TMBF-01', 'axis', det_axis, 'lock', 1800 );

% reset the sweep
configure_tune_sweep(axis , 0:935, 1, 1, 0, 0, 0)
lcaPut(['SR23C-DI-TMBF-01:' axis ':TRG:SEQ:MODE_S'],'Rearm')
lcaPut(['SR23C-DI-TMBF-01:' axis ':SEQ:RESET_S.PROC'],1)

% reshape the results
fracttune = scale(1:ncap);
for n = 1:size(data,2)
    result = reshape(abs(data(:,n)), ncap, 936);

    % plot the results
    figure(n)
    imagesc(1:936,fracttune,result)
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
end

% get the stored beam conditions
fill_pattern = lcaGet('SR-DI-PICO-01:BUCKETS_180');
current = lcaGet('SR-DI-DCCT-01:SIGNAL');

% save the data
save(savefile,'data','scale','axis','ncap','startmode','drive_bunch','fb_on_off','start_freq','end_freq','fill_pattern','current')

