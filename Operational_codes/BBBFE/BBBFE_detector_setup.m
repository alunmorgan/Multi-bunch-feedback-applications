function BBBFE_detector_setup(mbf_ax, single_bunch_location)

% press tune only
setup_operational_mode(mbf_ax, "TuneOnly")
if single_bunch_location == 0
    prior_bunch = 935;
else
    prior_bunch = single_bunch_location -1;
end %if
    
% set up the individual tune detectors to run on 1,2,3
if strcmp(mbf_ax, 'X') || strcmp(mbf_ax, 'Y')
pv_head = ['SR23C-DI-TMBF-01:', mbf_ax, ':'];
elseif strcmp(mbf_ax, 'S')
pv_head = ['SR23C-DI-LMBF-01:', 'IQ', ':'];
end %if

lcaPut([pv_head, 'DET:1:ENABLE_S'], 1)
lcaPut([pv_head, 'DET:1:SCALING_S'], 0)
lcaPut([pv_head, 'DET:1:BUNCH_SELECT_S'] ,'0:935');
lcaPut([pv_head, 'DET:1:RESET_SELECT_S.PROC'] ,1);
lcaPut([pv_head, 'DET:1:BUNCH_SELECT_S'], num2str(prior_bunch));
lcaPut([pv_head, 'DET:1:SET_SELECT_S.PROC'], 1);

lcaPut([pv_head, 'DET:2:ENABLE_S'], 1)
lcaPut([pv_head, 'DET:2:SCALING_S'], 0)
lcaPut([pv_head, 'DET:2:BUNCH_SELECT_S'], '0:935');
lcaPut([pv_head, 'DET:2:RESET_SELECT_S.PROC'], 1);
lcaPut([pv_head, 'DET:2:BUNCH_SELECT_S'], num2str(single_bunch_location));
lcaPut([pv_head, 'DET:2:SET_SELECT_S.PROC'], 1);

lcaPut([pv_head, 'DET:3:ENABLE_S'], 1)
lcaPut([pv_head, 'DET:3:SCALING_S'], 0)
lcaPut([pv_head, 'DET:3:BUNCH_SELECT_S'], '0:935');
lcaPut([pv_head, 'DET:3:RESET_SELECT_S.PROC'], 1);
lcaPut([pv_head, 'DET:3:BUNCH_SELECT_S'], num2str(single_bunch_location +1));
lcaPut([pv_head, 'DET:3:SET_SELECT_S.PROC'], 1);

% set sweep gain to -18
lcaPut([pv_head, 'SEQ:1:GAIN_DB_S'], '-18');
% set detector fixed gain