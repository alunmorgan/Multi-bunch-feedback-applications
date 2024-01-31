function mbf_startup_tests
% Runs all the regular MBF tests
%
% Inject 30mA 900 bunches into the machine before running the tests.

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

beam_current = get_variable(pv_names.current);
if beam_current< 10
    disp('Beam current below 10mA... not running tests.')
    return
end %if

fir_name_x = [mbf_names.x, mbf_vars.Bunch_bank.FIR_gains];
fir_name_y = [mbf_names.y, mbf_vars.Bunch_bank.FIR_gains];
fir_name_s = [mbf_names.s, mbf_vars.Bunch_bank.FIR_gains];

fir_gain_x = get_variable(fir_name_x);
fir_gain_y = get_variable(fir_name_y);
fir_gain_s = get_variable(fir_name_s);

% Get the tunes
tunes = get_all_tunes;

try
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, '0dB')
    [~] = growdamp_all('x',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch
    disp('Problem with Growdamp in X axis')
end %try
try
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, '0dB')
    [~] = growdamp_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch
    disp('Problem with Growdamp in Y axis')
end %try
try
    setup_operational_mode('s', "Feedback")
    set_variable(fir_name_s, '0dB')
    [~] = growdamp_all('s',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes);
    setup_operational_mode('s', "TuneOnly")
catch
    disp('Problem with Growdamp in S axis')
end %try

try
    setup_operational_mode('x', "TuneOnly")
    modscan_all('x', 'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
        setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch
    disp('Problem with Modescan in X axis')
end %try
try
    setup_operational_mode('y', "TuneOnly")
    modscan_all('y', 'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
        setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch
    disp('Problem with Modescan in Y axis')
end %try
try
    setup_operational_mode('s', "TuneOnly")
    modscan_all('s', 'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Modescan in S axis')
end %try

try
    setup_operational_mode('x', "TuneOnly")
    mbf_spectrum_all('x',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
     setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch
    disp('Problem with Spectrum in X axis')
end %try
try
    setup_operational_mode('y', "TuneOnly")
    mbf_spectrum_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
        setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch
    disp('Problem with Spectrum in Y axis')
end %try
try
    setup_operational_mode('s', "TuneOnly")
    mbf_spectrum_all('s',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Spectrum in S axis')
end %try

% Leaving the system in a known state
setup_operational_mode('x', "Feedback")
setup_operational_mode('y', "Feedback")
setup_operational_mode('s', "TuneOnly")
set_variable(fir_name_x, fir_gain_x );
set_variable(fir_name_y, fir_gain_y);
set_variable(fir_name_s, fir_gain_s);