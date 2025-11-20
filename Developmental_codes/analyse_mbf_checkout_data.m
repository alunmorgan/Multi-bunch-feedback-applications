function analyse_mbf_checkout_data(mbf_axis, display_units)
% Dispaly units (bool): 0 = SI, 1 = Tune units

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
sweep_gains = {tune_gains(tune_sweep_lb_off)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO1 gain sweep (Loopback off)'];
graph_data = conditioned_data(nco1_sweep_lb_off);
sweep_gains = {nco1_gains(nco1_sweep_lb_off)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO2 gain sweep (Loopback off)'];
graph_data = conditioned_data(nco2_sweep_lb_off);
sweep_gains = {nco2_gains(nco2_sweep_lb_off)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. FIR gain sweep (Loopback off)'];
graph_data = conditioned_data(fir_sweep_lb_off);
sweep_gains = {fir_gains(fir_sweep_lb_off), nco1_gains(fir_sweep_lb_off)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. Tune gain sweep (Loopback on)'];
graph_data = conditioned_data(tune_sweep_lb_on);
sweep_gains = {tune_gains(tune_sweep_lb_on)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO1 gain sweep (Loopback on)'];
graph_data = conditioned_data(nco1_sweep_lb_on);
sweep_gains = {nco1_gains(nco1_sweep_lb_on)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. NCO2 gain sweep (Loopback on)'];
graph_data = conditioned_data(nco2_sweep_lb_on);
sweep_gains = {nco2_gains(nco2_sweep_lb_on)};
if ~isempty(sweep_gains{1})
    plot_sweep(graph_data, sweep_gains, graph_title, display_units)
end %if

graph_title = ['MBF data ', mbf_axis,' axis. FIR gain sweep (Loopback on)'];
graph_data = conditioned_data(fir_sweep_lb_on);
sweep_gains = {fir_gains(fir_sweep_lb_on), nco1_gains(fir_sweep_lb_on)};
if ~isempty(sweep_gains{1})
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



for jse = 1:length(conditioned_data)
    plot_scan_data.adc_data(jse) = conditioned_data{jse}{1}.adc;
    plot_scan_data.dac_data(jse) = conditioned_data{jse}{1}.dac;
    plot_scan_data.adc_plot_data(jse) = fft_mbf_data(plot_scan_data.adc_data(jse));
    plot_scan_data.dac_plot_data(jse) = fft_mbf_data(plot_scan_data.dac_data(jse));


    if jse == 1
        if display_units == 0
            plot_scan_data.adc_t_scale = plot_scan_data.adc_plot_data(jse).t_scale_time * 1E6;
            plot_scan_data.adc_f_scale = plot_scan_data.adc_plot_data(jse).f_scale_hz * 1E-6;
            plot_scan_data.dac_t_scale = plot_scan_data.dac_plot_data(jse).t_scale_time * 1E6;
            plot_scan_data.dac_f_scale = plot_scan_data.dac_plot_data(jse).f_scale_hz * 1E-6;
            plot_scan_data.t_x_lab = 'Time (us)';
            plot_scan_data.f_x_lab = 'Frequency (MHz)';
        else
            plot_scan_data.adc_t_scale = plot_scan_data.adc_plot_data(jse).t_scale_ticks;
            plot_scan_data.adc_f_scale = plot_scan_data.adc_plot_data(jse).f_scale_tune;
            plot_scan_data.dac_t_scale = plot_scan_data.dac_plot_data(jse).t_scale_ticks;
            plot_scan_data.dac_f_scale = plot_scan_data.dac_plot_data(jse).f_scale_tune;
            plot_scan_data.t_x_lab = 'Ticks of 1/f_{rev} (~2ns)';
            plot_scan_data.f_x_lab = 'Tune';
        end %if
    end %if

    [plot_scan_data.main_adc_amp(jse), madci] = max(plot_scan_data.adc_plot_data(jse).f_data);
    plot_scan_data.main_adc_f(jse) = plot_scan_data.adc_f_scale(madci);
    [plot_scan_data.main_dac_amp(jse), mdaci] = max(plot_scan_data.dac_plot_data(jse).f_data);
    plot_scan_data.main_dac_f(jse) = plot_scan_data.dac_f_scale(mdaci);

    if jse == 1
        plot_scan_data.adc_x_limits = find_limits_around_peak(...
            plot_scan_data.adc_plot_data.f_data, plot_scan_data.adc_f_scale,...
            plot_scan_data.main_adc_amp(jse), madci);
        plot_scan_data.dac_x_limits = find_limits_around_peak(...
            plot_scan_data.dac_plot_data.f_data, plot_scan_data.dac_f_scale,...
            plot_scan_data.main_dac_amp(jse), mdaci);
    end %if



end %for
if length(sweep_gains) > 1
    plot_2D_scan(plot_scan_data, sweep_gains, {'FIR gain', 'NCO1 gain'}, graph_title)
else
    plot_1D_scan(plot_scan_data, sweep_gains{1}, graph_title)
end %if
end %function

function plot_2D_scan(data, sweep_gains, sweep_names, graph_title)

sweep1 = sweep_gains{1};
sweep2 = sweep_gains{2};

sweep1_values = unique(sweep1);
col_cycle = [0, 1, 0.5, 0.25, 0.75];
ck =1;
loop_length = ceil(length(sweep1_values).^0.33);
col_cycle = col_cycle(1:loop_length);
for ns = 1:length(col_cycle)
    for fsb = 1:length(col_cycle)
        for jdf = 1:length(col_cycle)
            cols(ck,1) = col_cycle(mod(ns-1,length(col_cycle))+1);
            cols(ck,2) = col_cycle(mod(fsb-1,length(col_cycle))+1);
            cols(ck,3) = col_cycle(mod(jdf-1,length(col_cycle))+1);
            ck = ck +1;
        end %for
    end %for
end %for
cols = cols(1:length(sweep1_values),:);
figure('Position', [20, 40, 1600, 800])
t = tiledlayout(2, 4);
title(t, graph_title)
seen_inds = zeros(length(data.adc_data), 1);
for jse = 1:length(data.adc_data)
    sweep_ind = find(sweep1_values == sweep1(jse));
    if ~isempty(find(seen_inds == sweep_ind, 1))
        hv = 'off';
    else
        hv = 'on';
    end %if
    seen_inds(jse) = sweep_ind;

    nexttile(1);
    hold on
    plot3(ones(length(1:data.adc_data(jse).harmonic_number) , 1).* sweep2(jse),...
        data.adc_t_scale(1:data.adc_data(jse).harmonic_number),...
        data.adc_plot_data(jse).t_data(1:data.adc_data(jse).harmonic_number),...
        'Color', cols(sweep_ind,:),...
        'DisplayName', [sweep_names{1}, ' ' ,num2str(sweep1(jse))],...
        'HandleVisibility',hv)

    zlabel('ADC')
    ylabel(data.t_x_lab)
    xlabel(sweep_names{2})
    title('Single turn')
    lg = legend;
    lg.Layout.Tile = 'west';
    grid on
    view([45, 45])

    nexttile(2);
    hold on
    plot3(ones(length(data.adc_f_scale), 1) .* sweep2(jse), ...
        data.adc_f_scale,...
        data.adc_plot_data(jse).f_data,...
        'Color', cols(sweep_ind,:),...
        'DisplayName', [num2str(sweep1(jse)), ' ', num2str(sweep2(jse))])
    xlabel(sweep_names{2})
    zlabel(' ')
    ylabel(data.f_x_lab)
    ylim(data.adc_x_limits)
    grid on
    view([45, 45])

    nexttile(5);
    hold on
    plot3(ones(length(1:data.dac_data(jse).harmonic_number) , 1).* sweep2(jse),...
        data.dac_t_scale(1:data.dac_data(jse).harmonic_number), ...
        data.dac_plot_data(jse).t_data(1:data.dac_data(jse).harmonic_number),...
        'Color', cols(sweep_ind,:),...
        'DisplayName', [num2str(sweep1(jse)), ' ', num2str(sweep2(jse))])
    zlabel('DAC')
    ylabel(data.t_x_lab)
    xlabel(sweep_names{2})
    title('Single turn')
    grid on
    view([45, 45])

    nexttile(6);
    hold on
    plot3(ones(length(data.dac_f_scale) , 1).* sweep2(jse),...
        data.dac_f_scale,...
        data.dac_plot_data(jse).f_data,...
        'Color', cols(sweep_ind,:),...
        'DisplayName', [num2str(sweep1(jse)), ' ', num2str(sweep2(jse))])
    zlabel(' ')
    ylabel(data.f_x_lab)
    xlabel(sweep_names{2})
    ylim(data.dac_x_limits)
    grid on
    view([45, 45])

end %for

nexttile(3)
scatter3(sweep1, sweep2, data.main_adc_f, '*')
xlabel(sweep_names{1})
ylabel(sweep_names{2})
zlabel({'ADC';data.f_x_lab})
nexttile(4)
scatter3(sweep1, sweep2, data.main_adc_amp, '*')
xlabel(sweep_names{1})
ylabel(sweep_names{2})
zlabel('Signal')
nexttile(7)
scatter3(sweep1, sweep2, data.main_dac_f, '*')
xlabel(sweep_names{1})
ylabel(sweep_names{2})
zlabel(data.f_x_lab)
nexttile(8)
scatter3(sweep1, sweep2, data.main_dac_amp, '*')
xlabel(sweep_names{1})
ylabel(sweep_names{2})
zlabel('Signal')
end %function

function plot_1D_scan(data, sweep_gains, graph_title)

figure('Position', [20, 40, 1600, 800])
t = tiledlayout(2, 4);
title(t, graph_title)
for jse = 1:length(data.adc_data)

    nexttile(1);
    hold on
    plot(data.adc_t_scale(1:data.adc_data(jse).harmonic_number),...
        data.adc_plot_data(jse).t_data(1:data.adc_data(jse).harmonic_number),...
        'DisplayName', num2str(sweep_gains(jse)))
    ylabel('ADC')
    xlabel(data.t_x_lab)
    title('Single turn')
    lg = legend;
    lg.Layout.Tile = 'west';
    grid on
    nexttile(2);
    hold on
    plot(data.adc_f_scale, data.adc_plot_data(jse).f_data,...
        'DisplayName', num2str(sweep_gains(jse)))
    ylabel(' ')
    xlabel(data.f_x_lab)
    xlim(data.adc_x_limits)
    grid on
    nexttile(5);
    hold on
    plot(data.dac_t_scale(1:data.dac_data(jse).harmonic_number), ...
        data.dac_plot_data(jse).t_data(1:data.dac_data(jse).harmonic_number),...
        'DisplayName', num2str(sweep_gains(jse)))
    ylabel('DAC')
    xlabel(data.t_x_lab)
    title('Single turn')
    grid on
    nexttile(6);
    hold on
    plot(data.dac_f_scale, data.dac_plot_data(jse).f_data, 'DisplayName', num2str(sweep_gains(jse)))
    ylabel(' ')
    xlabel(data.f_x_lab)
    xlim(data.dac_x_limits)
    grid on
end %for

nexttile(3)
plot(sweep_gains, data.main_adc_f, '*')
xlabel('Sweep gain')
ylabel({'ADC';data.f_x_lab})
nexttile(4)
plot(sweep_gains, data.main_adc_amp, '*')
xlabel('Sweep gain')
ylabel('Signal')
nexttile(7)
plot(sweep_gains, data.main_dac_f, '*')
xlabel('Sweep gain')
ylabel(data.f_x_lab)
nexttile(8)
plot(sweep_gains, data.main_dac_amp, '*')
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