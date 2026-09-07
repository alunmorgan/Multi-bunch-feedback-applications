function output = BPM_SA_get_data(bpm_list, varargin)
% Defaults to X and Y waveforms, ABCD, Q and current can be added
% with the flag 'all_channels'

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'bpm_list');
addParameter(p, 'n_samples', 30)
addParameter(p, 'all_channels', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, bpm_list, varargin{:});

n_bpms = length(bpm_list);

for n = n_bpms:-1:1
    for jsp = p.Results.n_samples:-1:1
        bpm_name = bpm_list{n};
        bpm_label = regexprep(bpm_name, '-', '_');
        BPM_data_temp = get_variable({char(strcat(bpm_name, ':SA:X')); ...
            char(strcat(bpm_name, ':SA:Y'))});
        output.(bpm_label).X(jsp) = squeeze(BPM_data_temp(1));
        output.(bpm_label).Y(jsp) = squeeze(BPM_data_temp(2));
        if strcmp(p.Results.all_channels, 'yes')
            BPM_data_temp_add = get_variable({char(strcat(bpm_name, ':SA:Q'));...
                char(strcat(bpm_name, ':SA:CURRENT'));...
                char(strcat(bpm_name, ':SA:A'));...
                char(strcat(bpm_name, ':SA:B'));...
                char(strcat(bpm_name, ':SA:C'));...
                char(strcat(bpm_name, ':SA:D'))});
            output.(bpm_label).Q(jsp) = squeeze(BPM_data_temp_add(1));
            output.(bpm_label).CURRENT(jsp) = squeeze(BPM_data_temp_add(2));
            output.(bpm_label).A(jsp) = squeeze(BPM_data_temp_add(3));
            output.(bpm_label).B(jsp) = squeeze(BPM_data_temp_add(4));
            output.(bpm_label).C(jsp) = squeeze(BPM_data_temp_add(5));
            output.(bpm_label).D(jsp) = squeeze(BPM_data_temp_add(6));
        end %if
    end %for
end %for
