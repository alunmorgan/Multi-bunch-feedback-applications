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

BBBFE_setup(mbf_ax, single_bunch_location)

[root_string, ~] = mbf_system_config;
root_string = root_string{1};
% getting general environment data.
tunes.x_tune=NaN;
tunes.y_tune=NaN;
tunes.s_tune=NaN;
data = machine_environment('tunes', tunes);
data.frontend_pv = 'SR23C-DI-BBFE-01';
if strcmpi(mbf_ax, 'X') || strcmpi(mbf_ax, 'Y')
    data.mbf_pv = ['SR23C-DI-TMBF-01:', mbf_ax];
elseif strcmpi(mbf_ax, 'S')
    data.mbf_pv = ['SR23C-DI-LMBF-01:', 'IQ'];
end %if

if strcmpi(mbf_ax, 'X') || strcmpi(mbf_ax, 'Y')
    original_setting=lcaGet([data.frontend_pv ':PHA:OFF:' mbf_ax]);
elseif strcmpi(mbf_ax, 'S')
    original_setting=lcaGet([data.frontend_pv ':PHA:OFF:IT']);
end %if
% moving to starting point in scan
for pp=original_setting:-20:-180
    if strcmp(mbf_ax, 'X') || strcmp(mbf_ax, 'Y')
        lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], pp)
    elseif strcmp(mbf_ax, 'S')
        lcaPut([data.frontend_pv ':PHA:OFF:IT'], pp)
    end %if
    pause(.5)
end

% measurement
data.phase=[-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase), 1);
data.main = NaN(length(data.phase), 1);
data.side2 = NaN(length(data.phase), 1);
for x = 1:length(data.phase)
    if strcmp(mbf_ax, 'X') || strcmp(mbf_ax, 'Y')
        lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], data.phase(x))
    elseif strcmp(mbf_ax, 'S')
        lcaPut([data.frontend_pv ':PHA:OFF:IT'], data.phase(x))
    end %if
    pause(2)
    data.side1(x) = max(lcaGet([data.mbf_pv, ':DET:1:POWER']));
    data.main(x) = max(lcaGet([data.mbf_pv, ':DET:2:POWER']));
    data.side2(x) = max(lcaGet([data.mbf_pv, ':DET:3:POWER']));
end

% move back to the original setting
for pp=-180:20:original_setting
    if strcmp(mbf_ax, 'X') || strcmp(mbf_ax, 'Y')
        lcaPut([data.frontend_pv ':PHA:OFF:' mbf_ax], pp)
    elseif strcmp(mbf_ax, 'S')
        lcaPut([data.frontend_pv ':PHA:OFF:IT'], pp)
    end %if
    pause(.5)
end

BBBFE_restore(mbf_ax)

data.time = datevec(datetime("now"));
data.base_name = ['system_phase_scan_', mbf_ax, '_axis'];
%% saving the data to a file
save_to_archive(root_string, data)
%% plotting
BBBFE_system_phase_scan_plotting(mbf_ax, data)
