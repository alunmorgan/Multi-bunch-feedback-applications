function monitored_data = setIDGap(ID, Gaps, monitor_pvs, wait)

if strcmp(ID,'I10')||strcmp(ID,'I06')
    ID = strcat(ID,'A');
end %if

params = ID_parameters;

PV_Lookup = containers.Map(params.IDs, params.gap_sets);
readback_Lookup = containers.Map(params.IDs, params.gap_readbacks);

Set_PV = PV_Lookup(ID);
read_PV = readback_Lookup(ID);

monitored_pvs = cat(1, params.gap_readbacks', params.phase_readbacks', monitor_pvs);
Execute = char(strcat(Set_PV(1:end-2),'.PROC'));

monitored_data = scan_id_setting(Gaps, Execute, Set_PV, read_PV,...
    monitored_pvs, wait);
