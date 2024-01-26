function BBBFE_detector_restore(mbf_ax)

    
% set up the individual tune detectors to run on 1,2,3
if strcmp(mbf_ax, 'X') || strcmp(mbf_ax, 'Y')
pv_head = ['SR23C-DI-TMBF-01:', mbf_ax, ':'];
elseif strcmp(mbf_ax, 'S')
pv_head = ['SR23C-DI-LMBF-01:', 'IQ', ':'];
end %if

set_variable([pv_head, 'DET:1:ENABLE_S'], 0)
set_variable([pv_head, 'DET:2:ENABLE_S'], 0)
set_variable([pv_head, 'DET:3:ENABLE_S'], 0)

% press tune only
setup_operational_mode(mbf_ax, "TuneOnly")