function exp_data = machine_environment(exp_data)
% captures the environmental variables of the machine
%
% exp_data is a structure containing experimental data. The state of the
% machine is added to the structure and then returned.
%
% Example: exp_data = machine_environment(exp_data)

if nargin == 0
    exp_data = struct('RF', []);
end

% timestamp
exp_data.time = clock;

%% General machine parameters
% Ring mode
exp_data.ringmode = lcaGet('SR-CS-RING-01:MODE');
% Machine current
exp_data.current =lcaGet('SR-DI-DCCT-01:SIGNAL');
% Fill pattern
exp_data.fill_pattern =lcaGet('SR-DI-PICO-01:BUCKETS');

% RF frequency
exp_data.RF = lcaGet('LI-RF-MOSC-01:FREQ');
% Cavity voltages
try
    exp_data.cavity1_voltage = lcaGet('SR-RF-LLRF-10:CAVVOLTAGE');
catch
end
% try
%     exp_data.cavity2_voltage = lcaGet('SR-RF-LLRF-20:CAVVOLTAGE');
% catch
% end
try
    exp_data.cavity3_voltage = lcaGet('SR-RF-LLRF-30:CAVVOLTAGE');
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

% Feedback status
exp_data.orbit_feedback_status = lcaGet('SR01A-CS-FOFB-01:RUN');
exp_data.tune_feedback_status = lcaGet('SR-CS-TFB-01:STATUS');

% Emittance
exp_data.emittance_h = lcaGet('SR-DI-EMIT-01:HEMIT_MEAN');
exp_data.emittance_v = lcaGet('SR-DI-EMIT-01:VEMIT_MEAN');
exp_data.coupling = lcaGet('SR-DI-EMIT-01:COUPLING_MEAN');
exp_data.espread = lcaGet('SR-DI-EMIT-01:ESPREAD_MEAN');

% Lifetime
exp_data.lifetime = lcaGet('SR-DI-DCCT-01:LIFETIME'); % Lifetime on main display chosen for lowest error.
exp_data.life.dcct.life30sec = lcaGet('SR-DI-DCCT-01:LIFE30');
exp_data.life.dcct.lifeerr30sec = lcaGet('SR-DI-DCCT-01:ERROR30');
exp_data.life.dcct.cond30sec = lcaGet('SR-DI-DCCT-01:COND30');
exp_data.life.dcct.life2min = lcaGet('SR-DI-DCCT-01:LIFE120');
exp_data.life.dcct.lifeerr2min = lcaGet('SR-DI-DCCT-01:ERROR120');
exp_data.life.dcct.cond2min = lcaGet('SR-DI-DCCT-01:COND120');
exp_data.life.dcct.life5min = lcaGet('SR-DI-DCCT-01:LIFE300');
exp_data.life.dcct.lifeerr5min = lcaGet('SR-DI-DCCT-01:ERROR300');
exp_data.life.dcct.cond5min = lcaGet('SR-DI-DCCT-01:COND300');
exp_data.life.dcct.life20min = lcaGet('SR-DI-DCCT-01:LIFE1200');
exp_data.life.dcct.lifeerr20min = lcaGet('SR-DI-DCCT-01:ERROR1200');
exp_data.life.dcct.cond20min = lcaGet('SR-DI-DCCT-01:COND1200');

exp_data.life.bpm.life300sec = lcaGet('SR-DI-EBPM-01:LIFE300');
exp_data.life.bpm.life300err = lcaGet('SR-DI-EBPM-01:ERROR300');
exp_data.life.bpm.cond300sec = lcaGet('SR-DI-EBPM-01:COND300');
exp_data.life.bpm.life120sec = lcaGet('SR-DI-EBPM-01:LIFE120');
exp_data.life.bpm.life120err = lcaGet('SR-DI-EBPM-01:ERROR120');
exp_data.life.bpm.cond120sec = lcaGet('SR-DI-EBPM-01:COND120');
exp_data.life.bpm.life30sec = lcaGet('SR-DI-EBPM-01:LIFE30');
exp_data.life.bpm.life30err = lcaGet('SR-DI-EBPM-01:ERROR30');
exp_data.life.bpm.cond30sec = lcaGet('SR-DI-EBPM-01:COND30');
exp_data.life.bpm.life10sec = lcaGet('SR-DI-EBPM-01:LIFE10');
exp_data.life.bpm.life10err = lcaGet('SR-DI-EBPM-01:ERROR10');
exp_data.life.bpm.cond10sec = lcaGet('SR-DI-EBPM-01:COND10');

% Injection
exp_data.injection.btssr2s = lcaGet('CS-DI-XFER-01:BS-SR2');
exp_data.injection.btssr10s = lcaGet('CS-DI-XFER-01:BS-SR10');
exp_data.injection.boostsr2s = lcaGet('CS-DI-XFER-01:BR-SR2');
exp_data.injection.boostsr10s = lcaGet('CS-DI-XFER-01:BR-SR10');

% IDs
exp_data.id.gap02 = lcaGet('SR02I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap02j = lcaGet('SR02J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap03 = lcaGet('SR03I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap04 = lcaGet('SR04I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap05 = lcaGet('SR05I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase05(1) = lcaGet('SR05I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase05(2) = lcaGet('SR05I-MO-SERVO-07:MOT.RBV');
exp_data.id.gap06a = lcaGet('SR06I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase06a(1) = lcaGet('SR06I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase06a(2) = lcaGet('SR06I-MO-SERVO-06:MOT.RBV');
exp_data.id.gap06b = lcaGet('SR06I-MO-SERVC-21:CURRGAPD');
exp_data.id.phase06b(1) = lcaGet('SR06I-MO-SERVO-25:MOT.RBV');
exp_data.id.phase06b(2) = lcaGet('SR06I-MO-SERVO-26:MOT.RBV');
exp_data.id.gap07 = lcaGet('SR04I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap08 = lcaGet('SR08I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase08(1) = lcaGet('SR08I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase08(2) = lcaGet('SR08I-MO-SERVO-07:MOT.RBV');
exp_data.id.gap09i = lcaGet('SR09I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap09j = lcaGet('SR09J-MO-SERVC-01:CURRGAPD');
exp_data.id.phase09j(1) = lcaGet('SR09J-MO-SERVO-05:MOT.RBV');
exp_data.id.phase09j(2) = lcaGet('SR09J-MO-SERVO-06:MOT.RBV');
exp_data.id.phase09j(3) = lcaGet('SR09J-MO-SERVO-07:MOT.RBV');
exp_data.id.phase09j(4) = lcaGet('SR09J-MO-SERVO-08:MOT.RBV');
exp_data.id.gap10a = lcaGet('SR10I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase10a(1) = lcaGet('SR10I-MO-SERVO-03:MOT.RBV');
exp_data.id.phase10a(2) = lcaGet('SR10I-MO-SERVO-04:MOT.RBV');
exp_data.id.phase10a(3) = lcaGet('SR10I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase10a(4) = lcaGet('SR10I-MO-SERVO-06:MOT.RBV');
exp_data.id.gap10b = lcaGet('SR10I-MO-SERVC-21:CURRGAPD');
exp_data.id.phase10b(1) = lcaGet('SR10I-MO-SERVO-23:MOT.RBV');
exp_data.id.phase10b(2) = lcaGet('SR10I-MO-SERVO-24:MOT.RBV');
exp_data.id.phase10b(3) = lcaGet('SR10I-MO-SERVO-25:MOT.RBV');
exp_data.id.phase10b(4) = lcaGet('SR10I-MO-SERVO-26:MOT.RBV');
exp_data.id.gap11 = lcaGet('SR11I-MO-SERVC-01:CURRGAPD');
exp_data.id.i12field = lcaGet('SR12I-CS-SCMPW-01:B');
exp_data.id.gap13i = lcaGet('SR13I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap13j = lcaGet('SR13J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap14 = lcaGet('SR14I-MO-SERVC-01:CURRGAPD');
exp_data.id.i15field = lcaGet('SR15I-ID-SCMPW-01:B_REAL');
exp_data.id.gap16 = lcaGet('SR16I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap18 = lcaGet('SR18I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap19 = lcaGet('SR19I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap20i = lcaGet('SR20I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap20j = lcaGet('SR20J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap21 = lcaGet('SR21I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase21(1) = lcaGet('SR21I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase21(2) = lcaGet('SR21I-MO-SERVO-06:MOT.RBV');
exp_data.id.phase21(3) = lcaGet('SR21I-MO-SERVO-07:MOT.RBV');
exp_data.id.phase21(4) = lcaGet('SR21I-MO-SERVO-08:MOT.RBV');
exp_data.id.gap22 = lcaGet('SR22I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap23 = lcaGet('SR23I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap24 = lcaGet('SR24I-MO-SERVC-01:CURRGAPD');

exp_data.orbit_x = lcaGet('SR-DI-EBPM-01:SA:X');
exp_data.orbit_y = lcaGet('SR-DI-EBPM-01:SA:Y');

