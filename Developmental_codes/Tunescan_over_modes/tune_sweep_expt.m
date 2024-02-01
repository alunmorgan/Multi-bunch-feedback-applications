function tune_sweep_expt(mbf_axis)

% add the matlab paths for MBF tools
mbf_tools;
[~, harmonic_number, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

% experiment parameters
savefile    = appendtimestamp('tmbf_expt');
ncap        = 1001; % 4096; % 1001 takes ~ 3 minutes
startmode   = 0;
drive_bunch = 0:harmonic_number-1;
% drive_bunch = 100;
fb_on_off   = 1;

if strcmp(mbf_axis,'x')
    start_freq = 0.139;
    end_freq = 0.239;
else
    start_freq = 0.227;
    end_freq = 0.327;
end

%%% configure the sweep 
configure_tune_sweep(mbf_axis , drive_bunch, fb_on_off, 1, 1, 1, 1)

% arm the TMBF as one-shot rather than continuous
set_variable([mbf_names.(mbf_axis), mbf_vars.triggers.mode],'One Shot')
set_variable([mbf_names.(mbf_axis), mbf_vars.Sequencer.Base, pv_names.tails.Sequencer.reset],1)

% set the super-sequencer to have the correct number of modes
set_variable([mbf_names.(mbf_axis), mbf_vars.Super_sequencer_reset],1)
set_variable([mbf_names.(mbf_axis), mbf_vars.Super_sequencer_count],...
    harmonic_number)

% change the number of captures to speed things up (normally 4096)
set_variable([mbf_names.(mbf_axis), mbf_vars.Sequencer.seq1.count],ncap)

% select the tune sweep frequency / mode
set_variable([mbf_names.(mbf_axis), mbf_vars.Sequencer.seq1.start_frequency],...
    startmode + start_freq)
set_variable([mbf_names.(mbf_axis), mbf_vars.Sequencer.seq1.end_frequency],...
    startmode + end_freq)

% start the multi-mode sweep
set_variable([mbf_names.(mbf_axis), mbf_vars.triggers.SEQ.arm], 1)

% download the data
% (Eww.  Convert axis string into 0 or 1.)
det_axis = find('xy' == mbf_axis) - 1;
[data, scale] = mbf_read_det(mbf_names.mem.(mbf_axis), 'axis', det_axis, 'lock', 1800 );

% reset the sweep
configure_tune_sweep(mbf_axis , 0:harmonic_number-1, 1, 1, 0, 0, 0)
set_variable([mbf_names.(mbf_axis), mbf_vars.triggers.SEQ.mode],'Rearm')
set_variable([mbf_names.(mbf_axis), mbf_vars.Sequencer.Base, pv_names.tails.Sequencer.reset],1)

% reshape the results
fracttune = scale(1:ncap);
for n = 1:size(data,2)
    result = reshape(abs(data(:,n)), ncap, harmonic_number);

    % plot the results
    figure(n)
    imagesc(1:harmonic_number, fracttune, result)
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
end

% get the stored beam conditions
fill_pattern = get_variable(pv_names.bunch_pattern);
current = get_variable(pv_names.current);

% save the data
save(savefile,'data','scale','mbf_axis','ncap','startmode','drive_bunch','fb_on_off','start_freq','end_freq','fill_pattern','current')

