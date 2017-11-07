function BBBFE_LO_scan(phase_centre, sweep_extent)
% Scans the LO phase shift in the bunch by bunch frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%     phase_centre (int): The phase value to center the sweep on.
%     sweep_extent (int): The range to sweep. 45 would sweep 45 degrees
%                         above and 45 degrees below the centre value.
%
% Example: BBBFE_LO_scan(90, 45)

[root_string, ~] = mbf_system_config;
root_string = root_string{1};

data.phase_pv = 'SR23C-DI-BBFE-01:PHA';
old_val = lcaGet(data.phase_pv);
data.n = phase_centre - sweep_extent:ceil(sweep_extent/20):phase_centre + sweep_extent;
data.t1 = NaN(length(data.n),1);
data.t2 = NaN(length(data.n),1);
data.t3 = NaN(length(data.n),1);
for jd = 1:length(data.n)
    lcaPut(data.phase_pv, data.n(jd));
    pause(2);
    data.t1(jd) = max(lcaGet('SR23C-DI-TMBF-01:TUNE:POWER'));
    data.t2(jd) = max(lcaGet('SR23C-DI-TMBF-02:TUNE:POWER'));
    data.t3(jd) = max(lcaGet('SR23C-DI-TMBF-03:TUNE:POWER'));
end
lcaPut(data.phase_pv, old_val);
graph_handles(1) = figure;
plot(data.n, data.t1 ./ max(data.t1), 'b',...
     data.n, data.t2 ./ max(data.t2), 'r',...
     data.n, data.t3 ./ max(data.t3), 'c')
xlabel('LO phase (degrees)')
ylabel('tune max value (normalised)')
legend('X', 'Y', 'S')

data.time = clock;
data.base_name = 'LO_scan';
%% saving the data to a file
save_to_archive(root_string, data, graph_handles)
