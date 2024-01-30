function setup_operational_mode(mbf_axis, operational_mode)
% Runs the setup scripts underlying the blue buttons.
% This allows the system to be put into a known state.
%   Args:
%       mbf_axis (char): x, y or  s
%       operational_mode (char): 'TuneOnly', 'TuneSpecial' or 'Feedback'
mbf_axis = lower(mbf_axis);
expected_axis_values = ["x", "y", "s", "it"];
expected_operational_modes = ["TuneOnly", "TuneSpecial", "Feedback"];

mbf_axis = validatestring(mbf_axis, expected_axis_values);
action = validatestring(operational_mode, expected_operational_modes);

if strcmp(mbf_axis, "it")
    mbf_axis = "s";
end %if

[~, ~, pv_names, ~] = mbf_system_config;

device = pv_names.hardware_names.(mbf_axis);

if strcmp(action, "TuneOnly")
    action = "TUNE";
elseif strcmp(action, "TuneSpecial")
   action = "AP";
elseif strcmp(action, "Feedback")
    action = "FB";
end %if

% Pick up the base directory
[rc, gui_dir] = system("configure-ioc s -p DI-MBF-gui-dir");
assert(rc == 0, "Error running `configure-ioc`");
gui_dir = strip(gui_dir, "right");  % Get rid of trailing newline

% construct the bash command
description = "Setting MBF defaults";
bash_command = sprintf("%s/%s '%s' mbf-setup-tune %s %s", ...
    gui_dir, "/epics/opi/scripts/mbf-run-command", ...
    description, device, action);
rc = system(bash_command);
assert(rc == 0, 'Error running mbf-setup-tune');
