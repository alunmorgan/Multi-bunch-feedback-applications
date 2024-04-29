function output = BPM_SA_get_data(bpm_list, varargin)
% Defaults to X and Y waveforms, ABCD, Q and current can be added
% with the flag 'all_channels'

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'bpm_list');
addRequired(p, 'capture_length');
addParameter(p, 'n_samples', 30)
addParameter(p, 'all_channels', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, nbpms, varargin{:});

n_bpms = length(bpm_list);

for n = n_bpms:-1:1
    for jsp = n_samples:-1:1
        bpm_name = bpm_list{n};
        bpm_label = regexprep(bpm_name, '-', '_');
        BPM_data_temp = get_variable({[bpm_name, ':SA:X']; ...
            [bpm_name, ':SA:Y'];});
        output.(bpm_label).X = squeeze(BPM_data_temp(1, jsp));
        output.(bpm_label).Y = squeeze(BPM_data_temp(2, jsp));
        if strcmp(p.Results.all_channels, 'yes')
            BPM_data_temp_add = get_variable({[bpm_name, ':SA:Q'];...
                [bpm_name, ':SA:CURRENT'];...
                [bpm_name, ':SA:A'];...
                [bpm_name, ':SA:B'];...
                [bpm_name, ':SA:C'];...
                [bpm_name, ':SA:D']});
            output.(bpm_label).Q = squeeze(BPM_data_temp_add(1, jsp));
            output.(bpm_label).CURRENT = squeeze(BPM_data_temp_add(2, jsp));
            output.(bpm_label).A = squeeze(BPM_data_temp_add(3, jsp));
            output.(bpm_label).B = squeeze(BPM_data_temp_add(4, jsp));
            output.(bpm_label).C = squeeze(BPM_data_temp_add(5, jsp));
            output.(bpm_label).D = squeeze(BPM_data_temp_add(6, jsp));
        end %if
    end %for
end %for
