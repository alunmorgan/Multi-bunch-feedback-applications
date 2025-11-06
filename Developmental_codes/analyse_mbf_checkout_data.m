function analyse_mbf_checkout_data(mbf_axis, display_units)

conditioned_data = mbf_checkout_archival_retrieval(mbf_axis, [datetime(2025, 11, 06, 11, 55, 00), datetime("now")]);

for jwsc = 1:length(conditioned_data)
    if isfield(conditioned_data{jwsc}{1}, 'tune_gain')
        tune_gains(jwsc) = str2double(regexprep(conditioned_data{jwsc}{1}.tune_gain, 'dB', ''));
    else
        tune_gains(jwsc) = 0;
    end %if
    if isfield(conditioned_data{jwsc}{1}, 'nco1_gain')
        nco1_gains(jwsc) = str2double(regexprep(conditioned_data{jwsc}{1}.nco1_gain, 'dB', ''));
    else
        nco1_gains(jwsc) = 0;
    end %if
    if isfield(conditioned_data{jwsc}{1}, 'nco2_gain')
        nco2_gains(jwsc) = str2double(regexprep(conditioned_data{jwsc}{1}.nco2_gain, 'dB', ''));
    else
        nco2_gains(jwsc) = 0;
    end %if
    if isfield(conditioned_data{jwsc}{1}, 'fir_gain')
        fir_gains(jwsc) = str2double(regexprep(conditioned_data{jwsc}{1}.fir_gain, 'dB', ''));
    else
        fir_gains(jwsc)  = 0;
    end %if
    if isfield(conditioned_data{jwsc}{1}, 'loopback')
        if contains(conditioned_data{jwsc}{1}.loopback, '_no_loopback')
            loopback(jwsc) = 0;
        elseif contains(conditioned_data{jwsc}{1}.loopback, '_with_loopback')
            loopback(jwsc) = 1;
        end %if;
    else
        loopback(jwsc) = 0;
    end %if
    tune_status(jwsc) = conditioned_data{jwsc}{1}.tune;
    nco1_status(jwsc) = conditioned_data{jwsc}{1}.nco1;
    nco2_status(jwsc) = conditioned_data{jwsc}{1}.nco2;
    fir_status(jwsc) = conditioned_data{jwsc}{1}.fir;
end %for


tune_on = find(tune_status == 1);
nco1_on = find(nco1_status == 1);
nco2_on = find(nco2_status == 1);
fir_on = find(fir_status == 1);

tune_off = find(tune_status == 0);
nco1_off = find(nco1_status == 0);
nco2_off = find(nco2_status == 0);
fir_off = find(fir_status == 0);

loopback_off = find(loopback ==0);
loopback_on = find(loopback ==1);

tune_sweep_lb_off =intersect_all(tune_on, fir_off, nco1_off, nco2_off, loopback_off);
nco1_sweep_lb_off =intersect_all(tune_off, fir_off, nco1_on, nco2_off, loopback_off);
nco2_sweep_lb_off =intersect_all(tune_off, fir_off, nco1_off, nco2_on, loopback_off);
fir_sweep_lb_off =intersect_all(tune_off, fir_on, nco1_on, nco2_off, loopback_off);

tune_sweep_lb_on =intersect_all(tune_on, fir_off, nco1_off, nco2_off, loopback_on);
nco1_sweep_lb_on =intersect_all(tune_off, fir_off, nco1_on, nco2_off, loopback_on);
nco2_sweep_lb_on =intersect_all(tune_off, fir_off, nco1_off, nco2_on, loopback_on);
fir_sweep_lb_on =intersect_all(tune_off, fir_on, nco1_on, nco2_off, loopback_on);


graph_title = ['MBF data ', mbf_axis,' axis. Tune gain sweep (Loopback off)'];
graph_data = conditioned_data(tune_sweep_lb_off);
sweep_gains = tune_gains(tune_sweep_lb_off);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO1 gain sweep (Loopback off)'];
graph_data = conditioned_data(nco1_sweep_lb_off);
sweep_gains = nco1_gains(nco1_sweep_lb_off);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO2 gain sweep (Loopback off)'];
graph_data = conditioned_data(nco2_sweep_lb_off);
sweep_gains = nco2_gains(nco2_sweep_lb_off);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. FIR gain sweep (Loopback off)'];
graph_data = conditioned_data(fir_sweep_lb_off);
sweep_gains = fir_gains(fir_sweep_lb_off);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. Tune gain sweep (Loopback on)'];
graph_data = conditioned_data(tune_sweep_lb_on);
sweep_gains = tune_gains(tune_sweep_lb_on);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO1 gain sweep (Loopback on)'];
graph_data = conditioned_data(nco1_sweep_lb_on);
sweep_gains = nco1_gains(nco1_sweep_lb_on);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO2 gain sweep (Loopback on)'];
graph_data = conditioned_data(nco2_sweep_lb_on);
sweep_gains = nco2_gains(nco2_sweep_lb_on);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. FIR gain sweep (Loopback on)'];
graph_data = conditioned_data(fir_sweep_lb_on);
sweep_gains = fir_gains(fir_sweep_lb_on);
if ~isempty(sweep_gains)
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if


disp('')
end %function

function temp = intersect_all(varargin)
temp = intersect(varargin{1}, varargin{2});
if length(varargin) >2
    for hse = 3:length(varargin)
        temp = intersect(temp, varargin{hse});
    end %for
end %if
end %function

function data_out = fft_mbf_data(data)
% Generating the frequency scales
n_bunches = data.n_turns .* data.harmonic_number;
timescale = (1:n_bunches) ./ data.RF; %sec
timestep = timescale(2) - timescale(1);
f_scale = 1./timestep .* (0:n_bunches-1) ./n_bunches; %Hz
data_out.f_data = abs(fft(data.timedata));
data_out.f_scale_hz = f_scale(1:n_bunches/2);
data_out.f_scale_tune = data_out.f_scale_hz ./ (data.RF .* data.harmonic_number);
data_out.f_data = data_out.f_data(1:n_bunches/2);
data_out.t_scale_time = timescale;
data_out.t_scale_ticks = timescale ./ timestep;
data_out.t_data = data.timedata;
end %function

function plot_sweep(conditioned_data, sweep_gains, graph_title, display_units)

figure('Position', [20, 40, 1600, 800])
t = tiledlayout(2, 2);
title(t, graph_title)
for jse = 1:length(sweep_gains)
    adc_data = conditioned_data{jse}{1}.adc;
    dac_data = conditioned_data{jse}{1}.dac;
    adc_plot_data = fft_mbf_data(adc_data);
    dac_plot_data = fft_mbf_data(dac_data);
    if display_units == 0
        adc_t_scale = adc_plot_data.t_scale_time * 1E6;
        adc_f_scale = adc_plot_data.f_scale_hz * 1E-6;
        dac_t_scale = dac_plot_data.t_scale_time * 1E6;
        dac_f_scale = dac_plot_data.f_scale_hz * 1E-6;
        t_x_lab = 'Time (us)';
        f_x_lab = 'Frequency (MHz)';
    else
        adc_t_scale = adc_plot_data.t_scale_ticks;
        adc_f_scale = adc_plot_data.f_scale_tune;
        dac_t_scale = dac_plot_data.t_scale_ticks;
        dac_f_scale = dac_plot_data.f_scale_tune;
        t_x_lab = 'Ticks of 1/f_{rev} (~2ns)';
        f_x_lab = 'Tune';
    end %if

    [main_adc_amp(jse), madci] = max(adc_plot_data.f_data);
    main_adc_f(jse) = adc_f_scale(madci);
    [main_dac_amp(jse), mdaci] = max(dac_plot_data.f_data);
    main_dac_f(jse) = dac_f_scale(mdaci);

    if jse == 1
    adc_x_limits = find_limits_around_peak(adc_plot_data.f_data, adc_f_scale, main_adc_amp(jse), madci)
    dac_x_limits = find_limits_around_peak(dac_plot_data.f_data, dac_f_scale, main_dac_amp(jse), mdaci)
    end %if

    nexttile(1);
    hold on
    plot(adc_t_scale, adc_plot_data.t_data, 'DisplayName', num2str(sweep_gains(jse)))
    ylabel('ADC')
    xlabel(t_x_lab)
    legend
    grid on
    nexttile(2);
    hold on
    plot(adc_f_scale, adc_plot_data.f_data, 'DisplayName', num2str(sweep_gains(jse)))
    ylabel(' ')
    xlabel(f_x_lab)
    legend
    xlim(adc_x_limits)
    grid on
    nexttile(3);
    hold on
    plot(dac_t_scale, dac_plot_data.t_data, 'DisplayName', num2str(sweep_gains(jse)))
    ylabel('DAC')
    xlabel(t_x_lab)
    legend
    grid on
    nexttile(4);
    hold on
    plot(dac_f_scale, dac_plot_data.f_data, 'DisplayName', num2str(sweep_gains(jse)))
    ylabel(' ')
    xlabel(f_x_lab)
    legend
    xlim(dac_x_limits)
    grid on
end %for
figure('Position', [20, 40, 800, 800])
t = tiledlayout(2, 2);
title(t, graph_title)
nexttile
plot(sweep_gains, main_adc_f, '*')
xlabel('Sweep gain')
ylabel({'ADC';f_x_lab})
nexttile
plot(sweep_gains, main_adc_amp, '*')
xlabel('Sweep gain')
ylabel('Signal')
nexttile
plot(sweep_gains, main_dac_f, '*')
xlabel('Sweep gain')
ylabel(f_x_lab)
nexttile
plot(sweep_gains, main_dac_amp, '*')
xlabel('Sweep gain')
ylabel('Signal')
end %function

function x_limits = find_limits_around_peak(data, scale, peak_amp, peak_ind)
begin_peak_ind = find(data(1:peak_ind) < (peak_amp ./ 1000), 1, 'last');
if ~isempty(begin_peak_ind)
    begin_peak = scale(begin_peak_ind);
else
    begin_peak = 0;
    begin_peak_ind = 1;
end %if
end_peak = scale(peak_ind + (peak_ind - begin_peak_ind));
if end_peak > begin_peak
    x_limits = [begin_peak, end_peak];
else
    x_limits = [begin_peak, inf];
end %if
end %function