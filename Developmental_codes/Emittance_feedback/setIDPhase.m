function monitored_data = setIDPhase(ID, Phases_in, monitor_pvs, wait)

if strcmp(ID,'I10')||strcmp(ID,'I06')
    ID = strcat(ID,'A');
end %if

params = ID_parameters;

PV_Lookup = containers.Map(params.IDs,params.phase_sets);
readback_Lookup = containers.Map(params.IDs, params.phase_readbacks);

Set_PV = PV_Lookup(ID);
read_PV = readback_Lookup(ID);

if isempty(Set_PV)
    disp("No phases associated with this ID")
    return
end %if

phase_settings = containers.Map(params.IDs, params.phase_values);
phase_setups = phase_settings(ID);

Modes = {'H','V','L','R'};
phase_setups_Lookup = containers.Map(Modes, phase_setups);

Phase_Puts = [];
for i = 1:length(Phases_in)
    Phase_Puts = [Phase_Puts; phase_setups_Lookup(Phases_in{i})];
end %for

monitored_pvs = cat(1, params.gap_readbacks', params.phase_readbacks', monitor_pvs);
Execute = char(strcat(Set_PV{1}(1:end-2),'.PROC'));

monitored_data = scan_id_setting(Phase_Puts, Execute, Set_PV, read_PV,...
    monitored_pvs, wait);
