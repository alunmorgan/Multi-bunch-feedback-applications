function BBBFE_system_phase_scan(mbf_ax, single_bunch_location)
% Scans one of the individual axis system phase shifts in the 
% bunch by bunch frontend and records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      mbf_ax (str): specifies which axis 'X','Y', 'S', 'IT', 'IL'
%      'S' maps to 'IT' 
%
% Machine setup
% fill some charge in bunch 'single_bunch_location' (0.2nC)
%
% Example: BBBFE_system_phase_scan('X', 400)

if strcmp(mbf_ax, 'X')
    ax = 1;
elseif strcmp(mbf_ax, 'Y')
    ax = 2;
elseif strcmp(mbf_ax, 'S')
%     mbf_ax = 'IT';
    ax = 3;
elseif strcmp(mbf_ax, 'IT')
    ax = 3;
elseif strcmp(mbf_ax, 'IL')
    ax = 3;
    warning( 'IL is not currently used')
else
    error('BBBFE_system_phase_scan: Input error. Should be X, Y,or IT')
end %if

BBBFE_setup(mbf_ax, single_bunch_location)

[root_string, ~] = mbf_system_config;
root_string = root_string{1};

data.frontend_pv = 'SR23C-DI-BBFE-01';
data.mbf_pv = ['SR23C-DI-TMBF-01:', mbf_ax];
original_setting=lcaGet([data.frontend_pv ':PHA:OFF:' mbf_ax]);

% moving to starting point in scan
for pp=original_setting:-20:-180
    lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], pp)
    pause(.5)
end

% measurement
data.phase=[-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase));
data.main = NaN(length(data.phase));
data.side2 = NaN(length(data.phase));
for x = 1:length(data.phase)
    lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], data.phase(x))
    pause(2)
    data.side1(x) = max(lcaGet([data.mbf_pv, ':DET:1:POWER']));
    data.main(x) = max(lcaGet([data.mbf_pv, ':DET:2:POWER']));
    data.side2(x) = max(lcaGet([data.mbf_pv, ':DET:3:POWER']));
end

% move back to the original setting
for pp=-180:20:original_setting
    lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], pp)
    pause(.5)
end

BBBFE_restore(mbf_ax)

% plotting
figure;
hold all
semilogy(data.phase, data.main)
semilogy(data.phase, data.side1)
semilogy(data.phase, data.side2)
legend('Excited bunch', 'preceeding', 'following')
xlabel('phase (degrees)')
ylabel('Signal')
title(['Phase sweep for MBF ', mbf_ax, ' axis'])
grid on
hold off

data.time = clock;
data.base_name = 'system_phase_scan';
%% saving the data to a file
save_to_archive(root_string, data)

