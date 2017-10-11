function mbf_bunch_motion_setup
% Sets up all three axis so that they will take a single set of data each 
% when armed and triggered 
%
% Example: mbf_bunch_motion_setup

for hse = 1:3
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:SEL_S'], 'Hardware')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:MODE_S'], 'One Shot')
    mbf_get_then_put([ax2dev(hse) ':TRG:SEQ:SEL_S'], 'BUF trigger')
    %     Setting hardware triggers
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:EXT:EN_S'], 'Enable')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:PM:EN_S'], 'Ignore')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:ADC:EN_S'], 'Ignore')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:SEQ:EN_S'], 'Ignore')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:SCLK:EN_S'], 'Ignore')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:EXT:BL_S'], 'All')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:PM:BL_S'], 'All')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:ADC:BL_S'], 'Blanking')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:SEQ:BL_S'], 'All')
    mbf_get_then_put([ax2dev(hse) ':TRG:DDR:SCLK:BL_S'], 'All')
    %  set up the DDR buffer to capture ADC data.
    mbf_get_then_put([ax2dev(hse) ':DDR:INPUT_S'], 'ADC')
end %for