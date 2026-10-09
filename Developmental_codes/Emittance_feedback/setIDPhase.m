function monitored_data = setIDPhase(ID, Phases_in, monitor_pvs, wait)

if strcmp(ID,'I10')||strcmp(ID,'I06')
    ID = strcat(ID,'A');
end %if

[params, lookups] = ID_parameters;

Set_PV = lookups.phases_set(ID);

if isempty(Set_PV)
    disp("No phases associated with this ID")
    return
end %if

read_PV = lookups.phases_readback(ID);
phase_setups = lookups.phases_settings(ID);
Execute_PV = lookups.phases_execute(ID);

Modes = {'H','V','L','R'};
phase_setups_Lookup = containers.Map(Modes, phase_setups);

Phase_Puts = [];
for i = 1:length(Phases_in)
    Phase_Puts = [Phase_Puts; phase_setups_Lookup(Phases_in{i})];
end %for

monitored_pvs = cat(1, params.gap_readbacks', params.phase_readbacks', monitor_pvs);

monitored_data = scan_id_setting(Phase_Puts, Execute_PV, Set_PV, read_PV,...
    monitored_pvs, wait);
