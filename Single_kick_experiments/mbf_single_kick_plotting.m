function mbf_single_kick_plotting(single_kick, single_kick_pp)

if isfield(single_kick_pp, 'beam_oscillation_x_f_scan')
    plot_single_kick_scan(single_kick.excitation_frequency, ...
        single_kick_pp.beam_oscillation_x_f_scan, 'Excitation frequency [tune]',...
        'Horizontal kick')
end %if

if isfield(single_kick_pp, 'beam_oscillation_y_f_scan')
    plot_single_kick_scan(single_kick.excitation_frequency, ...
        single_kick_pp.beam_oscillation_y_f_scan, 'Excitation frequency [tune]',...
        'Vertical kick')
end %if

if isfield(single_kick_pp, 'beam_oscillation_x_gain_scan')
    plot_single_kick_scan(single_kick.excitation_gain, ...
        single_kick_pp.beam_oscillation_x_gain_scan, 'Excitation gain [dB]',...
        'Horizontal kick')
end %if

if isfield(single_kick_pp, 'beam_oscillation_x_gain_scan')
    plot_single_kick_scan(single_kick.excitation_gain, ...
        single_kick_pp.beam_oscillation_y_gain_scan, 'Excitation gain [dB]', ...
        'Vertical kick')
end %if

% plots for a single capture.
if isfield(single_kick, 'bpm_data')
    % Raw time plots
    used_bpms = fieldnames(single_kick.bpm_data);
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(single_kick.bpm_data.(used_bpms{kds}).X);
    end %for
    legend(used_bpms)
    ylabel('BPM motion [\mum]')
    xlabel('Time')
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(single_kick.bpm_data.(used_bpms{kds}).Y);
    end %for
    legend(used_bpms)
    ylabel('BPM motion [\mum]')
    xlabel('Time')
    
    % RMS motion plots
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(kds, single_kick_pp.beam_oscillation_x(kds), '*');
    end %for
    legend(used_bpms)
    ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
    title('Horizontal kick')
    figure
    hold on
    for kds = 1:length(used_bpms)
        plot(kds, single_kick_pp.beam_oscillation_y(kds), '*');
    end %for
    legend(used_bpms)
    ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
    title('Vertical kick')
end %if

