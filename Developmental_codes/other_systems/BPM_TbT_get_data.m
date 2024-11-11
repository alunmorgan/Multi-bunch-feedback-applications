function output = BPM_TbT_get_data(bpm_list, capture_length, varargin)
% Defaults to X and Y waveforms, ABCD and procomputed statistics can be added
% with the flags 'all_waveforms' and 'capture_stats'

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'bpm_list');
addRequired(p, 'capture_length');
addParameter(p, 'xy_waveforms', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'all_waveforms', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'capture_stats', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'n_trys', 5)

parse(p, bpm_list, capture_length,  varargin{:});

update_tick = 1;
n_trys = p.Results.n_trys;
for n = 1:length(bpm_list)
    bpm_name = bpm_list{n};
    bpm_label = regexprep(bpm_name, '-', '_');
    fail_tick = 0;
    for tk = 1:n_trys
        try
            if strcmp(p.Results.xy_waveforms, 'yes')
                BPM_data_tempx = get_variable([bpm_name, ':TT:WFX']);
                BPM_data_tempy = get_variable([bpm_name, ':TT:WFY']);
                output.(bpm_label).X = BPM_data_tempx(1:capture_length);
                output.(bpm_label).Y = BPM_data_tempy(1:capture_length);
            end %if
            if strcmp(p.Results.all_waveforms, 'yes')
                bpm_data_temps = get_variable([bpm_name, ':TT:WFS']);...
                    bpm_data_tempa = get_variable([bpm_name, ':TT:WFA']);
                bpm_data_tempb = get_variable([bpm_name, ':TT:WFB']);
                bpm_data_tempc = get_variable([bpm_name, ':TT:WFC']);
                bpm_data_tempd = get_variable([bpm_name, ':TT:WFD']);
                output.(bpm_label).intensity = bpm_data_temps(1:capture_length);
                output.(bpm_label).A = bpm_data_tempa(1:capture_length);
                output.(bpm_label).B = bpm_data_tempb(1:capture_length);
                output.(bpm_label).C = bpm_data_tempc(1:capture_length);
                output.(bpm_label).D = bpm_data_tempd(1:capture_length);
            end %if
            % Statistics of waveforms
            if strcmp(p.Results.capture_stats, 'yes')
                output.(bpm_label).meanx = get_variable([bpm_name, ':TT:MEANX']);
                output.(bpm_label).meany = get_variable([bpm_name, ':TT:MEANY']);
                output.(bpm_label).stdx = get_variable([bpm_name, ':TT:STDX']);
                output.(bpm_label).stdy = get_variable([bpm_name, ':TT:STDY']);
                output.(bpm_label).minx = get_variable([bpm_name, ':TT:MINX']);
                output.(bpm_label).miny = get_variable([bpm_name, ':TT:MINY']);
                output.(bpm_label).maxx = get_variable([bpm_name, ':TT:MAXX']);
                output.(bpm_label).maxy = get_variable([bpm_name, ':TT:MAXY']);
            end %if
            fprintf('.')
            update_tick = update_tick + 1;
            if rem(update_tick, 50) == 0
                fprintf('\n')
            end %if
            break
        catch ME
            fprintf(['\nRetrying to get BPM TbT data for ', bpm_name, '(', ME.identifier, ')'])
            fail_tick = fail_tick + 1;
        end %try
    end %for
    if fail_tick == n_trys
        fprintf(['\nFailed to get BPM TbT data for ', bpm_name, '\n'])
    end %if
end %for
