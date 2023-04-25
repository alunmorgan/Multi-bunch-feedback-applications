function update_all_indexes
% updates all indexes in the data archive
% useful if something is corrupted.

mbf_make_index('LO_scan')
mbf_make_index('clock_phase_scan')
mbf_make_index('system_phase_scan')
mbf_make_index('Bunch_motion')
mbf_make_index('Spectrum', 'x')
mbf_make_index('Spectrum', 'y')
mbf_make_index('Spectrum', 's')
mbf_make_index('Growdamp', 'x')
mbf_make_index('Growdamp', 'y')
mbf_make_index('Growdamp', 's')


