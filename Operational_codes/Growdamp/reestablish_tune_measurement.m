function reestablish_tune_measurement(mbf_axis)

if strcmpi(mbf_axis,'x')
    sweep_start = 80.139;
sweep_end = 80.239;
tune_gain = -54;
tune_dwell = 100;
elseif strcmpi(mbf_axis, 'y')
sweep_start = 80.227;
sweep_end = 80.327;
tune_gain = -54;
tune_dwell = 100;
end %if
    sweep_start = 80.00320;
sweep_end = 80.00520;
tune_gain = -18;
tune_dwell = 100;

lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:START_FREQ_S',sweep_start);
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:END_FREQ_S',sweep_end);
lcaPut('SR23C-DI-SR23C-DI-TMBF-01:X:SEQ:1:ENABLE_S','On');
lcaPut('TMBF-01:X:SEQ:1:GAIN_DB_S',tune_gain);
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:BANK_S',{'Bank 1'});
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:TUNE_PLL_S',{'Ignore'});
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:COUNT_S',4096);
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:DWELL_S',tune_dwell);

lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:STATE_HOLDOFF_S',0);
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:HOLDOFF_S',0);
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:BLANK_S',{'Blanking'});
lcaPut('SR23C-DI-TMBF-01:X:SEQ:1:ENWIN_S',{'Windowed'});
lcaPut('SR23C-SR23C-DI-TMBF-01:X:SEQ:PC_S',1);
lcaPut('DI-TMBF-01:X:SEQ:1:CAPTURE_S',{'Capture'});
lcaPut('SR23C-DI-TMBF-01:X:SEQ:SUPER:COUNT_S',1);