function td = mbf_transverse_damping_capture(mbf_axis, varargin)
% Gathers data on the machine environment.
% Runs a growdamp experiment with sideband excitation on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       additional_save_location (str): Full path to additional save location.
%       save_to_archive (str): yes or no. 
%   Returns:
%       td (struct): data structure containing the experimental
%                          results and the machine conditions.
%
% example td = mbf_transverse_damping_capture('x')

binary_string = {'yes', 'no'};
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
parse(p, mbf_axis, varargin{:});

pinhole_trig_orig = lcaGet('SR01C-DI-EVR-01:SET_HW.OT3D');
disp(['Original pinhole trigger ', pinhole_trig_orig])

for n=1:25
    if n ==1
        td = mbf_growdamp_capture(mbf_axis,...
            'excitation_location', 'Sideband', 'save_to_archive', 'no');
    else
        mbf_growdamp_capture(mbf_axis,...
            'excitation_location', 'Sideband', 'save_to_archive', 'no');
    end %if
    td.beam_size.pinhole1.x(n) = lcaGet('SR-DI-EMIT-01:P1:SIGMAX');
    td.beam_size.pinhole1.y(n) = lcaGet('SR-DI-EMIT-01:P1:SIGMAY');
    td.beam_size.pinhole2.x(n) = lcaGet('SR-DI-EMIT-01:P2:SIGMAX');
    td.beam_size.pinhole2.y(n) = lcaGet('SR-DI-EMIT-01:P2:SIGMAY');
    td.ph1.image(n) = get_Pinhole_image('SR01C-DI-DCAM-04');
    td.ph2.image(n) = get_Pinhole_image('SR01C-DI-DCAM-05');
end %for
for n=1:25
    td.ph1.beam_info(n) = get_beamsize_from_image(td.ph1.image(n));
    td.ph2.beam_info(n) = get_beamsize_from_image(td.ph2.image(n));
end %for

%% saving the data to a file
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, td)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, td)
    end %if
end %if
