function mbf_startup_tests
% Runs all the regular MBF tests
%
% Inject 30mA 900 bunches into the machine before running the tests.
beam_current = lcaGet('SR-DI-DCCT-01:SIGNAL');
if beam_current< 10
    disp('Beam current below 10mA... not running tests.')
    return
end %if

fir_gain_x = lcaGet('SR23C-DI-TMBF-01:X:FIR:GAIN_S');
fir_gain_y = lcaGet('SR23C-DI-TMBF-01:Y:FIR:GAIN_S');
fir_gain_s = lcaGet('SR23C-DI-LMBF-01:IQ:FIR:GAIN_S');

% Get the tunes
tunes = get_all_tunes('xys');

try
    setup_operational_mode('x', "Feedback")
    lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', '0dB')
    growdamp_all('x',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Growdamp in X axis')
end %try
try
    setup_operational_mode('y', "Feedback")
    lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', '0dB')
    growdamp_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Growdamp in Y axis')
end %try
try
    setup_operational_mode('s', "Feedback")
    lcaPut('SR23C-DI-LMBF-01:IQ:FIR:GAIN_S', '0dB')
    growdamp_all('s',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Growdamp in S axis')
end %try

try
    setup_operational_mode('x', "TuneOnly")
    modscan_all('x', 'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
catch
    disp('Problem with Modescan in X axis')
end %try
try
    setup_operational_mode('y', "TuneOnly")
    modscan_all('y', 'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
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
catch
    disp('Problem with Spectrum in X axis')
end %try
try
    setup_operational_mode('y', "TuneOnly")
    mbf_spectrum_all('y',  'plotting', 'no', 'auto_setup', 'no', 'tunes', tunes)
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
lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', fir_gain_x );
lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', fir_gain_y);
lcaPut('SR23C-DI-LMBF-01:IQ:FIR:GAIN_S', fir_gain_s);