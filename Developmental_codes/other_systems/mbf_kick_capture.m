 [bpm_names, ~,~]=fa_id2name(1:172);
 n_turns = 1000;
 data.BPM_data = BPM_TbT_capture(bpm_names, n_turns);
 data.fill_pattern = lcaGet('SR-DI-PICO-02:BUCKETS_180');
 save('/home/afdm76/mbf_kick_y_nco_m30db.mat', 'data', '-v7.3')

% data.BPM_data = BPM_TbT_get_data(bpm_names, n_turns,...
%     'capture_stats', 'yes', 'all_waveforms', 'yes');
% data.emittance = emittance_get_data;
% save("test_BPM_capture","emittance","BPM_data")
