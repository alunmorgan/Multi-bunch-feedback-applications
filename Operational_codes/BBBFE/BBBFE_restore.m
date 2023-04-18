function BBBFE_restore(mbf_ax)

    
% set up the individual tune detectors to run on 1,2,3
pv_head = ['SR23C-DI-TMBF-01:', mbf_ax, ':'];

lcaPut([pv_head, 'DET:1:ENABLE_S'], 0)
lcaPut([pv_head, 'DET:2:ENABLE_S'], 0)
lcaPut([pv_head, 'DET:3:ENABLE_S'], 0)

% press tune only
setup_operational_mode(mbf_ax, "TuneOnly")