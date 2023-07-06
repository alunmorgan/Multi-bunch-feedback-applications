function BBBFE_clock_phase_scan(mbf_ax, single_bunch_location)
% Scans one of the clock phase shifts in the bunch by bunch frontend and
% records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      ax (str): Specifies which axis.
%      single_bunch_location (int): the location of the single bunch.
%
% Machine setup: (manual for the time being...)
% fill some charge in bunch 1 (0.2nC)
%
% Example: BBBFE_clock_phase_scan('X', 400)

BBBFE_setup(mbf_ax, single_bunch_location)
[root_string, ~] = mbf_system_config;
root_string = root_string{1};

% getting general environment data.
tunes.x_tune=NaN;
tunes.y_tune=NaN;
tunes.s_tune=NaN;
data = machine_environment('tunes', tunes);

if strcmp(mbf_ax, 'Y')
    ax = 3;
    data.mbf_pv = ['SR23C-DI-TMBF-01:', mbf_ax];
elseif strcmp(mbf_ax, 'X')
    ax = 3;
    data.mbf_pv = ['SR23C-DI-TMBF-01:', mbf_ax];
elseif strcmp(mbf_ax, 'S')
    ax = 4;
    data.mbf_pv = 'SR23C-DI-LMBF-01:IQ';
else
    error('Please use input axes X, Y or S')
end %if

data.frontend_pv = 'SR23C-DI-BBFE-01';
original_setting = lcaGet([data.frontend_pv ':PHA:CLO:' num2str(ax)]);

% moving to starting point in scan
for pp = original_setting:-20:-180
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], pp)
    pause(.5)
end %for

% measurement
data.phase = [-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase), 1);
data.main = NaN(length(data.phase), 1);
data.side2 = NaN(length(data.phase), 1);
for x = 1:length(data.phase)
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], data.phase(x))
    pause(2)
    data.side1(x) = max(lcaGet([data.mbf_pv, ':DET:1:POWER']));
    data.main(x) = max(lcaGet([data.mbf_pv, ':DET:2:POWER']));
    data.side2(x) = max(lcaGet([data.mbf_pv, ':DET:3:POWER']));
end %for

% move back to the original setting
for pp = -180:10:original_setting
    lcaPut([data.frontend_pv ':PHA:CLO:' num2str(ax)], pp)
    pause(.5)
end %for

BBBFE_restore(mbf_ax)

data.time = datevec(datetime("now"));
data.base_name = ['clock_phase_scan_', mbf_ax, '_axis'];

%% saving the data to a file
save_to_archive(root_string, data)
%% plotting
BBBFE_clock_phase_scan_plotting(data, ax, mbf_ax)
