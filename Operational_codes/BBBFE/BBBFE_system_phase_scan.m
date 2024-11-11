function BBBFE_system_phase_scan(mbf_ax, single_bunch_location)
% Scans one of the individual axis system phase shifts in the
% bunch by bunch frontend and records the strength of the tune signal.
% Restores the original value after the scan.
%
% Args:
%      mbf_ax (str): specifies which axis 'X','Y','S'
%
% Machine setup
% fill some charge in bunch 'single_bunch_location' (0.2nC)
%
% Example: BBBFE_system_phase_scan('X', 400)

BBBFE_detector_setup(mbf_ax, single_bunch_location)

[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
% getting general environment data.
tunes.x_tune=NaN;
tunes.y_tune=NaN;
tunes.s_tune=NaN;
data = machine_environment('tunes', tunes);
data.time = datevec(datetime("now"));
data.base_name = ['system_phase_scan_', mbf_ax, '_axis'];

%prealloacation
data.phase=[-180:20:180 160:-20:-180];
data.side1 = NaN(length(data.phase), 1);
data.main = NaN(length(data.phase), 1);
data.side2 = NaN(length(data.phase), 1);

if strcmpi(mbf_ax, 'X') || strcmpi(mbf_ax, 'Y')
    if strcmpi(mbf_ax, 'X')
        mbf_pv = pv_names.hardware_names.x;
        fe_phase_pv = [pv_names.frontend.base pv_names.frontend.system_phase.x];
    elseif strcmpi(mbf_ax, 'Y')
        mbf_pv = pv_names.hardware_names.y;
        fe_phase_pv = [pv_names.frontend.base pv_names.frontend.system_phase.y];
    end %if
    data.original_setting=get_variable(fe_phase_pv);
    % moving to starting point in scan
    for pp=original_setting:-20:-180
        set_variable(fe_phase_pv, pp)
        pause(.5)
    end
    % measurement
    for x = 1:length(data.phase)
        set_variable(fe_phase_pv, data.phase(x))
        pause(2)
        data.side1(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det1.power]));
        data.main(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det2.power]));
        data.side2(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det3.power]));
    end

    % move back to the original setting
    for pp=-180:20:data.original_setting
        set_variable(fe_phase_pv, pp)
        pause(.5)
    end
elseif strcmpi(mbf_ax, 'S')
    mbf_pv =pv_names.hardware_names.s;
    fe_phase_pvI = [pv_names.frontend.base pv_names.frontend.system_phase.sI];
    fe_phase_pvQ = [pv_names.frontend.base pv_names.frontend.system_phase.sQ];
    data.original_setting=get_variable(fe_phase_pvI);
    data.original_settingQ=get_variable(fe_phase_pvQ);
    % moving to starting point in scan
    for pp=original_setting:-20:-180
        set_variable(fe_phase_pvI, pp)
        pause(.5)
    end
    % I and Q must be in quadrature
    for pp=original_settingQ:-20:-90
        set_variable(fe_phase_pvI, pp)
        pause(.5)
    end
    % measurement
    for x = 1:length(data.phase)
        set_variable(fe_phase_pvI, data.phase(x))
        set_variable(fe_phase_pvQ, data.phase(x) + 90)
        pause(2)
        data.side1(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det1.power]));
        data.main(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det2.power]));
        data.side2(x) = max(get_variable([mbf_pv, pv_names.tails.Detector.det3.power]));
    end
    % move back to the original setting
    for pp=-180:20:data.original_setting
        set_variable(fe_phase_pvI, pp)
        pause(.5)
    end
    % move back to the original setting
    for pp=-90:20:data.original_settingQ
        set_variable(fe_phase_pvQ, pp)
        pause(.5)
    end
end %if

BBBFE_detector_restore(mbf_ax)

%% saving the data to a file
save_to_archive(root_string, data)
%% plotting
BBBFE_system_phase_scan_plotting(mbf_ax, data)
