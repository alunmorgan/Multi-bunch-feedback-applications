function BBBFE_clock_phase_scan(ax)
% Scans one of the clock phase shifts in the bunch by bunch frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      ax (int): 1..4 specifies which clock to scan.
%
% Setup: (manual for the time being...)
% press tune only
% fill some charge in bunch 1 (0.2nC)
% set bunch mode single bunch
% set single bunch 1
% press setup tune
% set up the individual tune detectors to run on 0,1,2
% SR23C-DI-TMBF-01:DET:BUNCH0_S 0
% SR23C-DI-TMBF-01:DET:BUNCH1_S 0
% SR23C-DI-TMBF-01:DET:BUNCH2_S 0
% set sweep gain to -18
% set detector fixed gain
%
% Example: BBBFE_clock_phase_scan(1)

[root_string, ~] = mbf_system_config;
root_string = root_string{1};

data.frontend_pv = 'SR23C-DI-BBFE-01';
p = lcaGet([data.frontend_pv ':PHA:CLO:' num2str(ax)]);
for pp = p:-20:-180
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], pp)
    pause(.5)
end %for

data.phase = [-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase));
data.main = NaN(length(data.phase));
data.side2 = NaN(length(data.phase));
for x = 1:length(data.phase)
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], data.phase(x))
    pause(2)
    data.side1(x) = max(lcaGet([ax2dev(ax) ':DET:POWER:0']));
    data.main(x) = max(lcaGet([ax2dev(ax) ':DET:POWER:1']));
    data.side2(x) = max(lcaGet([ax2dev(ax) ':DET:POWER:2']));
end %for
for pp = -180:20:p
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], pp)
    pause(.5)
end %for
lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], p)

graph_handles(1) = figure;
semilogy(data.phase, data.main, data.phase, data.side1, data.phase, data.side2)
legend('Excited bunch', 'preceeding', 'following')
xlabel('phase (degrees)')
ylabel('Signal')
title(['Clock sweep for TMBF0' num2str(ax)])

data.time = clock;
data.base_name = 'clock_phase_scan';
%% saving the data to a file
save_to_archive(root_string, data, graph_handles)

