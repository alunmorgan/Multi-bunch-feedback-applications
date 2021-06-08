function setup_operational_mode(mbf_axis, operational_mode)
% Runs the setup scripts underlying the blue buttons.
% This allows the system to be put into a known state.
%   Args:
%       mbf_axis (char): x, y or  s
%       operational_mode (char): 'TuneOnly', 'TuneSpecial' or 'Feedback'

expected_axis_values = ["x", "X", "y", "Y" "s", "S"];
axis = validatestring(mbf_axis, expected_axis_values);

expected_operational_modes = ["TuneOnly", "TuneSpecial", "Feedback"];
action = validatestring(operational_mode, expected_operational_modes);

if strcmpi(axis, 'x')
    axis = "X";
    device = "SR23C-DI-TMBF-01";
elseif strcmpi(axis, 'y')
    axis = "Y";
    device = "SR23C-DI-TMBF-01";
elseif strcmpi(axis, 's')
    axis = "IQ";
    device = "SR23C-DI-LMBF-01";
end %if

if strcmp(action, "TuneOnly")
    action = "TUNE";
elseif strcmp(action, "TuneSpecial")
   action = "AP";
elseif strcmp(action, "Feedback")
    action = "FB";
end %if

% construct the bash command
bash_command1 = 'gui_dir="$(configure-ioc s -p DI-MBF-gui-dir)"';
bash_command2 = "$gui_dir/epics/opi/scripts/mbf-run-command 'description' mbf-setup-tune " + device + ":" + axis + ' ' + action;

% status1 = system(bash_command1);
% status2 = system(bash_command2);
