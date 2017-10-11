function exp_data = machine_environment(exp_data)
% captures the environmental variables of the machine
%
% exp_data is a structure containing experimental data. The state of the
% machine is added to the structure and then returned.
%
% Example: exp_data = machine_environment(exp_data)

if nargin == 0
    exp_data = struct('RF',[]);
end

% timestamp
exp_data.time = clock;

%% General machine paramerters
% Ring mode
exp_data.ringmode = lcaGet('SR-CS-RING-01:MODE');
% Machine current
exp_data.current =lcaGet('SR-DI-DCCT-01:SIGNAL');
% Fill pattern
exp_data.fill_pattern =lcaGet('SR-DI-PICO-01:BUCKETS');
%  and to deal with offset in cyrille's code
%  tmbf.fill_pattern = circshift(tmbf.fill_pattern',69)';

% RF frequency
exp_data.RF = lcaGet('LI-RF-MOSC-01:FREQ');
% Cavity voltages
try
    exp_data.cavity1_voltage = lcaGet('SR-RF-LLRF-10:CAVVOLTAGE');
catch
end
try
    exp_data.cavity2_voltage = lcaGet('SR-RF-LLRF-20:CAVVOLTAGE');
catch
end
try
    exp_data.cavity2_voltage = lcaGet('SR-RF-LLRF-30:CAVVOLTAGE');
catch
end
%getting the kicker status
injection = cell2mat(lcaGet('LI-TI-MTGEN-01:SRPREI-MODE'));
timing = cell2mat(lcaGet('LI-TI-MTGEN-01:STATUS.DESC'));
if strcmpi(injection,'Off') == 1
    exp_data.kicker_status = 'off';
elseif strcmpi(injection,'Every shot') == 1
    exp_data.kicker_status = 'on';
elseif strcmpi(injection,'On LINAC-PRE') == 1
    if strcmpi(timing,'Idle') == 1
        exp_data.kicker_status = 'off';
    else
        exp_data.kicker_status = 'on';
    end
else
    exp_data.kicker_status = 'unknown';
end

% wiggler fields
exp_data.wiggler_field_I15 = lcaGet('SR15I-ID-SCMPW-01:B_REAL');
exp_data.wiggler_field_I12 = lcaGet('SR12I-CS-SCMPW-01:B');

% capturing a sample pinhole image
a = lcaGet('SR01C-DI-DCAM-04:PROXY:DATA');
alims = lcaGet({'SR01C-DI-DCAM-04:WIDTH';'SR01C-DI-DCAM-04:HEIGHT'});
a = a(1:alims(1) * alims(2));
a = reshape(a,alims(1),[]);a(a<0) = (a(a<0)) + 256;
exp_data.pinhole = a;
