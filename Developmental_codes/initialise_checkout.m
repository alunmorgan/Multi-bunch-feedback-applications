function initialise_checkout(mbf_axis)
% Set all signals to off for the testing.

[~, harmonic_number, pv_names, ~] = mbf_system_config;
system_axis = pv_names.hardware_names.(mbf_axis);
bb = pv_names.tails.Bunch_bank.bank1;
seq = pv_names.tails.Sequencer.seq1;
nco1 = pv_names.tails.NCO1;
nco2 = pv_names.tails.NCO2;
adc = pv_names.tails.adc;

% Set all bank 1 entries to disabled.
lcaPut([system_axis bb.NCO1.enablewf], zeros(1, harmonic_number))
lcaPut([system_axis bb.NCO2.enablewf], zeros(1, harmonic_number))
lcaPut([system_axis bb.FIR.enablewf], zeros(1, harmonic_number))
lcaPut([system_axis bb.SEQ.enablewf], zeros(1, harmonic_number))
lcaPut([system_axis bb.PLL.enablewf], zeros(1, harmonic_number))

% Turn off NCOs
lcaPut([system_axis nco1.enable], 'Off')
lcaPut([system_axis nco2.enable], 'Off')

% Turn off Tune
lcaPut([system_axis seq.enable], 'Off')

% Turn off Loopback
lcaPut([system_axis adc.loopback], 'Normal')


