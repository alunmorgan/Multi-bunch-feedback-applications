    return 

def PPRE_aquisition(number_of_repeats):
    # captures all the required data for a single aquisition
    #
    # Example:  data_out = PPRE_aquisition
    [ _3 ,  _2 , pv_names,  _1 ] = system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    set_variable(pv_names['Hardware_trigger'], 1)
    while ~strcmp('Fit Forced',get_variable(pv_names['emittance']['status'])) :
            and ~strcmp('Successful',get_variable(pv_names['emittance']['status']))
        if strcmp('Image too faint',get_variable(pv_names['emittance']['status'])):
            error('Excitation gain likely too high!')

        pause(0['2'])

    data_out['mbf_data_x'] = get_variable([mbf_names['x'], mbf_vars['adc']['std']])
    data_out['mbf_data_y'] = get_variable([mbf_names['y'], mbf_vars['adc']['std']])
    data_out['pinhole_settings'] = pinhole_get_settings
    for nds  in range( 1, number_of_repeats):
        data_out['bunch_motion']['x'] = get_variable([mbf_names['x'], pv_names['tails']['adc']['std']])
        data_out['bunch_motion']['y'] = get_variable([mbf_names['y'], pv_names['tails']['adc']['std']])
        data_out['pinhole1_images'][nds] = pinhole_get_image(pv_names['pinhole1'])
        data_out['pinhole2_images'][nds] = pinhole_get_image(pv_names['pinhole2'])
        data_out['beam_sizes'][nds]['P1_sigx'] = get_variable(pv_names['beam_size']['pinhole1']['sigmax'])
        data_out['beam_sizes'][nds]['P1_sigy'] = get_variable(pv_names['beam_size']['pinhole1']['sigmay'])
        data_out['beam_sizes'][nds]['P2_sigx'] = get_variable(pv_names['beam_size']['pinhole2']['sigmax'])
        data_out['beam_sizes'][nds]['P2_sigy'] = get_variable(pv_names['beam_size']['pinhole2']['sigmay'])
        data_out['emittances'][nds]['coupling'] = get_variable(pv_names['coupling']['val'])
        data_out['emittances'][nds]['espread'] = get_variable(pv_names['energy_spread']['val'])
        data_out['emittances'][nds]['hemit'] = get_variable(pv_names['emittance']['x']['val'])
        data_out['emittances'][nds]['veimt'] = get_variable(pv_names['emittance']['y']['val'])
        data_out['emittances'][nds]['herror'] = get_variable(pv_names['emittance']['x']['error'])
        data_out['emittances'][nds]['verror'] = get_variable(pv_names['emittance']['y']['error'])
        print([(nds),'[''] '])
        pause(0['4']) # wait for next camera image['']

    print('\n')
    return data_out 

def mbf_PPRE_capture(mbf_axis, varargin):
    # Sets up the FLL with an additional excitation at a user defined gain and
    # frequency/tune['']
    #   Args:
    #       mbf_axis(str): 'x', or 'y'
    #       excitation_gain(vector of floats): the magnitude of the excitation in dB['']
    #       excitation_frequency(vector of floats): The tune value of the additional excitation
    #       harmonic(int): The tune harmonic to operate on['']
    #       BPM_data_capture_len(float): Amount of FA data to capture from
    #                                       the BPMs in seconds
    #       save_to_archive(str): 'yes' or 'no'
    #       additional_save_location(str): if specified the data will be saved
    #                                      to this location['']
    #   Returns:
    #       PPRE(struct): data captured from the MBF system and the cameras['']
    #       PPRE['scan'] contains a 3D cell array of scans: axis 1 is gain, axis 2 is
    #       frequency, axis 3 is harmonic['']
    #
    # Example: data =  mbf_PPRE_capture('y','excitation_gain', -30, 'save_to_archive', 'no')
    [root_string, harmonic_number, pv_names,  _1 ] = system_config
    # Define input and default values
    binary_string = {'yes', 'no'}
    validScalarNum = @(x) isnumeric(x) and isscalar(x)
    tunes = get_all_tunes
    leftSB = tunes['']([mbf_axis, '_tune'])['lower_sideband']
    default_excitation_frequency = leftSB
    default_excitation_gain = -60; #dB
    default_excitation_pattern = ones(harmonic_number,1)
    default_harmonic = 0
    default_repeat_datapoints = 20
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_string = @(x) ischar(x)
    addRequired(p, 'mbf_axis')
    addParameter(p, 'excitation_gain', default_excitation_gain)
    addParameter(p, 'excitation_frequency',default_excitation_frequency)
    addParameter(p, 'excitation_pattern', default_excitation_pattern)
    addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)))
    addParameter(p, 'additional_save_location', NaN, valid_string)
    addParameter(p, 'harmonic', default_harmonic)
    addParameter(p, 'repeat_datapoints', default_repeat_datapoints, validScalarNum)
    parse[p, mbf_axis, varargin[:]]
    # Set up MBF environment
    root_string = root_string[1]
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    ## Get environment data
    # getting general environment data['']
    PPRE = machine_environment
    # Add the axis label to the data structure['']
    PPRE['ax_label'] = mbf_axis
    # construct name and add it to the structure
    PPRE['base_name'] = ['PPRE_' PPRE['ax_label'] '_axis']
    # Excitation frequency and gain
    PPRE['excitation_gain'] = p['Results']['excitation_gain']
    PPRE['excitation_frequency'] = p['Results']['excitation_frequency']
    PPRE['harmonic'] = p['Results']['harmonic']
    # Tune sweeps (do we need all of these?)
    PPRE['tune_x_sweep'] = get_variable[[mbf_names['x'], ':TUNE:DMAGNITUDE']]
    PPRE['tune_x_sweep_model'] = get_variable[[mbf_names['x'], ':TUNE:MMAGNITUDE']]
    PPRE['tune_x_scale'] = get_variable[[mbf_names['x'], ':TUNE:SCALE']]
    PPRE['tune_y_sweep'] = get_variable[[mbf_names['y'], ':TUNE:DMAGNITUDE']]
    PPRE['tune_y_sweep_model'] = get_variable[[mbf_names['y'], ':TUNE:MMAGNITUDE']]
    PPRE['tune_y_scale'] = get_variable[[mbf_names['y'], ':TUNE:SCALE']]
    PPRE['tunes'] = get_all_tunes
    ## Set up MBF excitation
    PPRE['excitation_pattern'] = mbf_emittance_setup(mbf_axis, 
        'excitation', p['Results']['excitation_gain'](1),
        'excitation_frequency',p['Results']['excitation_frequency'](1),
        'excitation_pattern', p['Results']['excitation_pattern'], 
        'harmonic', p['Results']['harmonic'](1))
    ## Setup cameras
    set_variable['SR01C-DI-DCAM-05:IMAGEWIDTH', 1024]
    set_variable['SR01C-DI-DCAM-04:IMAGEWIDTH', 1024]
    set_variable['SR01C-DI-PINH-01:POS1', -2['5']]
    set_variable['SR01C-DI-PINH-02:POS1', -2['5']]
    ## Do measurement
    orig_gain = get_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']])
    orig_freq = get_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']])
    # gain scan
    for whd  in range( 1, len(p['Results']['excitation_gain'])):
        print('\n')
        # frequency scan
        for nwa  in range( 1, len(p['Results']['excitation_frequency'])):
            print('\n')
            # harmonic scan
            for kef  in range( 1, len(p['Results']['harmonic'])):
                print('['']')
                set_variable(pv_names['Hardware_trigger'], 0)
                set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']],p['Results']['excitation_gain'](whd))
                set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']], p['Results']['harmonic'](1) + p['Results']['excitation_frequency'](nwa))
                set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']], p['Results']['harmonic'](kef) + p['Results']['excitation_frequency'](1))
                pause(10)
                PPRE['scan']{whd, nwa, kef} = PPRE_aquisition(p['Results']['repeat_datapoints'])



    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']], orig_gain)
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']], orig_freq)
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['enable']], 0)
    ## saving the data to a file
    if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's'):
        #     only save if not on test system
        if strcmp(p['Results']['save_to_archive'], 'yes'):
            save_to_archive(root_string, PPRE)

        if ~isnan(p['Results']['additional_save_location']):
            save(additional_save_location, PPRE)


    if nargout == 1:
        varargout[1] = PPRE

def mbf_PPRE_plotting(PPRE_pp):
    # Plots the 1D scans of the pulse picking by resonant excitation['']
    if size(PPRE_pp['emittance_x'], 1) >1 and size(PPRE_pp['emittance_x'], 2) == 1 and size(PPRE_pp['emittance_x'], 3) == 1:
        scan_axis = PPRE_pp['excitation_gain_axis']
        scan_label = 'Gain'
    elif size(PPRE_pp['emittance_x'], 1) ==1 and size(PPRE_pp['emittance_x'], 2) > 1 and size(PPRE_pp['emittance_x'], 3) == 1:
        scan_axis = PPRE_pp['excitation_frequency_axis']
        scan_label = 'Frequency'
    elif size(PPRE_pp['emittance_x'], 1) == 1 and size(PPRE_pp['emittance_x'], 2) == 1 and size(PPRE_pp['emittance_x'], 3) > 1:
        scan_axis = PPRE_pp['harmonic_axis']
        scan_label = 'Harmonic'
    elif size(PPRE_pp['emittance_x'], 1) == 1 and size(PPRE_pp['emittance_x'], 2) == 1 and size(PPRE_pp['emittance_x'], 3) == 1:
        print('singular dataset[''] Nothing to plot['']')
        return
    else:
        print('Multidimensional data[''] Cant plot that yet!')
        return

    tiledlayout('flow')
    nexttile
    plot(scan_axis, PPRE_pp['emittance_x'])
    title('Horizontal emittance')
    xlabel(scan_label)
    nexttile
    plot(scan_axis, PPRE_pp['emittance_y'])
    title('Vertical emittance')
    xlabel(scan_label)
    nexttile
    plot(scan_axis, PPRE_pp['beam_sizes_P1'])
    title('Pinhole 1 vertical beamsize')
    xlabel(scan_label)
    nexttile
    plot(scan_axis, PPRE_pp['beam_sizes_P2'])
    title('Pinhole 2 vertical beamsize')
    xlabel(scan_label)
    nexttile
    plot(scan_axis, PPRE_pp['beam_sizes_P3'])
    title('Pinhole 3 vertical beamsize')
    xlabel(scan_label)
    return varargout 

def mbf_PPRE_postprocessing(PPRE_data):
    data_out['excitation_gain_axis'] = PPRE_data['excitation_gain']
    data_out['excitation_frequency_axis'] = PPRE_data['excitation_frequency']
    data_out['harmonic_axis'] = PPRE_data['harmonic']
    for gd  in range( 1, size(PPRE_data['scan'], 1)):
        for hum  in range( 1, size(PPRE_data['scan'], 2)):
            for snf  in range( 1, size(PPRE_data['scan'], 3)):
                data_out['emittance_x'](gd, hum, snf) = PPRE_data['scan']{gd, hum, snf}['emittances'][1]['hemit']
                data_out['emittance_y'](gd, hum, snf) = PPRE_data['scan']{gd, hum, snf}['emittances'][1]['veimt']
                data_out['beam_sizes_P1'](gd, hum, snf) = PPRE_data['scan']{gd, hum, snf}['beam_sizes'][1]['P1_sigy']
                data_out['beam_sizes_P2'](gd, hum, snf) = PPRE_data['scan']{gd, hum, snf}['beam_sizes'][1]['P2_sigy']
                #             data_out['beam_sizes_P1'](gd, hum, snf) = PPRE_data['scan']{gd, hum, snf}['beam_sizes'][1]['P3_sigy']



    return data_out 

def :
        mbf_ppre_archival_analysis(data_requested, varargin)
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets[''] Then plots the results['']
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed['']
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep['']
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged[''] (only needed if
    #                                    anal_type set to 'parameter sweep')
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides['']
    #
    # Returns:
    #         emittance_x (numeric matrix): Horizontal emittance['']
    #                                      (bunches vs datasets)
    #         emittance_y (numeric matrix): Vertical emittance['']
    #                                      (bunches vs datasets)
    #         beam_size_p1 (numeric matrix): Beam size at pinhole 1['']
    #         beam_size_p2 (numeric matrix): Beam size at pinhole 2['']
    #         times (numeric vector): Datetimes of the datasets['']
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis['']
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = growdamp_archival_analysis(data_requested, 'average')
    p = inputParser
    validScalarPosNum = @(x) isnumeric(x) and isscalar(x) and (x > 0)
    addRequired(p, 'data_requested',@iscell)
    addParameter(p, 'analysis_type', 'collate', @ischar)
    addParameter(p, 'sweep_parameter', 'excitation_gain', @ischar)
    addParameter(p, 'parameter_step', 0['1'], validScalarPosNum)
    addParameter(p, 'overrides', [NaN, NaN])
    addParameter(p, 'debug', 0)
    p['PartialMatching'] = false
    parse[p,data_requested, varargin[:]]
    anal_type = p['Results']['analysis_type']
    sweep_parameter = p['Results']['sweep_parameter']
    parameter_step_size = p['Results']['parameter_step']
    for nd  in range( len[data_requested):-1, 1]:
        data_out = mbf_PPRE_postprocessing(data_requested[nd])
        times(nd) = datetime(data_requested[nd]['time'])
        data_fields = fields(data_out)
        for fde  in range( 1, len(data_fields)):
            data_analysed[data_fields[fde]](nd,1:size(data_out[data_fields[fde]],1),1:size(data_out[data_fields[fde]],2), 
                1:size(data_out[data_fields[fde]],3)) = data_out[data_fields[fde]]

        if 'I_dcct5' in data_requested[nd]:
            data_requested[nd]['current'] = data_requested[nd]['I_dcct5']

        if strcmp(anal_type, 'parameter_sweep') and nargin >2:
            param(nd) = data_requested[nd][sweep_parameter]

        print('['']')

    print('\n')
    experimental_setup['anal_type'] = anal_type
    data_fields = fields(data_analysed)
    if strcmp(anal_type, 'parameter_sweep'):
        experimental_setup['sweep_parameter'] = sweep_parameter
        experimental_setup['parameter_step_size'] = parameter_step_size
        if not dr_passive:
            print('No data left[''] Try changing analysis settings['']')
            return
        else:
            for fde  in range( 1, len(data_fields)):
                [data_analysed[data_fields[fde]], experimental_setup['param']] = mbf_analysis_reorganise_for_parameter_sweep(data_analysed[data_fields[fde]], param, parameter_step_size)

            #         [emittance_y,  _1 ] = mbf_analysis_reorganise_for_parameter_sweep(emittance_y, param, parameter_step_size)
            #         [beam_size_p1,  _1 ] = mbf_analysis_reorganise_for_parameter_sweep(beam_size_p1, param, parameter_step_size)
            #         [beam_size_p2,  _1 ] = mbf_analysis_reorganise_for_parameter_sweep(beam_size_p2, param, parameter_step_size)

    elif strcmp(anal_type, 'average'):
        warning['Archive:Growdamp:setting','Ignoring the last two parameters as "average" is set']
        for fde  in range( 1, len(data_fields)):
            data_analysed[data_fields[fde]] = mean(data_analysed[data_fields[fde]],1, 'omitnan')

        #     emittance_y = mean(emittance_y,1, 'omitnan')
        #     beam_size_p1 = mean(beam_size_p1,1, 'omitnan')
        #     beam_size_p2 = mean(beam_size_p2,1, 'omitnan')

def mbf_ppre_archival_plotting(requested_data, data, times, experimental_setup):
    # Plots the data processed by growdamp_archival_analysis['']
    # Args:
    #      emittance_x (numeric matrix): Horizontal emittance['']
    #                                   (bunches vs datasets)
    #      emittance_y (numeric matrix): Vertical emittance['']
    #                                   (bunches vs datasets)
    #      beam_size_p1 (numeric matrix): Beam size at pinhole 1['']
    #      beam_size_p2 (numeric matrix): Beam size at pinhole 2['']
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #      plot_error_graphs (anything): if present the code will plot the results of the fit errors['']
    #
    # Example: mbf_ppre_archival_plotting(requested_data, emittance_x, emittance_y, beam_size_p1, beam_size_p2, times, experimental_setup)
    # Only do something if there is data to do something with['']
    if not times:
        return

    [ _3 , harmonic_number,  _2 ,  _1 ] = system_config
    x_plt_axis = [0:harmonic_number-1] - harmonic_number/2
    this_year = year(datetime("now"))
    ranges_to_printlay = {'RF', 'time','current'}
    years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'}
    graph_text[1] = ['Analysis type: ', experimental_setup['anal_type']]
    graph_title = 'Damping rates for different modes'
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
    graph_title = {['Emittance as a def of ', experimental_setup['sweep_parameter']];:
            ['Using a step size of ', (experimental_setup['parameter_step_size']), ' in the ', experimental_setup['axis'], ' axis']}
        graph_labels = cell(1, len(experimental_setup['param']))
        for hw  in range( 1, len(experimental_setup['param'])):
            graph_labels[hw]=(experimental_setup['param'](hw))


    figure('Position',[50, 50, 1400, 800])
    annotation('textbox', [0 1-0['3'] 0['3'] 0['3']], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none')
    emittance_x = squeeze(data['emittance_x'](:,1 ,1, 1)); #TEMP
    emittance_y = squeeze(data['emittance_y'](:,1 ,1, 1)); # FIXME
    ax1 = axes('OuterPosition', [0['12'] 0['5'] 0['95'] 0['5']])
    hold on
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        emittance_x = squeeze(emittance_x)
        emittance_y = squeeze(emittance_y)
        plot(x_plt_axis, data['emittance_x'], 'LineWidth', 2)
        legend(graph_labels)
    else:
        populate_graph(emittance_x, years_input, times, x_plt_axis)

    plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
    title(graph_title)
    xlabel('Mode')
    ylabel('Horizontal emittance')
    legend show
    ymin = min(min(emittance_x,[],2))
    if ymin > 0:
        ymin = 0

    ymax = max(max(emittance_x,[],2))
    ymax = ymax + ymax /10
    ylim([ymin ymax])
    grid on
    hold off
    ax2 =axes('OuterPosition', [0['12'] 0 0['95'] 0['5']])
    hold on
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        plot(x_plt_axis, emittance_y, 'LineWidth', 2)
        legend(graph_labels)
    else:
        populate_graph(emittance_y, years_input, times, x_plt_axis)

    plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
    # title(graph_title)
    xlabel('Mode')
    ylabel('Vertical emittance')
    ymin = min(min(emittance_y,[],2))
    if ymin > 0:
        ymin = 0

    ymax = max(max(emittance_y,[],2))
    ymax = ymax + ymax /10
    ylim([ymin ymax])
    grid on
    hold off
    ck = 1
    for hrd  in range( 1, len(ranges_to_printlay)):
        if strcmp(ranges_to_printlay[hrd], 'time'):
            continue
        else:
            axes('OuterPosition', [0['01'] ck/3 0['2'] 0['3']])
            xlabel('Time')
            title(ranges_to_printlay[hrd])
            data_temp = NaN(len(times),1)
            for hse  in range( 1, len(times)):
                data_temp(hse) = requested_data[hse][ranges_to_printlay[hrd]]

            plot[times, data_temp, 'o:']
            datetick
            ylabel(ranges_to_printlay[hrd])

            ck = ck +1


    axfp = axes('OuterPosition', [0['01'] 0 0['2'] 0['3']])
    hold on
    for hkw  in range( 1, len(requested_data)):
        plot[1:harmonic_number, requested_data[hkw]['fill_pattern'], 'b']

    ylim([0 inf])
    xlim([1 harmonic_number])
    set(axfp, 'XTick', [])
    title('Fill pattern variation')
    ylabel('Charge (nC)')
    # add labels if it is a parameter sweep['']
    if nargin == 4 and strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        for tb  in range( len[experimental_setup['param']):-1, 1]:
            labels[tb] = (experimental_setup['param'](tb))

        legend(labels)

    linkaxes([ax1,ax2],'x')
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        figure('Position',[50, 50, 1400, 800])
        if strcmp(experimental_setup['sweep_parameter'], 'current'):
            axes('OuterPosition', [0 0 0['48'] 0['5']])
        else:
            axes('OuterPosition', [0 0 1 0['5']])

        hold on
        plot(experimental_setup['param'], data['emittance_x']')
        xlabel(experimental_setup['sweep_parameter'])
        ylabel('Passive damping rates (1/turns)')
        grid on
        plot([experimental_setup['param'](1), experimental_setup['param'][end)], [0,0], 'r:', 'HandleVisibility', 'off']
        hold off
        if strcmp(experimental_setup['sweep_parameter'], 'current'):
            axes('OuterPosition', [0 0['5'] 0['48'] 0['5']])
        else:
            axes('OuterPosition', [0 0['5'] 1 0['5']])

        hold on
        plot(experimental_setup['param'], data['emittance_y']')
        xlabel(experimental_setup['sweep_parameter'])
        ylabel('Active damping rates (1/turns)')
        title(['Damping rates vs ', experimental_setup['sweep_parameter'], ' in the ', experimental_setup['axis'], ' axis'])
        grid on
        plot([experimental_setup['param'](1), experimental_setup['param'][end)], [0,0], 'r:', 'HandleVisibility', 'off']
        hold off
        #     if strcmp(experimental_setup['sweep_parameter'], 'current')
        #         x1 = 0:1:300
        #         axes('OuterPosition', [0['52'] 0 0['48'] 0['5']])
        #         hold on
        #         for ks = 1:len(data['emittance_x'])
        #             P = polyfit(experimental_setup['param']',data['emittance_x'](:,ks),1)
        #             P_start = find(x1 < min(experimental_setup['param']), 1, 'last')
        #             P_points = polyval(P,x1)
        #             # Find the first time after the lowest current that the extrapolation goes negative['']
        #             P_loc = find(sign(P_points[P_start:-1])==-1,1, 'first')
        #             if  P_loc
        #             plot(x1, P_points,'DisplayName', ['Mode ', (x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2)
        #             plot(experimental_setup['param']', data['emittance_x'](:,ks),'ko', 'HandleVisibility', 'off')
        #             end #if
        #         end #for
        #         xlabel(experimental_setup['sweep_parameter'])
        #         ylabel('Passive damping rates (1/turns)')
        #         title('Extrapolated data')
        #         legend('Location', 'eastoutside')
        #         grid on
        #         plot([x1(1), x1[end)], [0,0], 'r:', 'HandleVisibility', 'off']
        #         hold off
        #
        #         axes('OuterPosition', [0['52'] 0['5'] 0['48'] 0['5']])
        #         hold on
        #         for ks = 1:len(data['emittance_y'])
        #             P = polyfit(experimental_setup['param']',data['emittance_y'](:,ks),1)
        #             P_start = find(x1 < min(experimental_setup['param']), 1, 'last')
        #              P_points = polyval(P,x1)
        #             P_loc = find(sign(P_points[P_start:-1])==-1,1, 'first')
        #             if  P_loc
        #             plot(x1, polyval(P,x1),'DisplayName', ['Mode ', (x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2)
        #             plot(experimental_setup['param']', data['emittance_y'](:,ks),'ko', 'HandleVisibility', 'off')
        #             end #if
        #         end #for
        #         xlabel(experimental_setup['sweep_parameter'])
        #         ylabel('Active damping rates (1/turns)')
        #         title('Extrapolated data')
        #         legend('Location', 'eastoutside')
        #         grid on
        #         plot([x1(1), x1[end)], [0,0], 'r:', 'HandleVisibility', 'off']
        #         hold off
        #     end #if

def populate_graph(input_data, years_input, times, x_plt_axis):
    if not input_data:
        return

    hold on
    y_max = max(max(input_data))
    y_min = min(min(input_data))
    for esr  in range( size[years_input,1):-1, 1]:
        years(esr) = years_input[esr][1]
        states(esr) = 0
        cols[esr] = years_input[esr][2]

    sample_year_temp = datevec(times)
    year_list = sample_year_temp(:,1)
    if len(unique(year_list)) < 2:
        for ner  in range( 1, size(input_data, 1)):
            sample_time = datevec(times(ner))
            sample_time = datestr(sample_time)
            plot(x_plt_axis, input_data[ner,:], 'DisplayName', sample_time, 'LineWidth', 2)

    else:
        for ner  in range( 1, size(input_data, 1)):
            years_ind = find(year_list(ner)== years)
            if states(years_ind) == 0:
                plot(x_plt_axis, input_data[ner,:], cols[years_ind], 'DisplayName', (year_list(ner)), 'LineWidth', 2)
                states(years_ind) = 1
            else:
                plot(x_plt_axis, input_data[ner,:], cols[years_ind], 'HandleVisibility', 'off', 'LineWidth', 2)



    xlim([x_plt_axis(1) x_plt_axis(end)])
    ylim([y_min y_max])
    legend('show')
    return data_analysed, times, experimental_setup

def mbf_ppre_archival_retrieval(ax, date_range, varargin):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax)['']
    # also filters out datasets with machine settings outside the specified
    # acceptable range['']
    #
    # Args:
    #       ax (str): The number of the axis (x, y, s)
    #       date_range (pair of datetime instances): The range of time to extract['']
    #       bypass_index (str) : 'no' for use the pregnerated index (much faster)
    #                            'yes' for work things out from the file metatdata['']
    #                            the default is 'no'['']
    #       metadata_only(str): 'no' return all data
    #                            'yes' remove the sample data from the output structure['']
    #                            the default is 'no'['']
    #       analysis_type(str): determines the type of analysis to run 'collate' or
    #                           'sweep', the default is 'collate'['']
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep['']
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged[''] (only needed if
    #                                    anal_type set to 'parameter sweep')
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides['']
    #
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures['']
    #
    # Example: mbf_ppre_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    axis_string = {'x', 'y', 's'}
    boolean_string = {'yes', 'no'}
    validScalarPosNum = @(x) isnumeric(x) and isscalar(x) and (x > 0)
    default_sweep_parameter = 'current'
    default_parameter_step_size = 0['1']
    defaultOverrides = [NaN, NaN]
    defaultAnalysisSetting = 0
    defaultCurrentRange = [2, 150]
    addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)))
    addRequired(p, 'date_range')
    addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'analysis_type', 'collate', @ischar)
    addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar)
    addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum)
    addParameter(p, 'overrides', defaultOverrides)
    addParameter(p,'advanced_fitting',defaultAnalysisSetting, @isnumeric)
    addParameter(p,'current_range',defaultCurrentRange)
    addParameter(p, 'debug', 0)
    parse[p, ax, date_range, varargin[:]]
    if strcmpi(ax, 'x'):
        filter_name = 'PPRE_x_axis'
    elif  strcmpi(ax, 'y'):
        filter_name = 'PPRE_y_axis'
    elif strcmpi(ax, 's'):
        filter_name = 'PPRE_s_axis'
    else:
        error('MBF:Archive:InputError', 'archival_dataset_retrieval: No valid axis given (should be x, y or s)')

    requested_data = archival_dataset_retrieval(filter_name, date_range,
        'bypass_index' ,p['Results']['bypass_index'], 'metadata_only', p['Results']['metadata_only'])
    # Only keeping datasets that satify the requested machine conditions['']
    conditioned_data = archival_conditional_filtering(requested_data, 'current_range', p['Results']['current_range'])
    if not conditioned_data:
        print('No data meeting the requirements')
    else:
        if strcmp(p['Results']['analysis_type'], 'collate'):
            [data, times, setup] = 
                mbf_ppre_archival_analysis(conditioned_data, 'analysis_type','collate',
                'overrides', p['Results']['overrides'], 
                'debug', p['Results']['debug'])
        elif strcmp(p['Results']['analysis_type'], 'sweep'):
            [data, times, setup] = 
                mbf_ppre_archival_analysis(conditioned_data, 'analysis_type','parameter_sweep', 
                'sweep_parameter',p['Results']['sweep_parameter'],
                'parameter_step', p['Results']['parameter_step'],
                'overrides', p['Results']['overrides'], 
                'debug', p['Results']['debug'])
        else:
            error['MBF:Archive:InputError', 'Please select collate or sweep as the analysis type']

        setup['axis'] = ax
        mbf_ppre_archival_plotting(conditioned_data, data, times, setup)
