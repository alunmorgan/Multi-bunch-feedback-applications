function monitored_data = setIDGap(ID, Gaps, monitor_pvs, wait)

if strcmp(ID,'I10')||strcmp(ID,'I06')
    ID = strcat(ID,'A');
end %if

[params, lookups] = ID_parameters;

Set_PV = lookups.gaps_set(ID);
read_PV = lookups.gaps_readback(ID);
Execute_PV = lookups.gaps_execute(ID);
monitored_pvs = cat(1, params.gap_readbacks', params.phase_readbacks', monitor_pvs);

monitored_data = scan_id_setting(Gaps, Execute_PV, Set_PV, read_PV,...
    monitored_pvs, wait);
