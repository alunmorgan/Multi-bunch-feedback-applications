function [root_path, harmonic_number, pv_names] = mbf_system_config

%       harmonic_number (int): Harmonic number of the machine.

root_path = '/dls/ops-data/Diagnostics/MBF/';
harmonic_number = 936;

pv_names.Hardware_trigger = 'LI-TI-MTGEN-01:BS-DI-MODE';
pv_names.tails.DDR_arm = ':TRG:DDR:ARM_S.PROC';
pv_names.tails.DDR_status = ':DDR:STATUS';
pv_names.tails.DDR_buffer = ':DDR:LONGWF';

pv_names.tails.DDR_trigger_select = ':TRG:DDR:SEL_S';
pv_names.tails.DDR_trigger_mode = ':TRG:DDR:MODE_S';
pv_names.tails.Sequencer_trigger_select = ':TRG:SEQ:SEL_S';
pv_names.tails.DDR_external_trigger_enable_status = ':TRG:DDR:EXT:EN_S';
pv_names.tails.DDR_post_mortem_trigger_enable_status = ':TRG:DDR:PM:EN_S';
pv_names.tails.DDR_ADC_trigger_enable_status = ':TRG:DDR:ADC:EN_S';
pv_names.tails.DDR_sequencer_trigger_enable_status = ':TRG:DDR:SEQ:EN_S';
pv_names.tails.DDR_system_clock_trigger_enable_status = ':TRG:DDR:SCLK:EN_S';
pv_names.tails.DDR_external_trigger_blanking_status = ':TRG:DDR:EXT:BL_S';
pv_names.tails.DDR_post_mortem_trigger_blanking_status   = ':TRG:DDR:PM:BL_S';
pv_names.tails.DDR_ADC_trigger_blanking_status = ':TRG:DDR:ADC:BL_S';
pv_names.tails.DDR_sequencer_trigger_blanking_status = ':TRG:DDR:SEQ:BL_S';
pv_names.tails.DDR_system_clock_trigger_blanking_status = ':TRG:DDR:SCLK:BL_S';
pv_names.tails.DDR_input = ':DDR:INPUT_S';

pv_names.tails.Sequencer_trigger_state = ':SEQ:TRIGGER_S';
pv_names.tails.Sequencer.Base = ':SEQ:';
pv_names.tails.Sequencer.start_frequency = ':START_FREQ_S';
pv_names.tails.Sequencer.count = ':COUNT_S';
pv_names.tails.Sequencer.dwell = ':DWELL_S';
pv_names.tails.Sequencer.gain = ':GAIN_S';

pv_names.tails.Detector_gain = ':DET:GAIN_S';
pv_names.tails.Detector_mode = ':DET:MODE_S';
pv_names.tails.Detector_autogain_state = ':DET:AUTOGAIN_S';
pv_names.tails.Detector_input = ':DET:INPUT_S';

pv_names.tails.DDR_IQ_overflow = ':DDR:OVF:IQ';
pv_names.tails.DDR_IQ_mode = ':DDR:IQMODE_S';
pv_names.tails.DDR_autostop_setting = ':DDR:AUTOSTOP_S';

pv_names.tails.Super_sequencer_count = ':SEQ:SUPER:COUNT_S';

pv_names.tails.Buffer_trigger_mode = ':TRG:BUF:MODE_S';
pv_names.tails.Buffer_trigger_stop = ':TRG:BUF:RESET_S.PROC';

