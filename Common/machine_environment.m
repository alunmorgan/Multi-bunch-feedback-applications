function exp_data = machine_environment(varargin)
% captures the environmental variables of the machine
%
% exp_data is a structure containing experimental data. The state of the
% machine is added to the structure and then returned.
%
% tunes are the previous captured tune measurements. As depending on the
% experimental setup it may not be possible to capture them before each capture.
%
% Example: exp_data = machine_environment(exp_data)

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
addParameter(p, 'exp_data', struct('RF', []));
addParameter(p, 'tunes', NaN);

parse(p, varargin{:});
exp_data = p.Results.exp_data;
% timestamp
exp_data.time = datevec(datetime("now"));

lcaSetSeverityWarnLevel(4)
%% General machine parameters
% Tunes
if ~isstruct(p.Results.tunes)
    exp_data.tunes = get_all_tunes;
end %if
% Ring mode
exp_data.ringmode = get_variable('SR-CS-RING-01:MODE');
% Machine current
exp_data.current =get_variable('SR-DI-DCCT-01:SIGNAL');
% Fill pattern
exp_data.fill_pattern =get_variable('SR-DI-PICO-01:BUCKETS');

% RF frequency
exp_data.RF = get_variable('LI-RF-MOSC-01:FREQ');
% Cavity voltages
try
    exp_data.cavity1_voltage = get_variable('SR-RF-LLRF-10:CAVVOLTAGE');
catch
end
% try
%     exp_data.cavity2_voltage = get_variable('SR-RF-LLRF-20:CAVVOLTAGE');
% catch
% end
try
    exp_data.cavity3_voltage = get_variable('SR-RF-LLRF-30:CAVVOLTAGE');
catch
end
%getting the kicker status
injection = cell2mat(get_variable('LI-TI-MTGEN-01:SRPREI-MODE'));
timing = cell2mat(get_variable('LI-TI-MTGEN-01:STATUS.DESC'));
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
exp_data.wiggler_field_I15 = get_variable('SR15I-ID-SCMPW-01:B_REAL');
exp_data.wiggler_field_I12 = get_variable('SR12I-CS-SCMPW-01:B');

% capturing a sample pinhole image
a = get_variable('SR01C-DI-DCAM-04:PROXY:DATA');
alims = get_variable({'SR01C-DI-DCAM-04:WIDTH';'SR01C-DI-DCAM-04:HEIGHT'});
a = a(1:alims(1) * alims(2));
a = reshape(a,alims(1),[]);
a(a<0) = (a(a<0)) + 256;
exp_data.pinhole = a;

% Feedback status
exp_data.orbit_feedback_status = get_variable('SR01A-CS-FOFB-01:RUN');
exp_data.tune_feedback_status = get_variable('SR-CS-TFB-01:STATUS');

% Emittance
exp_data.emittance_h = get_variable('SR-DI-EMIT-01:HEMIT_MEAN');
exp_data.emittance_v = get_variable('SR-DI-EMIT-01:VEMIT_MEAN');
exp_data.coupling = get_variable('SR-DI-EMIT-01:COUPLING_MEAN');
exp_data.espread = get_variable('SR-DI-EMIT-01:ESPREAD_MEAN');

% Lifetime
exp_data.lifetime = get_variable('SR-DI-DCCT-01:LIFETIME'); % Lifetime on main display chosen for lowest error.
exp_data.life.dcct.life30sec = get_variable('SR-DI-DCCT-01:LIFE30');
exp_data.life.dcct.lifeerr30sec = get_variable('SR-DI-DCCT-01:ERROR30');
exp_data.life.dcct.cond30sec = get_variable('SR-DI-DCCT-01:COND30');
exp_data.life.dcct.life2min = get_variable('SR-DI-DCCT-01:LIFE120');
exp_data.life.dcct.lifeerr2min = get_variable('SR-DI-DCCT-01:ERROR120');
exp_data.life.dcct.cond2min = get_variable('SR-DI-DCCT-01:COND120');
exp_data.life.dcct.life5min = get_variable('SR-DI-DCCT-01:LIFE300');
exp_data.life.dcct.lifeerr5min = get_variable('SR-DI-DCCT-01:ERROR300');
exp_data.life.dcct.cond5min = get_variable('SR-DI-DCCT-01:COND300');
exp_data.life.dcct.life20min = get_variable('SR-DI-DCCT-01:LIFE1200');
exp_data.life.dcct.lifeerr20min = get_variable('SR-DI-DCCT-01:ERROR1200');
exp_data.life.dcct.cond20min = get_variable('SR-DI-DCCT-01:COND1200');

exp_data.life.bpm.life300sec = get_variable('SR-DI-EBPM-01:LIFE300');
exp_data.life.bpm.life300err = get_variable('SR-DI-EBPM-01:ERROR300');
exp_data.life.bpm.cond300sec = get_variable('SR-DI-EBPM-01:COND300');
exp_data.life.bpm.life120sec = get_variable('SR-DI-EBPM-01:LIFE120');
exp_data.life.bpm.life120err = get_variable('SR-DI-EBPM-01:ERROR120');
exp_data.life.bpm.cond120sec = get_variable('SR-DI-EBPM-01:COND120');
exp_data.life.bpm.life30sec = get_variable('SR-DI-EBPM-01:LIFE30');
exp_data.life.bpm.life30err = get_variable('SR-DI-EBPM-01:ERROR30');
exp_data.life.bpm.cond30sec = get_variable('SR-DI-EBPM-01:COND30');
exp_data.life.bpm.life10sec = get_variable('SR-DI-EBPM-01:LIFE10');
exp_data.life.bpm.life10err = get_variable('SR-DI-EBPM-01:ERROR10');
exp_data.life.bpm.cond10sec = get_variable('SR-DI-EBPM-01:COND10');

% Injection
exp_data.injection.btssr2s = get_variable('CS-DI-XFER-01:BS-SR2');
exp_data.injection.btssr10s = get_variable('CS-DI-XFER-01:BS-SR10');
exp_data.injection.boostsr2s = get_variable('CS-DI-XFER-01:BR-SR2');
exp_data.injection.boostsr10s = get_variable('CS-DI-XFER-01:BR-SR10');

% IDs
exp_data.id.gap02 = get_variable('SR02I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap02j = get_variable('SR02J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap03 = get_variable('SR03I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap04 = get_variable('SR04I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap05 = get_variable('SR05I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase05(1) = get_variable('SR05I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase05(2) = get_variable('SR05I-MO-SERVO-07:MOT.RBV');
exp_data.id.gap06a = get_variable('SR06I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase06a(1) = get_variable('SR06I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase06a(2) = get_variable('SR06I-MO-SERVO-06:MOT.RBV');
exp_data.id.gap06b = get_variable('SR06I-MO-SERVC-21:CURRGAPD');
exp_data.id.phase06b(1) = get_variable('SR06I-MO-SERVO-25:MOT.RBV');
exp_data.id.phase06b(2) = get_variable('SR06I-MO-SERVO-26:MOT.RBV');
exp_data.id.gap07 = get_variable('SR04I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap08 = get_variable('SR08I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase08(1) = get_variable('SR08I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase08(2) = get_variable('SR08I-MO-SERVO-07:MOT.RBV');
exp_data.id.gap09i = get_variable('SR09I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap09j = get_variable('SR09J-MO-SERVC-01:CURRGAPD');
exp_data.id.phase09j(1) = get_variable('SR09J-MO-SERVO-05:MOT.RBV');
exp_data.id.phase09j(2) = get_variable('SR09J-MO-SERVO-06:MOT.RBV');
exp_data.id.phase09j(3) = get_variable('SR09J-MO-SERVO-07:MOT.RBV');
exp_data.id.phase09j(4) = get_variable('SR09J-MO-SERVO-08:MOT.RBV');
exp_data.id.gap10a = get_variable('SR10I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase10a(1) = get_variable('SR10I-MO-SERVO-03:MOT.RBV');
exp_data.id.phase10a(2) = get_variable('SR10I-MO-SERVO-04:MOT.RBV');
exp_data.id.phase10a(3) = get_variable('SR10I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase10a(4) = get_variable('SR10I-MO-SERVO-06:MOT.RBV');
exp_data.id.gap10b = get_variable('SR10I-MO-SERVC-21:CURRGAPD');
exp_data.id.phase10b(1) = get_variable('SR10I-MO-SERVO-23:MOT.RBV');
exp_data.id.phase10b(2) = get_variable('SR10I-MO-SERVO-24:MOT.RBV');
exp_data.id.phase10b(3) = get_variable('SR10I-MO-SERVO-25:MOT.RBV');
exp_data.id.phase10b(4) = get_variable('SR10I-MO-SERVO-26:MOT.RBV');
exp_data.id.gap11 = get_variable('SR11I-MO-SERVC-01:CURRGAPD');
exp_data.id.i12field = get_variable('SR12I-CS-SCMPW-01:B');
exp_data.id.gap13i = get_variable('SR13I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap13j = get_variable('SR13J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap14 = get_variable('SR14I-MO-SERVC-01:CURRGAPD');
exp_data.id.i15field = get_variable('SR15I-ID-SCMPW-01:B_REAL');
exp_data.id.gap16 = get_variable('SR16I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap18 = get_variable('SR18I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap19 = get_variable('SR19I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap20i = get_variable('SR20I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap20j = get_variable('SR20J-MO-SERVC-01:CURRGAPD');
exp_data.id.gap21 = get_variable('SR21I-MO-SERVC-01:CURRGAPD');
exp_data.id.phase21(1) = get_variable('SR21I-MO-SERVO-05:MOT.RBV');
exp_data.id.phase21(2) = get_variable('SR21I-MO-SERVO-06:MOT.RBV');
exp_data.id.phase21(3) = get_variable('SR21I-MO-SERVO-07:MOT.RBV');
exp_data.id.phase21(4) = get_variable('SR21I-MO-SERVO-08:MOT.RBV');
exp_data.id.gap22 = get_variable('SR22I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap23 = get_variable('SR23I-MO-SERVC-01:CURRGAPD');
exp_data.id.gap24 = get_variable('SR24I-MO-SERVC-01:CURRGAPD');

exp_data.orbit_x = get_variable('SR-DI-EBPM-01:SA:X');
exp_data.orbit_y = get_variable('SR-DI-EBPM-01:SA:Y');

mbf_systems = {'SR23C-DI-TMBF-01:X', 'SR23C-DI-TMBF-01:Y','SR23C-DI-LMBF-01:IQ'};
mbf_axes = {'x', 'y', 's'};
for sjkh = 1:length(mbf_systems)
exp_data.mbf.(mbf_axes{sjkh}).fll.target_bunches = get_variable([mbf_systems{sjkh}, ':PLL:DET:BUNCHES_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.nco.gain = get_variable([mbf_systems{sjkh}, ':PLL:NCO:GAIN_DB_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.nco.freq = get_variable([mbf_systems{sjkh}, ':PLL:NCO:FREQ_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.nco.enable = get_variable([mbf_systems{sjkh}, ':PLL:NCO:ENABLE_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.integral = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:KI_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.proportional = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:KP_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.maglim = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:MIN_MAG_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.offsetlim = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:MAX_OFFSET_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.target_phase = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:TARGET_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.detector.source = get_variable([mbf_systems{sjkh}, ':PLL:DET:SELECT_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.detector.gain = get_variable([mbf_systems{sjkh}, ':PLL:DET:SCALING_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.detector.dwell = get_variable([mbf_systems{sjkh}, ':PLL:DET:DWELL_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.detector.blanking = get_variable([mbf_systems{sjkh}, ':PLL:DET:BLANKING_S']);
exp_data.mbf.(mbf_axes{sjkh}).fll.status.state = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:STATUS']);
exp_data.mbf.(mbf_axes{sjkh}).fll.status.stopped_by_user = get_variable([mbf_systems{sjkh}, ':PLL:CTRL:STOP:STOP']);
exp_data.mbf.(mbf_axes{sjkh}).fll.status.detector_overflow = get_variable([mbf_systems{sjkh}, ':PLL:STA:DET_OVF']);
exp_data.mbf.(mbf_axes{sjkh}).fll.status.magnitude_error = get_variable([mbf_systems{sjkh}, ':PLL:STA:MAG_ERROR']);
exp_data.mbf.(mbf_axes{sjkh}).fll.status.offset_overflow = get_variable([mbf_systems{sjkh}, ':PLL:STA:OFFSET_OVF']);
exp_data.mbf.(mbf_axes{sjkh}).fll.readbacks.magnitude = get_variable([mbf_systems{sjkh}, ':PLL:FILT:MAG']);
exp_data.mbf.(mbf_axes{sjkh}).fll.readbacks.magnitudedb = get_variable([mbf_systems{sjkh}, ':PLL:FILT:MAG_DB']);
exp_data.mbf.(mbf_axes{sjkh}).fll.readbacks.phase = get_variable([mbf_systems{sjkh}, ':PLL:FILT:PHASE']);
end %for
lcaSetSeverityWarnLevel(3)