function mbf_startup_tests
% Runs all the regular MBF tests
%
% Inject 30mA 900 bunches into the machine before running the tests.

[~, ~, pv_names] = mbf_system_config;

beam_current = get_variable(pv_names.current);
if beam_current< 10
    disp('Beam current below 10mA... not running tests.')
    return
end %if

fir_name_x = [pv_names.hardware_names.x, ':FIR:GAIN_S'];
fir_name_y = [pv_names.hardware_names.y, ':FIR:GAIN_S'];
fir_name_s = [pv_names.hardware_names.s, ':FIR:GAIN_S'];

fir_gain_x = get_variable(fir_name_x);
fir_gain_y = get_variable(fir_name_y);
fir_gain_s = get_variable(fir_name_s);

try
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, '0dB')
    growdamp_all('x',  'plotting', 'no', 'auto_setup', 'no');
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch me 
    disp('Problem with Growdamp in X axis')
    disp(me.message)
end %try
try
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, '0dB')
    growdamp_all('y',  'plotting', 'no', 'auto_setup', 'no');
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch me
    disp('Problem with Growdamp in Y axis')
        disp(me.message)
end %try
try
    setup_operational_mode('s', "Feedback")
    set_variable(fir_name_s, '0dB')
    growdamp_all('s',  'plotting', 'no', 'auto_setup', 'no');
    setup_operational_mode('s', "TuneOnly")
catch me
    disp('Problem with Growdamp in S axis')
        disp(me.message)
end %try

try
    setup_operational_mode('x', "TuneOnly")
    modescan_all('x', 'plotting', 'no', 'auto_setup', 'no')
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch me
    disp('Problem with Modescan in X axis')
        disp(me.message)
end %try
try
    setup_operational_mode('y', "TuneOnly")
    modescan_all('y', 'plotting', 'no', 'auto_setup', 'no')
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch me 
    disp('Problem with Modescan in Y axis')
        disp(me.message)
end %try
try
    setup_operational_mode('s', "TuneOnly")
    modescan_all('s', 'plotting', 'no', 'auto_setup', 'no')
catch me
    disp('Problem with Modescan in S axis')
        disp(me.message)
end %try

try
    setup_operational_mode('x', "TuneOnly")
    mbf_spectrum_all('x',  'plotting', 'no', 'auto_setup', 'no')
    setup_operational_mode('x', "Feedback")
    set_variable(fir_name_x, fir_gain_x)
catch me
    disp('Problem with Spectrum in X axis')
        disp(me.message)
end %try
try
    setup_operational_mode('y', "TuneOnly")
    mbf_spectrum_all('y',  'plotting', 'no', 'auto_setup', 'no')
    setup_operational_mode('y', "Feedback")
    set_variable(fir_name_y, fir_gain_y)
catch me
    disp('Problem with Spectrum in Y axis')
        disp(me.message)
end %try
try
    setup_operational_mode('s', "TuneOnly")
    mbf_spectrum_all('s',  'plotting', 'no', 'auto_setup', 'no')
catch me
    disp('Problem with Spectrum in S axis')
        disp(me.message)
end %try

% Leaving the system in a known state
setup_operational_mode('x', "Feedback")
setup_operational_mode('y', "Feedback")
setup_operational_mode('s', "TuneOnly")
set_variable(fir_name_x, fir_gain_x );
set_variable(fir_name_y, fir_gain_y);
set_variable(fir_name_s, fir_gain_s);