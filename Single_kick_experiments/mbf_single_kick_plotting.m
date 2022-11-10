function mbf_single_kick_plotting(single_kick, single_kick_pp)

if strcmp(single_kick.scan_label, 'Frequency')
    plot_single_kick_scan(single_kick.excitation_frequency, ...
        single_kick_pp.beam_oscillation_x, 'Excitation frequency [tune]',...
        'Horizontal kick')
    plot_single_kick_scan(single_kick.excitation_frequency, ...
        single_kick_pp.beam_oscillation_y, 'Excitation frequency [tune]',...
        'Vertical kick')
end %if
if strcmp(single_kick.scan_label, 'Harmonic')
    plot_single_kick_scan(single_kick.harmonic, ...
        single_kick_pp.beam_oscillation_x, 'Excitation frequency [tune]',...
        'Horizontal kick')
    plot_single_kick_scan(single_kick.harmonic, ...
        single_kick_pp.beam_oscillation_y, 'Excitation frequency [tune]',...
        'Vertical kick')
end %if
if strcmp(single_kick.scan_label, 'Gain')
    plot_single_kick_scan(single_kick.excitation_gain, ...
        single_kick_pp.beam_oscillation_x, 'Excitation gain [dB]',...
        'Horizontal kick')
    plot_single_kick_scan(single_kick.excitation_gain, ...
        single_kick_pp.beam_oscillation_y, 'Excitation gain [dB]', ...
        'Vertical kick')
end %if
if strcmp(single_kick.scan_label, '')
    % plots for a single capture.
    %     % Raw time plots
    used_bpms = single_kick_pp.used_bpms;
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(squeeze(single_kick_pp.beam_signal_x(1, kds, :)));
    end %for
    legend(used_bpms)
    ylabel('BPM motion [\mum]')
    xlabel('Time')
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(squeeze(single_kick_pp.beam_signal_y(1, kds, :)));
    end %for
    legend(used_bpms)
    ylabel('BPM motion [\mum]')
    xlabel('Time')
    
    % RMS motion plots
    figure
    plot(1:length(used_bpms), single_kick_pp.beam_oscillation_x(1, :), '*');
    ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
    title('Horizontal kick')
    figure
    plot(1:length(used_bpms), single_kick_pp.beam_oscillation_y(1,:), '*');
    ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
    title('Vertical kick')
end %if