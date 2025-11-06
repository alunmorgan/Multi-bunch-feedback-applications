function mbf_digital_loopback_checkout(mbf_axis)
% This runs a series of tests using various internal signal sources in
% order to validate the expected system performance.
% THIS SHOULD BE RUN WITH NO OTHER SIGNALS (I.E. BEAM)
%
% Example:  mbf_digital_loopback_checkout('x')


[root_string, ~, ~, ~] = mbf_system_config;
base_name = ['DL_checkout_' mbf_axis];
exp_time = datevec(datetime("now"));
%TEMP OVERRIDE
root_string = '/scihome/afdm76/MBF_loopback_test_data/';
% Number of turns to capture.
n_turns = 1000;
%% FIXME HARDCOADED PVS S axis is not fully implemented.
if strcmpi(mbf_axis, 'x')
    lcaPut('SR23C-DI-TMBF-01:MEM:SEL0_S', 'ADC0')
    lcaPut('SR23C-DI-TMBF-01:MEM:SEL1_S', 'DAC0')
elseif strcmpi(mbf_axis, 'y')
    lcaPut('SR23C-DI-TMBF-01:MEM:SEL0_S', 'ADC1')
    lcaPut('SR23C-DI-TMBF-01:MEM:SEL1_S', 'DAC1')
elseif strcmpi(mbf_axis, 's')
    lcaPut('SR23C-DI-LMBF-01:MEM:SEL0_S', 'ADC0')
    lcaPut('SR23C-DI-LMBF-01:MEM:SEL1_S', 'DAC0')
end %if
lcaPut('SR23C-DI-TMBF-01:TRG:MEM:DISARM_S.PROC', 1)

pause(1)
% Default is everything off.
lb_status = {'_no_loopback', '_with_loopback'};
lb_state = {'no', 'yes'};
% Run the measurement set once with no loopback and once with loopback enabled.
for bwe = 1:2
    % All sources off
    mbf_checkout_setup(mbf_axis, 'loopback', lb_state{bwe})
    pause(1)
    lcaPut('SR23C-DI-TMBF-01:MEM:CAPTURE_S.PROC', 1)
    pause(1)
    data_out.time = exp_time;
    data_out.base_name = [base_name '_noise' lb_status{bwe}];
    data_out.tune = 0;
    data_out.nco1 = 0;
    data_out.nco2 = 0;
    data_out.fir = 0;
    data_out.adc = get_data_from_mbf_memory(mbf_axis, 0, n_turns);
    data_out.dac = get_data_from_mbf_memory(mbf_axis, 1, n_turns);

    save_to_archive(root_string, data_out)

    % Tune on
    tune_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'};
    tune_labels = regexprep(tune_gains, '-', 'm');
    for emw = 1:length(tune_gains)
        mbf_checkout_setup(mbf_axis, 'loopback',lb_state{bwe}, 'tune', 'yes',...
            'tune_gain', tune_gains{emw})
        pause(1)
        lcaPut('SR23C-DI-TMBF-01:MEM:CAPTURE_S.PROC', 1)
        pause(1)
        data_out.time = exp_time;
        data_out.base_name = [base_name '_tune_gain_' tune_labels{emw} lb_status{bwe}];
        data_out.tune_gain = tune_gains{emw};
        data_out.loopback = lb_status{bwe};
        data_out.tune = 1;
        data_out.nco1 = 0;
        data_out.nco2 = 0;
        data_out.fir = 0;
        data_out.adc = get_data_from_mbf_memory(mbf_axis, 0, n_turns);
        data_out.dac = get_data_from_mbf_memory(mbf_axis, 1, n_turns);
        save_to_archive(root_string, data_out)
    end %for

    % NCO1 on
    nco1_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'};
    nco1_labels = regexprep(nco1_gains, '-', 'm');
    for emw = 1:length(nco1_gains)
        mbf_checkout_setup(mbf_axis, 'loopback', lb_state{bwe}, 'nco1', 'yes',...
            'nco1_gain', nco1_gains{emw})
        pause(1)
        lcaPut('SR23C-DI-TMBF-01:MEM:CAPTURE_S.PROC', 1)
        pause(1)
        data_out.time = exp_time;
        data_out.base_name = [base_name '_nco1_gain_' nco1_labels{emw} lb_status{bwe}];
        data_out.nco1_gain = nco1_gains{emw};
        data_out.loopback = lb_status{bwe};
        data_out.tune = 0;
        data_out.nco1 = 1;
        data_out.nco2 = 0;
        data_out.fir = 0;
        data_out.adc = get_data_from_mbf_memory(mbf_axis, 0, n_turns);
        data_out.dac = get_data_from_mbf_memory(mbf_axis, 1, n_turns);

        save_to_archive(root_string, data_out)
    end %for

    % NCO2 on
    nco2_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'};
    nco2_labels = regexprep(nco2_gains, '-', 'm');
    for emw = 1:length(nco2_gains)
        mbf_checkout_setup(mbf_axis, 'loopback', lb_state{bwe}, 'nco2', 'yes',...
            'nco2_gain', nco2_gains{emw})
        pause(1)
        lcaPut('SR23C-DI-TMBF-01:MEM:CAPTURE_S.PROC', 1)
        pause(1)
        data_out.time = exp_time;
        data_out.base_name = [base_name '_nco2_gain_' nco2_labels{emw} lb_status{bwe}];
        data_out.nco2_gain = nco2_gains{emw};
        data_out.loopback = lb_status{bwe};
        data_out.tune = 0;
        data_out.nco1 = 0;
        data_out.nco2 = 1;
        data_out.fir = 0;
        data_out.adc = get_data_from_mbf_memory(mbf_axis, 0, n_turns);
        data_out.dac = get_data_from_mbf_memory(mbf_axis, 1, n_turns);
        save_to_archive(root_string, data_out)
    end %for

    % FIR on
    nco1_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'};
    fir_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'};
    fir_labels = regexprep(fir_gains, '-', 'm');
    nco1_labels = regexprep(nco1_gains, '-', 'm');
    for bes = 1:length(nco1_gains)
        for emw = 1:length(fir_gains)
            mbf_checkout_setup(mbf_axis, 'loopback', lb_state{bwe}, 'fir', 'yes',...
                'fir_gain', fir_gains{emw},'nco1', 'yes', 'nco1_gain', nco1_gains{bes})
            pause(1)
            lcaPut('SR23C-DI-TMBF-01:MEM:CAPTURE_S.PROC', 1)
            pause(1)
            data_out.time = exp_time;
            data_out.base_name = [base_name '_fir_gain_' fir_labels{emw} ...
                '_nco1_gain_' nco1_labels{bes} lb_status{bwe}];
            data_out.nco1_gain = nco1_gains{bes};
            data_out.fir_gain = fir_gains{emw};
            data_out.loopback = lb_status{bwe};
            data_out.tune = 0;
            data_out.nco1 = 1;
            data_out.nco2 = 0;
            data_out.fir = 1;
            data_out.adc = get_data_from_mbf_memory(mbf_axis, 0, n_turns);
            data_out.dac = get_data_from_mbf_memory(mbf_axis, 1, n_turns);

            save_to_archive(root_string, data_out)
        end %for
    end %for
end %for
 initialise_checkout(mbf_axis)