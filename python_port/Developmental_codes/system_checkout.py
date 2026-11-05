def analyse_mbf_checkout_data(mbf_axis, printlay_units):
    # Dispaly units (bool): 0 = SI, 1 = Tune units
    conditioned_data = mbf_checkout_archival_retrieval(mbf_axis, [datetime(2025, 11, 06, 11, 55, 00), datetime("now")])
    tune_gains = zeros(len(conditioned_data), 1)
    nco1_gains = zeros(len(conditioned_data), 1)
    nco2_gains = zeros(len(conditioned_data), 1)
    fir_gains = zeros(len(conditioned_data), 1)
    loopback = zeros(len(conditioned_data), 1)
    tune_status = nan(len(conditioned_data), 1)
    nco1_status = nan(len(conditioned_data), 1)
    nco2_status = nan(len(conditioned_data), 1)
    fir_status = nan(len(conditioned_data), 1)
    for jwsc  in range( 1, len(conditioned_data)):
        if 'tune_gain' in conditioned_data[jwsc][1]:
            tune_gains(jwsc) = str2double(regexprep(conditioned_data[jwsc][1]['tune_gain'], 'dB', ''))

        if 'nco1_gain' in conditioned_data[jwsc][1]:
            nco1_gains(jwsc) = str2double(regexprep(conditioned_data[jwsc][1]['nco1_gain'], 'dB', ''))

        if 'nco2_gain' in conditioned_data[jwsc][1]:
            nco2_gains(jwsc) = str2double(regexprep(conditioned_data[jwsc][1]['nco2_gain'], 'dB', ''))

        if 'fir_gain' in conditioned_data[jwsc][1]:
            fir_gains(jwsc) = str2double(regexprep(conditioned_data[jwsc][1]['fir_gain'], 'dB', ''))

        if 'loopback' in conditioned_data[jwsc][1]:
            if contains(conditioned_data[jwsc][1]['loopback'], '_with_loopback'):
                loopback(jwsc) = 1


        tune_status(jwsc) = conditioned_data[jwsc][1]['tune']
        nco1_status(jwsc) = conditioned_data[jwsc][1]['nco1']
        nco2_status(jwsc) = conditioned_data[jwsc][1]['nco2']
        fir_status(jwsc) = conditioned_data[jwsc][1]['fir']

    tune_on = find(tune_status == 1)
    nco1_on = find(nco1_status == 1)
    nco2_on = find(nco2_status == 1)
    fir_on = find(fir_status == 1)
    tune_off = find(tune_status == 0)
    nco1_off = find(nco1_status == 0)
    nco2_off = find(nco2_status == 0)
    fir_off = find(fir_status == 0)
    loopback_off = find(loopback ==0)
    loopback_on = find(loopback ==1)
    tune_sweep_lb_off =intersect_all(tune_on, fir_off, nco1_off, nco2_off, loopback_off)
    nco1_sweep_lb_off =intersect_all(tune_off, fir_off, nco1_on, nco2_off, loopback_off)
    nco2_sweep_lb_off =intersect_all(tune_off, fir_off, nco1_off, nco2_on, loopback_off)
    fir_sweep_lb_off =intersect_all(tune_off, fir_on, nco1_on, nco2_off, loopback_off)
    tune_sweep_lb_on =intersect_all(tune_on, fir_off, nco1_off, nco2_off, loopback_on)
    nco1_sweep_lb_on =intersect_all(tune_off, fir_off, nco1_on, nco2_off, loopback_on)
    nco2_sweep_lb_on =intersect_all(tune_off, fir_off, nco1_off, nco2_on, loopback_on)
    fir_sweep_lb_on =intersect_all(tune_off, fir_on, nco1_on, nco2_off, loopback_on)
    graph_title = ['MBF data ', mbf_axis,' axis[''] Tune gain sweep (Loopback off)']
    graph_data = conditioned_data(tune_sweep_lb_off)
    sweep_gains = {tune_gains(tune_sweep_lb_off)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] NCO1 gain sweep (Loopback off)']
    graph_data = conditioned_data(nco1_sweep_lb_off)
    sweep_gains = {nco1_gains(nco1_sweep_lb_off)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] NCO2 gain sweep (Loopback off)']
    graph_data = conditioned_data(nco2_sweep_lb_off)
    sweep_gains = {nco2_gains(nco2_sweep_lb_off)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] FIR gain sweep (Loopback off)']
    graph_data = conditioned_data(fir_sweep_lb_off)
    sweep_gains = {fir_gains(fir_sweep_lb_off), nco1_gains(fir_sweep_lb_off)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] Tune gain sweep (Loopback on)']
    graph_data = conditioned_data(tune_sweep_lb_on)
    sweep_gains = {tune_gains(tune_sweep_lb_on)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] NCO1 gain sweep (Loopback on)']
    graph_data = conditioned_data(nco1_sweep_lb_on)
    sweep_gains = {nco1_gains(nco1_sweep_lb_on)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] NCO2 gain sweep (Loopback on)']
    graph_data = conditioned_data(nco2_sweep_lb_on)
    sweep_gains = {nco2_gains(nco2_sweep_lb_on)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    graph_title = ['MBF data ', mbf_axis,' axis[''] FIR gain sweep (Loopback on)']
    graph_data = conditioned_data(fir_sweep_lb_on)
    sweep_gains = {fir_gains(fir_sweep_lb_on), nco1_gains(fir_sweep_lb_on)}
    if  sweep_gains[1]:
        plot_sweep(graph_data, sweep_gains, graph_title, printlay_units)

    print('')

    return 

def intersect_all(varargin):
    temp = intersect(varargin[1], varargin[2])
    if len(varargin) >2:
        for hse  in range( 3, len(varargin)):
            temp = intersect(temp, varargin[hse])



    return temp 

def fft_mbf_data(data):
    # Generating the frequency scales
    n_bunches = data['n_turns'] ['']* data['harmonic_number']
    timescale = [1:n_bunches] ['']/ data['RF']; #sec
    timestep = timescale(2) - timescale(1)
    f_scale = 1['']/timestep ['']* [0:n_bunches-1] ['']/n_bunches; #Hz
    data_out['f_data'] = abs(fft(data['timedata']))
    data_out['f_scale_hz'] = f_scale[1:n_bunches/2]
    data_out['f_scale_tune'] = data_out['f_scale_hz'] ['']/ (data['RF'] ['']* data['harmonic_number'])
    data_out['f_data'] = data_out['f_data'][1:n_bunches/2]
    data_out['t_scale_time'] = timescale
    data_out['t_scale_ticks'] = timescale ['']/ timestep
    data_out['t_data'] = data['timedata']

def plot_sweep(conditioned_data, sweep_gains, graph_title, printlay_units):
    for jse  in range( 1, len(conditioned_data)):
        plot_scan_data['adc_data'](jse) = conditioned_data[jse][1]['adc']
        plot_scan_data['dac_data'](jse) = conditioned_data[jse][1]['dac']
        plot_scan_data['adc_plot_data'](jse) = fft_mbf_data(plot_scan_data['adc_data'](jse))
        plot_scan_data['dac_plot_data'](jse) = fft_mbf_data(plot_scan_data['dac_data'](jse))
        if jse == 1:
            if printlay_units == 0:
                plot_scan_data['adc_t_scale'] = plot_scan_data['adc_plot_data'](jse)['t_scale_time'] * 1E6
                plot_scan_data['adc_f_scale'] = plot_scan_data['adc_plot_data'](jse)['f_scale_hz'] * 1E-6
                plot_scan_data['dac_t_scale'] = plot_scan_data['dac_plot_data'](jse)['t_scale_time'] * 1E6
                plot_scan_data['dac_f_scale'] = plot_scan_data['dac_plot_data'](jse)['f_scale_hz'] * 1E-6
                plot_scan_data['t_x_lab'] = 'Time (us)'
                plot_scan_data['f_x_lab'] = 'Frequency (MHz)'
            else:
                plot_scan_data['adc_t_scale'] = plot_scan_data['adc_plot_data'](jse)['t_scale_ticks']
                plot_scan_data['adc_f_scale'] = plot_scan_data['adc_plot_data'](jse)['f_scale_tune']
                plot_scan_data['dac_t_scale'] = plot_scan_data['dac_plot_data'](jse)['t_scale_ticks']
                plot_scan_data['dac_f_scale'] = plot_scan_data['dac_plot_data'](jse)['f_scale_tune']
                plot_scan_data['t_x_lab'] = 'Ticks of 1/f_[rev] (~2ns)'
                plot_scan_data['f_x_lab'] = 'Tune'


        [plot_scan_data['main_adc_amp'](jse), madci] = max(plot_scan_data['adc_plot_data'](jse)['f_data'])
        plot_scan_data['main_adc_f'](jse) = plot_scan_data['adc_f_scale'](madci)
        [plot_scan_data['main_dac_amp'](jse), mdaci] = max(plot_scan_data['dac_plot_data'](jse)['f_data'])
        plot_scan_data['main_dac_f'](jse) = plot_scan_data['dac_f_scale'](mdaci)
        if jse == 1:
            plot_scan_data['adc_x_limits'] = find_limits_around_peak(
                plot_scan_data['adc_plot_data']['f_data'], plot_scan_data['adc_f_scale'],
                plot_scan_data['main_adc_amp'](jse), madci)
            plot_scan_data['dac_x_limits'] = find_limits_around_peak(
                plot_scan_data['dac_plot_data']['f_data'], plot_scan_data['dac_f_scale'],
                plot_scan_data['main_dac_amp'](jse), mdaci)


    if len(sweep_gains) > 1:
        plot_2D_scan(plot_scan_data, sweep_gains, {'FIR gain', 'NCO1 gain'}, graph_title)
    else:
        plot_1D_scan(plot_scan_data, sweep_gains[1], graph_title)


def plot_2D_scan(data, sweep_gains, sweep_names, graph_title):
    sweep1 = sweep_gains[1]
    sweep2 = sweep_gains[2]
    sweep1_values = unique(sweep1)
    col_cycle = [0, 1, 0['5'], 0['25'], 0['75']]
    cols = zeros(len(col_cycle)^3, 3)
    ck =1
    loop_length = ceil(len(sweep1_values)['']^0['33'])
    col_cycle = col_cycle[1:loop_length]
    for ns  in range( 1, len(col_cycle)):
        for fsb  in range( 1, len(col_cycle)):
            for jdf  in range( 1, len(col_cycle)):
                cols(ck,1) = col_cycle(mod(ns-1,len(col_cycle))+1)
                cols(ck,2) = col_cycle(mod(fsb-1,len(col_cycle))+1)
                cols(ck,3) = col_cycle(mod(jdf-1,len(col_cycle))+1)
                ck = ck +1



    cols = cols(1:len[sweep1_values),:]
    figure('Position', [20, 40, 1600, 800])
    t = tiledlayout(2, 4)
    title(t, graph_title)
    seen_inds = zeros(len(data['adc_data']), 1)
    for jse  in range( 1, len(data['adc_data'])):
        sweep_ind = find(sweep1_values == sweep1(jse))
        if  find(seen_inds == sweep_ind, 1):
            hv = 'off'
        else:
            hv = 'on'

        seen_inds(jse) = sweep_ind
        nexttile(1)
        hold on
        plot3(ones(len(1:data['adc_data'](jse)['harmonic_number']) , 1)['']* sweep2(jse),
            data['adc_t_scale'](1:data['adc_data'](jse)['harmonic_number']),
            data['adc_plot_data'](jse)['t_data'](1:data['adc_data'](jse)['harmonic_number']),
            'Color', cols[sweep_ind,:],
            'DisplayName', [sweep_names[1], ' ' ,(sweep1(jse))],
            'HandleVisibility',hv)
        zlabel('ADC')
        ylabel(data['t_x_lab'])
        xlabel(sweep_names[2])
        title('Single turn')
        lg = legend
        lg['Layout']['Tile'] = 'west'
        grid on
        view([45, 45])
        nexttile(2)
        hold on
        plot3(ones(len(data['adc_f_scale']), 1) ['']* sweep2(jse), 
            data['adc_f_scale'],
            data['adc_plot_data'](jse)['f_data'],
            'Color', cols[sweep_ind,:],
            'DisplayName', [(sweep1(jse)), ' ', num2str(sweep2(jse))])
        xlabel(sweep_names[2])
        zlabel(' ')
        ylabel(data['f_x_lab'])
        ylim(data['adc_x_limits'])
        grid on
        view([45, 45])
        nexttile(5)
        hold on
        plot3(ones(len(1:data['dac_data'](jse)['harmonic_number']) , 1)['']* sweep2(jse),
            data['dac_t_scale'](1:data['dac_data'](jse)['harmonic_number']), 
            data['dac_plot_data'](jse)['t_data'](1:data['dac_data'](jse)['harmonic_number']),
            'Color', cols[sweep_ind,:],
            'DisplayName', [(sweep1(jse)), ' ', num2str(sweep2(jse))])
        zlabel('DAC')
        ylabel(data['t_x_lab'])
        xlabel(sweep_names[2])
        title('Single turn')
        grid on
        view([45, 45])
        nexttile(6)
        hold on
        plot3(ones(len(data['dac_f_scale']) , 1)['']* sweep2(jse),
            data['dac_f_scale'],
            data['dac_plot_data'](jse)['f_data'],
            'Color', cols[sweep_ind,:],
            'DisplayName', [(sweep1(jse)), ' ', num2str(sweep2(jse))])
        zlabel(' ')
        ylabel(data['f_x_lab'])
        xlabel(sweep_names[2])
        ylim(data['dac_x_limits'])
        grid on
        view([45, 45])

    nexttile(3)
    scatter3(sweep1, sweep2, data['main_adc_f'], '*')
    xlabel(sweep_names[1])
    ylabel(sweep_names[2])
    zlabel({'ADC';data['f_x_lab']})
    nexttile(4)
    scatter3(sweep1, sweep2, data['main_adc_amp'], '*')
    xlabel(sweep_names[1])
    ylabel(sweep_names[2])
    zlabel('Signal')
    nexttile(7)
    scatter3(sweep1, sweep2, data['main_dac_f'], '*')
    xlabel(sweep_names[1])
    ylabel(sweep_names[2])
    zlabel(data['f_x_lab'])
    nexttile(8)
    scatter3(sweep1, sweep2, data['main_dac_amp'], '*')
    xlabel(sweep_names[1])
    ylabel(sweep_names[2])
    zlabel('Signal')

def plot_1D_scan(data, sweep_gains, graph_title):
    figure('Position', [20, 40, 1600, 800])
    t = tiledlayout(2, 4)
    title(t, graph_title)
    for jse  in range( 1, len(data['adc_data'])):
        nexttile(1)
        hold on
        plot(data['adc_t_scale'](1:data['adc_data'](jse)['harmonic_number']),
            data['adc_plot_data'](jse)['t_data'](1:data['adc_data'](jse)['harmonic_number']),
            'DisplayName', (sweep_gains(jse)))
        ylabel('ADC')
        xlabel(data['t_x_lab'])
        title('Single turn')
        lg = legend
        lg['Layout']['Tile'] = 'west'
        grid on
        nexttile(2)
        hold on
        plot(data['adc_f_scale'], data['adc_plot_data'](jse)['f_data'],
            'DisplayName', (sweep_gains(jse)))
        ylabel(' ')
        xlabel(data['f_x_lab'])
        xlim(data['adc_x_limits'])
        grid on
        nexttile(5)
        hold on
        plot(data['dac_t_scale'](1:data['dac_data'](jse)['harmonic_number']), 
            data['dac_plot_data'](jse)['t_data'](1:data['dac_data'](jse)['harmonic_number']),
            'DisplayName', (sweep_gains(jse)))
        ylabel('DAC')
        xlabel(data['t_x_lab'])
        title('Single turn')
        grid on
        nexttile(6)
        hold on
        plot(data['dac_f_scale'], data['dac_plot_data'](jse)['f_data'], 'DisplayName', (sweep_gains(jse)))
        ylabel(' ')
        xlabel(data['f_x_lab'])
        xlim(data['dac_x_limits'])
        grid on

    nexttile(3)
    plot(sweep_gains, data['main_adc_f'], '*')
    xlabel('Sweep gain')
    ylabel({'ADC';data['f_x_lab']})
    nexttile(4)
    plot(sweep_gains, data['main_adc_amp'], '*')
    xlabel('Sweep gain')
    ylabel('Signal')
    nexttile(7)
    plot(sweep_gains, data['main_dac_f'], '*')
    xlabel('Sweep gain')
    ylabel(data['f_x_lab'])
    nexttile(8)
    plot(sweep_gains, data['main_dac_amp'], '*')
    xlabel('Sweep gain')
    ylabel('Signal')

    return data_out 

def find_limits_around_peak(data, scale, peak_amp, peak_ind):
    begin_peak_ind = find(data[1:peak_ind] < (peak_amp ['']/ 1000), 1, 'last')
    if  begin_peak_ind:
        begin_peak = scale(begin_peak_ind)
    else:
        begin_peak = 0
        begin_peak_ind = 1

    end_peak = scale(peak_ind + (peak_ind - begin_peak_ind))
    if end_peak > begin_peak:
        x_limits = [begin_peak, end_peak]
    else:
        x_limits = [begin_peak, inf]


    return x_limits 

def get_data_from_mbf_memory(mbf_axis, chan, n_turns):
    mbf_tools
    [ _2 ,harmonic_number, pv_names,  _1 ] = system_config
    data_out['RF'] = lcaGet(pv_names['RF'])
    if strcmpi(mbf_axis, 's'):
        system_name = pv_names['hardware_names']['L']
        system_axis_name = pv_names['hardware_names']['s']
        mem_lock = 60; #180
    elif strcmpi(mbf_axis, 'x'):
        system_name = pv_names['hardware_names']['T']
        system_axis_name = pv_names['hardware_names']['x']
        mem_lock = 60; #30
    elif strcmpi(mbf_axis, 'y'):
        system_name = pv_names['hardware_names']['T']
        system_axis_name = pv_names['hardware_names']['y']
        mem_lock = 60; #30

    if chan == 0:
        target_location =  lcaGet([system_name pv_names['tails']['MEM']['channel0_target']])
    elif chan == 1:
        target_location =  lcaGet([system_name pv_names['tails']['MEM']['channel1_target']])

    target_location = target_location[1]
    if contains(target_location, 'DAC0'):
        trgt_extra = lcaGet([system_axis_name pv_names['tails']['dac']['dram_source']])
    elif contains(target_location, 'DAC1'):
        trgt_extra = lcaGet([system_axis_name pv_names['tails']['dac']['dram_source']])
    elif contains(target_location, 'ADC0'):
        trgt_extra = lcaGet([system_axis_name pv_names['tails']['adc']['dram_source']])
    elif contains(target_location, 'ADC1'):
        trgt_extra = lcaGet([system_axis_name pv_names['tails']['adc']['dram_source']])
    else:
        trgt_extra = ''

    trgt_extra = trgt_extra[1]
    data = mbf_read_mem(system_name, n_turns,'channel', chan, 'lock', mem_lock)
    # [data, data_freq,  _1 ] = mbf_read_det(system_name, 'axis', chan, 'lock', mem_lock)
    data_out['timedata'] = data
    data_out['n_turns'] = n_turns
    data_out['ax_label'] = mbf_axis
    data_out['datasource'] = [target_location, ' ', trgt_extra]
    data_out['harmonic_number'] = harmonic_number
def initialise_checkout(mbf_axis):
    # Set all signals to off for the testing['']
    [ _2 , harmonic_number, pv_names,  _1 ] = system_config
    system_axis = pv_names['hardware_names'][mbf_axis]
    bb = pv_names['tails']['Bunch_bank']['bank1']
    seq = pv_names['tails']['Sequencer']['seq1']
    nco1 = pv_names['tails']['NCO1']
    nco2 = pv_names['tails']['NCO2']
    adc = pv_names['tails']['adc']
    # Set all bank 1 entries to disabled['']
    lcaPut([system_axis bb['NCO1']['enablewf']], zeros(1, harmonic_number))
    lcaPut([system_axis bb['NCO2']['enablewf']], zeros(1, harmonic_number))
    lcaPut([system_axis bb['FIR']['enablewf']], zeros(1, harmonic_number))
    lcaPut([system_axis bb['SEQ']['enablewf']], zeros(1, harmonic_number))
    lcaPut([system_axis bb['PLL']['enablewf']], zeros(1, harmonic_number))
    # Turn off NCOs
    lcaPut([system_axis nco1['enable']], 'Off')
    lcaPut([system_axis nco2['enable']], 'Off')
    # Turn off Tune
    lcaPut([system_axis seq['enable']], 'Off')
    # Turn off Loopback
    lcaPut([system_axis adc['loopback']], 'Normal')
def mbf_checkout_setup(mbf_axis, varargin):
    # Sets the MBF system specified to have the desired signals passing
    # through the system['']
    #
    # Example: mbf_checkout_setup('x')
    mbf_p = inputParser
    mbf_p['StructExpand'] = false
    mbf_p['CaseSensitive'] = false
    axis_string = {'x', 'y', 's'}
    boolean_string = {'yes', 'no'}
    addRequired(mbf_p, 'mbf_axis', @(x) any(validatestring(x, axis_string)))
    addParameter(mbf_p, 'tune', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(mbf_p, 'nco1', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(mbf_p, 'nco2', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(mbf_p, 'loopback', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(mbf_p, 'fir', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(mbf_p, 'fir_gain', '-42dB')
    addParameter(mbf_p, 'nco1_gain', '-36dB')
    addParameter(mbf_p, 'nco2_gain', '-36dB')
    addParameter(mbf_p, 'tune_gain', '-42dB')
    # parse(p, mbf_axis)
    parse[mbf_p, mbf_axis, varargin[:]]
    [ _2 , harmonic_number, pv_names,  _1 ] = system_config
    system_axis = pv_names['hardware_names'][mbf_axis]
    nco1 = pv_names['tails']['NCO1']
    nco2 = pv_names['tails']['NCO2']
    bb1 = pv_names['tails']['Bunch_bank']['bank1']
    fir = pv_names['tails']['FIR']
    tune = pv_names['tails']['Sequencer']['seq1']
    adc = pv_names['tails']['adc']
    n_cycles = 1
    initialise_checkout(mbf_axis)
    if strcmp(mbf_p['Results']['nco1'], 'yes'):
        lcaPut([system_axis nco1['frequency']], n_cycles)
        lcaPut([system_axis nco1['gaindb']], mbf_p['Results']['nco1_gain'])
        lcaPut([system_axis nco1['enable']], 'On')
        lcaPut([system_axis bb1['NCO1']['enablewf']], ones(1, harmonic_number))

    if strcmp(mbf_p['Results']['nco2'], 'yes'):
        lcaPut([system_axis nco2['frequency']], n_cycles)
        lcaPut([system_axis nco2['gain_db']], mbf_p['Results']['nco2_gain'])
        lcaPut([system_axis nco2['enable']], 'On')
        lcaPut([system_axis bb1['NCO2']['enablewf']], ones(1, harmonic_number))

    if strcmp(mbf_p['Results']['fir'], 'yes'):
        lcaPut([system_axis fir['gain']], mbf_p['Results']['fir_gain'])
        lcaPut([system_axis bb1['FIR']['enablewf']], ones(1, harmonic_number))

    if strcmp(mbf_p['Results']['tune'], 'yes'):
        lcaPut([system_axis tune['gaindb']], mbf_p['Results']['tune_gain'])
        lcaPut([system_axis tune['enable']], 'On')
        lcaPut([system_axis bb1['SEQ']['enablewf']], ones(1, harmonic_number))

    if strcmp(mbf_p['Results']['loopback'], 'yes'):
        lcaPut([system_axis adc['loopback']], 'Loopback')

def mbf_digital_loopback_checkout(mbf_axis):
    # This runs a series of tests using various internal signal sources in
    # order to validate the expected system performance['']
    # THIS SHOULD BE RUN WITH NO OTHER SIGNALS (I['E'][''] BEAM)
    #
    # Example:  mbf_digital_loopback_checkout('x')
    [root_string,  _3 ,  _2 ,  _1 ] = system_config
    base_name = ['DL_checkout_', mbf_axis]
    exp_time = datevec(datetime("now"))
    # Number of turns to capture['']
    n_turns = 1000
    ## FIXME HARDCOADED PVS S axis is not fully implemented['']
    if strcmpi(mbf_axis, 'x'):
        lcaPut['SR23C-DI-TMBF-01:MEM:SEL0_S', 'ADC0']
        lcaPut['SR23C-DI-TMBF-01:MEM:SEL1_S', 'DAC0']
    elif strcmpi(mbf_axis, 'y'):
        lcaPut['SR23C-DI-TMBF-01:MEM:SEL0_S', 'ADC1']
        lcaPut['SR23C-DI-TMBF-01:MEM:SEL1_S', 'DAC1']
    elif strcmpi(mbf_axis, 's'):
        lcaPut['SR23C-DI-LMBF-01:MEM:SEL0_S', 'ADC0']
        lcaPut['SR23C-DI-LMBF-01:MEM:SEL1_S', 'DAC0']

    lcaPut['SR23C-DI-TMBF-01:TRG:MEM:DISARM_S['PROC']', 1]
    pause(1)
    # Default is everything off['']
    lb_status = {'_no_loopback', '_with_loopback'}
    lb_state = {'no', 'yes'}
    # Run the measurement set once with no loopback and once with loopback enabled['']
    for bwe  in range( 1, 2):
        # All sources off
        mbf_checkout_setup(mbf_axis, 'loopback', lb_state[bwe])
        pause(1)
        lcaPut['SR23C-DI-TMBF-01:MEM:CAPTURE_S['PROC']', 1]
        pause(1)
        data_out['time'] = exp_time
        data_out['base_name'] = [base_name '_noise' lb_status[bwe]]
        data_out['tune'] = 0
        data_out['nco1'] = 0
        data_out['nco2'] = 0
        data_out['fir'] = 0
        data_out['adc'] = get_data_from_mbf_memory(mbf_axis, 0, n_turns)
        data_out['dac'] = get_data_from_mbf_memory(mbf_axis, 1, n_turns)
        save_to_archive(root_string, data_out)
        # Tune on
        tune_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'}
        tune_labels = regexprep(tune_gains, '-', 'm')
        for emw  in range( 1, len(tune_gains)):
            mbf_checkout_setup(mbf_axis, 'loopback',lb_state[bwe], 'tune', 'yes',
                'tune_gain', tune_gains[emw])
            pause(1)
            lcaPut['SR23C-DI-TMBF-01:MEM:CAPTURE_S['PROC']', 1]
            pause(1)
            data_out['time'] = exp_time
            data_out['base_name'] = [base_name '_tune_gain_' tune_labels[emw] lb_status[bwe]]
            data_out['tune_gain'] = tune_gains[emw]
            data_out['loopback'] = lb_status[bwe]
            data_out['tune'] = 1
            data_out['nco1'] = 0
            data_out['nco2'] = 0
            data_out['fir'] = 0
            data_out['adc'] = get_data_from_mbf_memory(mbf_axis, 0, n_turns)
            data_out['dac'] = get_data_from_mbf_memory(mbf_axis, 1, n_turns)
            save_to_archive(root_string, data_out)

        # NCO1 on
        nco1_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'}
        nco1_labels = regexprep(nco1_gains, '-', 'm')
        for emw  in range( 1, len(nco1_gains)):
            mbf_checkout_setup(mbf_axis, 'loopback', lb_state[bwe], 'nco1', 'yes',
                'nco1_gain', nco1_gains[emw])
            pause(1)
            lcaPut['SR23C-DI-TMBF-01:MEM:CAPTURE_S['PROC']', 1]
            pause(1)
            data_out['time'] = exp_time
            data_out['base_name'] = [base_name '_nco1_gain_' nco1_labels[emw] lb_status[bwe]]
            data_out['nco1_gain'] = nco1_gains[emw]
            data_out['loopback'] = lb_status[bwe]
            data_out['tune'] = 0
            data_out['nco1'] = 1
            data_out['nco2'] = 0
            data_out['fir'] = 0
            data_out['adc'] = get_data_from_mbf_memory(mbf_axis, 0, n_turns)
            data_out['dac'] = get_data_from_mbf_memory(mbf_axis, 1, n_turns)
            save_to_archive(root_string, data_out)

        # NCO2 on
        nco2_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'}
        nco2_labels = regexprep(nco2_gains, '-', 'm')
        for emw  in range( 1, len(nco2_gains)):
            mbf_checkout_setup(mbf_axis, 'loopback', lb_state[bwe], 'nco2', 'yes',
                'nco2_gain', nco2_gains[emw])
            pause(1)
            lcaPut['SR23C-DI-TMBF-01:MEM:CAPTURE_S['PROC']', 1]
            pause(1)
            data_out['time'] = exp_time
            data_out['base_name'] = [base_name '_nco2_gain_' nco2_labels[emw] lb_status[bwe]]
            data_out['nco2_gain'] = nco2_gains[emw]
            data_out['loopback'] = lb_status[bwe]
            data_out['tune'] = 0
            data_out['nco1'] = 0
            data_out['nco2'] = 1
            data_out['fir'] = 0
            data_out['adc'] = get_data_from_mbf_memory(mbf_axis, 0, n_turns)
            data_out['dac'] = get_data_from_mbf_memory(mbf_axis, 1, n_turns)
            save_to_archive(root_string, data_out)

        # FIR on
        nco1_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'}
        fir_gains = {'-42dB', '-36dB', '-30dB', '-24dB', '-18dB', '-12dB'}
        fir_labels = regexprep(fir_gains, '-', 'm')
        nco1_labels = regexprep(nco1_gains, '-', 'm')
        for bes  in range( 1, len(nco1_gains)):
            for emw  in range( 1, len(fir_gains)):
                mbf_checkout_setup(mbf_axis, 'loopback', lb_state[bwe], 'fir', 'yes',
                    'fir_gain', fir_gains[emw],'nco1', 'yes', 'nco1_gain', nco1_gains[bes])
                pause(1)
                lcaPut['SR23C-DI-TMBF-01:MEM:CAPTURE_S['PROC']', 1]
                pause(1)
                data_out['time'] = exp_time
                data_out['base_name'] = [base_name '_fir_gain_' fir_labels[emw] 
                    '_nco1_gain_' nco1_labels[bes] lb_status[bwe]]
                data_out['nco1_gain'] = nco1_gains[bes]
                data_out['fir_gain'] = fir_gains[emw]
                data_out['loopback'] = lb_status[bwe]
                data_out['tune'] = 0
                data_out['nco1'] = 1
                data_out['nco2'] = 0
                data_out['fir'] = 1
                data_out['adc'] = get_data_from_mbf_memory(mbf_axis, 0, n_turns)
                data_out['dac'] = get_data_from_mbf_memory(mbf_axis, 1, n_turns)
                save_to_archive(root_string, data_out)



    initialise_checkout(mbf_axis)
def plot_data_from_mbf_checkout_file(data):
    # Generating the frequency scales
    n_bunches = data['n_turns'] ['']* data['harmonic_number']
    timescale = [1:n_bunches] ['']/ data['RF']; #sec
    timestep = timescale(2) - timescale(1)
    # f_scale = 1['']/timestep ['']* (-(n_bunches/2)+1:(n_bunches/2)) ['']/n_bunches; #Hz
    f_scale = 1['']/timestep ['']* [0:n_bunches-1] ['']/n_bunches; #Hz
    xf1 = abs(fft(data))
    figure('Position', [20, 40, 800, 800])
    t = tiledlayout(2, 1)
    title(t, {['MBF data ', mbf_axis,' axis '];
        ['Memory location:', target_location, ' ', trgt_extra]})
    nexttile
    plot(timescale/timestep, data, 'DisplayName', 'Raw data')
    ylabel(' ')
    xlabel('Ticks of 2ns')
    legend
    grid on
    # xlim([x_plt_axis(1) x_plt_axis(end)])
    nexttile
    plot(f_scale[1:n_bunches/2] * 1E-6, xf1[1:n_bunches/2], 'DisplayName', 'Raw frequency')
    ylabel(' ')
    xlabel('Frequency (MHz)')
    legend
    grid on
    # xlim([x_plt_axis(1) x_plt_axis(end)])
def plot_data_from_mbf_memory(data):
    # Generating the frequency scales
    n_bunches = data['n_turns'] ['']* data['harmonic_number']
    timescale = [1:n_bunches] ['']/ data['RF']; #sec
    timestep = timescale(2) - timescale(1)
    # f_scale = 1['']/timestep ['']* (-(n_bunches/2)+1:(n_bunches/2)) ['']/n_bunches; #Hz
    f_scale = 1['']/timestep ['']* [0:n_bunches-1] ['']/n_bunches; #Hz
    xf1 = abs(fft(data['timedata']))
    figure('Position', [20, 40, 800, 800])
    t = tiledlayout(2, 1)
    title(t, {['MBF data ', data['ax_label'],' axis '];
        ['Memory location:', data['datasource']]})
    nexttile
    plot(timescale/timestep, data['timedata'], 'DisplayName', 'Raw data')
    ylabel(' ')
    xlabel('Ticks of 2ns')
    legend
    grid on
    # xlim([x_plt_axis(1) x_plt_axis(end)])
    nexttile
    plot(f_scale[1:n_bunches/2] * 1E-6, xf1[1:n_bunches/2], 'DisplayName', 'Raw frequency')
    ylabel(' ')
    xlabel('Frequency (MHz)')
    legend
    grid on
    # xlim([x_plt_axis(1) x_plt_axis(end)])
