function data_out = get_data_from_mbf_memory(mbf_axis, chan, n_turns)
mbf_tools
[~,harmonic_number, pv_names, ~] = mbf_system_config;
data_out.RF = lcaGet(pv_names.RF);

if strcmpi(mbf_axis, 's')
    system_name = pv_names.hardware_names.L;
    system_axis_name = pv_names.hardware_names.s;
    mem_lock = 60; %180;
elseif strcmpi(mbf_axis, 'x')
    system_name = pv_names.hardware_names.T;
        system_axis_name = pv_names.hardware_names.x;
    mem_lock = 60; %30;
    elseif strcmpi(mbf_axis, 'y')
    system_name = pv_names.hardware_names.T;
        system_axis_name = pv_names.hardware_names.y;
    mem_lock = 60; %30;
end %if

if chan == 0
    target_location =  lcaGet([system_name pv_names.tails.MEM.channel0_target]);
elseif chan == 1
    target_location =  lcaGet([system_name pv_names.tails.MEM.channel1_target]);
end %if

target_location = target_location{1};
if contains(target_location, 'DAC0')
    trgt_extra = lcaGet([system_axis_name pv_names.tails.dac.dram_source]);
elseif contains(target_location, 'DAC1')
    trgt_extra = lcaGet([system_axis_name pv_names.tails.dac.dram_source]);
elseif contains(target_location, 'ADC0')
    trgt_extra = lcaGet([system_axis_name pv_names.tails.adc.dram_source]);
elseif contains(target_location, 'ADC1')
    trgt_extra = lcaGet([system_axis_name pv_names.tails.adc.dram_source]);
else
    trgt_extra = '';
end %if
trgt_extra = trgt_extra{1};

data = mbf_read_mem(system_name, n_turns,'channel', chan, 'lock', mem_lock);

% [data, data_freq, ~] = mbf_read_det(system_name, 'axis', chan, 'lock', mem_lock);

data_out.timedata = data;
data_out.n_turns = n_turns;
data_out.ax_label = mbf_axis;
data_out.datasource = [target_location, ' ', trgt_extra];
data_out.harmonic_number = harmonic_number;

