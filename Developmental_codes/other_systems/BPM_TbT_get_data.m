function output = get_BPM_TbT_data(bpm_list, capture_length, varargin)
% Defaults to X and Y waveforms, ABCD and procomputed statistics can be added
% with the flags 'all_waveforms' and 'capture_stats'

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'bpm_list');
addRequired(p, 'capture_length');
addParameter(p, 'all_waveforms', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'capture_stats', 'no', @(x) any(validatestring(x, boolean_string)));

% parse(p, mbf_axis);
parse(p, nbpms, capture_length,  varargin{:});

for n = 1:length(bpm_list)
    bpm_name = bpm_list{n};
    bpm_label = regexprep(bpm_name, '-', '_');
    for tk = 1:10
        try
            BPM_data_temp = get_variable({[bpm_name, ':TT:WFX'];[bpm_name, ':TT:WFY'];});
            output.(bpm_label).X = BPM_data_temp(1, 1:capture_length);
            output.(bpm_label).Y = BPM_data_temp(2, 1:capture_length);
            BPM_data_temp2 = get_variable({[BPM_name, ':TT:WFS'];...
                [BPM_name, ':TT:WFA'];...
                [BPM_name, ':TT:WFB'];...
                [BPM_name, ':TT:WFC'];...
                [BPM_name, ':TT:WFD']});
            output.(bpm_label).intensity = BPM_data_temp2(1, 1:capture_length);
            output.(bpm_label).A = BPM_data_temp2(2, 1:capture_length);
            output.(bpm_label).B = BPM_data_temp2(3, 1:capture_length);
            output.(bpm_label).C = BPM_data_temp2(4, 1:capture_length);
            output.(bpm_label).D = BPM_data_temp2(5, 1:capture_length);
            % Statistics of waveforms
            output.(bpm_label).meanx = lcaGet([bpm, ':TT:MEANX']);
            output.(bpm_label).meany = lcaGet([bpm, ':TT:MEANY']);
            output.(bpm_label).stdx = lcaGet([bpm, ':TT:STDX']);
            output.(bpm_label).stdy = lcaGet([bpm, ':TT:STDY']);
            output.(bpm_label).minx = lcaGet([bpm, ':TT:MINX']);
            output.(bpm_label).miny = lcaGet([bpm, ':TT:MINY']);
            output.(bpm_label).maxx = lcaGet([bpm, ':TT:MAXX']);
            output.(bpm_label).maxy = lcaGet([bpm, ':TT:MAXY']);
            break
        catch
            disp(['Failed to get BPM TbT data for ', bpm_name])
        end %try
    end %while
end %for
