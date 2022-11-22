function setup_operational_mode(mbf_axis, operational_mode)
% Runs the setup scripts underlying the blue buttons.
% This allows the system to be put into a known state.
%   Args:
%       mbf_axis (char): x, y or  s
%       operational_mode (char): 'TuneOnly', 'TuneSpecial' or 'Feedback'
mbf_axis = upper(mbf_axis);
expected_axis_values = ["X", "Y", "S", "IT"];
mbf_axis = validatestring(mbf_axis, expected_axis_values);
if strcmp(mbf_axis, "IT")
    mbf_axis = "S";
end %if
expected_operational_modes = ["TuneOnly", "TuneSpecial", "Feedback"];
action = validatestring(operational_mode, expected_operational_modes);

if strcmp(mbf_axis, "X")
    device = "SR23C-DI-TMBF-01:X";
elseif strcmp(mbf_axis, "Y")
    device = "SR23C-DI-TMBF-01:Y";
elseif strcmp(mbf_axis, "S")
    device = "SR23C-DI-LMBF-01:IQ";
end %if

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
