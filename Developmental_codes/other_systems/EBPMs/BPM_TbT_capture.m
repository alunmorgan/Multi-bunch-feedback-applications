function output = BPM_TbT_capture(bpm_list, capture_length)
%sets up and arms a turn by turn capture on the requested set of BPMs.
% the BPMs will trigger on the next hardware trigger.
% the output is then captured into a structure.
% use fa_id2name to pregenerate a list of BPM names.
%
% Example: output = BPM_TbT_capture({'SR01C-DI-EBPM-01', 'SR01C-DI-EBPM-02'}, 1000)
BPM_TbT_capture_setup(bpm_list, capture_length)
BPM_TbT_capture_arm(bpm_list)
pause(0.2)
output = BPM_TbT_get_data(bpm_list, capture_length,...
    'capture_stats', 'yes', 'all_waveforms', 'yes');
fprintf('\n')