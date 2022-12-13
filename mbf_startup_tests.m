function mbf_startup_tests
% Runs all the regular MBF tests
%
% Inject 30mA 900 bunches into the machine before running the tests.
try
    modscan_all('x', 'plotting', 'no')
catch
    disp('Problem with Modescan in X axis')
end %try
try
    modscan_all('y', 'plotting', 'no')
catch
    disp('Problem with Modescan in Y axis')
end %try
try
    modscan_all('s', 'plotting', 'no')
catch
    disp('Problem with Modescan in S axis')
end %try

try
    growdamp_all('x',  'plotting', 'no')
catch
    disp('Problem with Growdamp in X axis')
end %try
try
    growdamp_all('y',  'plotting', 'no')
catch
    disp('Problem with Growdamp in Y axis')
end %try
try
    growdamp_all('s',  'plotting', 'no')
catch
    disp('Problem with Growdamp in S axis')
end %try

try
    mbf_spectrum_all('x',  'plotting', 'no')
catch
    disp('Problem with Spectrum in X axis')
end %try
try
    mbf_spectrum_all('y',  'plotting', 'no')
catch
    disp('Problem with Spectrum in Y axis')
end %try
try
    mbf_spectrum_all('s',  'plotting', 'no')
catch
    disp('Problem with Spectrum in S axis')
end %try

% Leaving the system in a known state
setup_operational_mode('x', "TuneOnly")
setup_operational_mode('y', "TuneOnly")
setup_operational_mode('s', "TuneOnly")