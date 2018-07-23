function mbf_bunch_motion_setup
% Sets up all three axis so that they will take a single set of data each 
% when armed and triggered 
%
% Example: mbf_bunch_motion_setup

[~, ~, pv_names] = mbf_system_config;
PVt = pv_names.tails;
for hse = 1:3
    mbf_get_then_put([ax2dev(hse) PVt.MEM_trigger_select], 'Hardware')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_trigger_mode], 'One Shot')
    mbf_get_then_put([ax2dev(hse) PVt.Sequencer_trigger_select], 'BUF trigger')
    %     Setting hardware triggers
    mbf_get_then_put([ax2dev(hse) PVt.MEM_external_trigger_enable_status], 'Enable')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_post_mortem_trigger_enable_status], 'Ignore')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_ADC_trigger_enable_status], 'Ignore')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_sequencer_trigger_enable_status], 'Ignore')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_system_clock_trigger_enable_status], 'Ignore')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_external_trigger_blanking_status], 'All')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_post_mortem_trigger_blanking_status], 'All')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_ADC_trigger_blanking_status], 'Blanking')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_sequencer_trigger_blanking_status], 'All')
    mbf_get_then_put([ax2dev(hse) PVt.MEM_system_clock_trigger_blanking_status], 'All')
    %  set up the memory buffer to capture ADC data.
    mbf_get_then_put([ax2dev(hse) PVt.MEM_input], 'ADC')
end %for