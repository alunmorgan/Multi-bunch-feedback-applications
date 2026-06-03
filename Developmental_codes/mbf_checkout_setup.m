function mbf_checkout_setup(mbf_axis, varargin)
% Sets the MBF system specified to have the desired signals passing
% through the system.
%
% Example: mbf_checkout_setup('x')

mbf_p = inputParser;
mbf_p.StructExpand = false;
mbf_p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

addRequired(mbf_p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(mbf_p, 'tune', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'nco1', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'nco2', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'loopback', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'fir', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(mbf_p, 'fir_gain', '-42dB');
addParameter(mbf_p, 'nco1_gain', '-36dB');
addParameter(mbf_p, 'nco2_gain', '-36dB');
addParameter(mbf_p, 'tune_gain', '-42dB');

% parse(p, mbf_axis);
parse(mbf_p, mbf_axis, varargin{:});

[~, harmonic_number, pv_names, ~] = mbf_system_config;
system_axis = pv_names.hardware_names.(mbf_axis);
nco1 = pv_names.tails.NCO1;
nco2 = pv_names.tails.NCO2;
bb1 = pv_names.tails.Bunch_bank.bank1;
fir = pv_names.tails.FIR;
tune = pv_names.tails.Sequencer.seq1;
adc = pv_names.tails.adc;

n_cycles = 1;
initialise_checkout(mbf_axis)

if strcmp(mbf_p.Results.nco1, 'yes')
    lcaPut([system_axis nco1.frequency], n_cycles)
    lcaPut([system_axis nco1.gaindb], mbf_p.Results.nco1_gain)
    lcaPut([system_axis nco1.enable], 'On')
    lcaPut([system_axis bb1.NCO1.enablewf], ones(1, harmonic_number))
end %if

if strcmp(mbf_p.Results.nco2, 'yes')
    lcaPut([system_axis nco2.frequency], n_cycles)
    lcaPut([system_axis nco2.gain_db], mbf_p.Results.nco2_gain)
    lcaPut([system_axis nco2.enable], 'On')
    lcaPut([system_axis bb1.NCO2.enablewf], ones(1, harmonic_number))
end %if

if strcmp(mbf_p.Results.fir, 'yes')
    lcaPut([system_axis fir.gain], mbf_p.Results.fir_gain)
    lcaPut([system_axis bb1.FIR.enablewf], ones(1, harmonic_number))
end %if

if strcmp(mbf_p.Results.tune, 'yes')
    lcaPut([system_axis tune.gaindb], mbf_p.Results.tune_gain)
    lcaPut([system_axis tune.enable], 'On')
    lcaPut([system_axis bb1.SEQ.enablewf], ones(1, harmonic_number))
end %if

if strcmp(mbf_p.Results.loopback, 'yes')
    lcaPut([system_axis adc.loopback], 'Loopback')
end %if
