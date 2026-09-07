function results = setIDPhase(ID,Phases_in,Monitor,Wait)

results = [];

if strcmp(ID,'I10')|strcmp(ID,'I06')
    ID = strcat(ID,'A');
end

IDs = {'I02','I03','I04','J04','I05','I06A','I06B','I07','I08','I09','J09','I10A','I10B','I11','I13','J13','I14','I16','I18','I19','I20','I21','I22','I23','I24'};
PVs = {{},{},{},{},{},{'SR06I-MO-SERVC-01:PHASESET.B';'SR06I-MO-SERVC-01:PHASESET.C'},...
    {'SR06I-MO-SERVC-21:PHASESET.B';'SR06I-MO-SERVC-21:PHASESET.C'},...
    {},{'SR08I-MO-SERVC-01:PHASESET.B';'SR08I-MO-SERVC-01:PHASESET.C'},...
    {},{'SR09J-MO-SERVC-01:PHASESET.B';'SR09J-MO-SERVC-01:PHASESET.C';...
    'SR09J-MO-SERVC-01:PHASESET.D';'SR09J-MO-SERVC-01:PHASESET.E'},...
    {'SR10I-MO-SERVC-01:PHASESET.B';'SR10I-MO-SERVC-01:PHASESET.C'},...
    {'SR10I-MO-SERVC-21:PHASESET.B';'SR10I-MO-SERVC-21:PHASESET.C'},...
    {},{},{},{},{},{},{},{},...
    {'SR21I-MO-SERVC-01:PHASESET.B';'SR21I-MO-SERVC-01:PHASESET.C';...
    'SR21I-MO-SERVC-01:PHASESET.D';'SR21I-MO-SERVC-01:PHASESET.E'},...
    {},{},{}};
PV_Lookup = containers.Map(IDs,PVs);
Set_PV = PV_Lookup(ID);

Phase_IDs = {'I06A','I06B','I08','J09','I10A','I10B','I21'};
Phase_Values = {{[0,0],[32,32],[22,22],[-22,-22]},{[0,0],[32,32],...
    [22,22],[-22,-22]},{[0,0],[26.5,26.5],[17,17],[-17,-17]},...
    {[0,0,0,0],[30,0,30,0],[17,0,17,0],[-17,0,-17,0]},...
    {[0,0],[24,24],[-15.1724,-15.1724],[15.1724,15.1724]},...
    {[0,0],[24,24],[-15.1724,-15.1724],[15.1724,15.1724]},...
    {[0,0,0,0],[28,0,28,0],[18,0,18,0],[-18,0,-10,0]}};
Settings = containers.Map(Phase_IDs,Phase_Values);
Puts = Settings(ID);

Modes = {'H','V','L','R'};
Put_Lookup = containers.Map(Modes,Puts);


Phase_Puts = [];
for i = 1:length(Phases_in)
    Phase_Puts = [Phase_Puts;Put_Lookup(Phases_in(i))];
end

if isempty(Set_PV)
    display("No phases associated with this ID")
    return
else
    Execute = strcat(Set_PV{1}(1:end-2),'.PROC');

    for i = 1:length(Phases_in)
        lcaPut(Set_PV,Phase_Puts(i,:)')
        lcaPutNoWait(char(Execute),1)
        pause(Wait)
        if ~isempty(Monitor)
            gap_result = lcaGet(Monitor);
            results = [results;gap_result];
        end
    end
end


end