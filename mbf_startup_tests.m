function mbf_startup_tests

modscan_all('x', 'plotting', 'no')
modscan_all('y', 'plotting', 'no')
modscan_all('s', 'plotting', 'no')

growdamp_all('x',  'plotting', 'no')
growdamp_all('y',  'plotting', 'no')
growdamp_all('s',  'plotting', 'no')

mbf_spectrum_all('x',  'plotting', 'no')
mbf_spectrum_all('y',  'plotting', 'no')
mbf_spectrum_all('s',  'plotting', 'no')