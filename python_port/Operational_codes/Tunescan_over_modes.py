def configure_tune_sweep(mbf_axis, drive_bunch, fb_on_off, d0flag, d1flag, d2flag, d3flag):
    # drive_bunch = 0:2:935;    # starts at 0
    # drive_bunch = 123
    # fb_on_off = 1;      # 0 => off, 1 => on
    [ _1 , harmonic_number, pv_names] = mbf_system_config
    head = pv_names['hardware_names'][mbf_axis]
    bank1 = pv_names['tails']['Bunch_bank']['']("bank1")
    detectors = pv_names['tails']['Detector']
    detect_bunch = drive_bunch
    # Only sweep selected bunch
    drive_wf = zeros(1, harmonic_number)
    drive_wf(drive_bunch + 1) = 1
    # chose which bunches to monitor the response
    detect_wf_1 = zeros(1,harmonic_number)
    detect_wf_1(sort(mod(detect_bunch + 0,harmonic_number)+1)) = 1
    detect_wf_2 = zeros(1,harmonic_number)
    detect_wf_2(sort(mod(detect_bunch + 1,harmonic_number)+1)) = 1
    detect_wf_3 = zeros(1,harmonic_number)
    detect_wf_3(sort(mod(detect_bunch + 2,harmonic_number)+1)) = 1
    # write to the TMBF on which bunches to perform the sweep
    set_variable([head, bank1['SEQ']['enablewf']], drive_wf)
    # Configure FIR enable (whether feedback is on or off)
    set_variable([head bank1['FIR']['enablewf']], fb_on_off * ones(1,harmonic_number))
    # Detector 0 grabs everything
    if d0flag:
        set_variable([head, detectors['']("det0")['bunch_selection']], ones(1,harmonic_number))
        set_variable([head, detectors['']("det0")['enable']], 'Enabled')
    else:
        set_variable([head, detectors['']("det0")['enable']], 'Disabled')

    # Detector 1 only observes active bunches
    if d1flag:
        set_variable([head, detectors['']("det1")['bunch_selection']], detect_wf_1)
        set_variable([head, detectors['']("det1")['enable']], 'Enabled')
    else:
        set_variable([head, detectors['']("det1")['enable']], 'Disabled')

    # Detector 2 only observes 1 bunch behind driven bunches
    if d2flag:
        set_variable([head, detectors['']("det2")['bunch_selection']], detect_wf_2)
        set_variable([head, detectors['']("det2")['enable']], 'Enabled')
    else:
        set_variable([head, detectors['']("det2")['enable']], 'Disabled')

    # Detector 3 only observes 2 bunches behind driven bunches
    if d3flag:
        set_variable([head, detectors['']("det3")['bunch_selection']], detect_wf_3)
        set_variable([head, detectors['']("det3")['enable']], 'Enabled')
    else:
        set_variable([head, detectors['']("det3")['enable']], 'Disabled')

    return 

def :
        mbf_tunescan_over_modes_archival_analysis(data_requested, varargin)
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
    #         dataset containing
    #         dr_passive (numeric matrix): Passive damping time['']
    #                                      (bunches vs datasets)
    #         dr_active (numeric matrix): Passive damping time['']
    #                                      (bunches vs datasets)
    #         error_passive (numeric matrix): Error of the fit for the passive
    #                                         damping rate['']
    #         error_active (numeric matrix): Error of the fit for the active
    #                                        damping rate['']
    #         times (numeric vector): Datetimes of the datasets['']
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis['']
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_tunescan_over_modes_archival_analysis(data_requested, 'average')
    p = inputParser
    validScalarPosNum = @(x) isnumeric(x) and isscalar(x) and (x > 0)
    addRequired(p, 'data_requested',@iscell)
    addParameter(p, 'analysis_type', 'collate', @ischar)
    addParameter(p, 'sweep_parameter', 'current', @ischar)
    addParameter(p, 'parameter_step', 0['1'], validScalarPosNum)
    addParameter(p, 'active_override', NaN)
    addParameter(p, 'passive_override', NaN)
    addParameter(p,'advanced_fitting', 0, @isnumeric)
    addParameter(p,'error_threshold', 0['1'], @isnumeric)
    addParameter(p, 'debug', 0)
    p['PartialMatching'] = false
    parse[p,data_requested, varargin[:]]
    # #condition the data in order to harmonise data changes made over time['']
    # for nd = len(data_requested):-1:1
    #     data_requested[nd] = growdamp_archive_data_conditioning(data_requested[nd])
    # end
    ck = 1
    for nd  in range( 1, len(data_requested)):
        if 'I_dcct5' in data_requested[nd]:
            data_requested[nd]['current'] = data_requested[nd]['I_dcct5']

        [data, data_state] = mbf_tunescan_over_modes_analysis(data_requested[nd],
            'active_override', p['Results']['active_override'],
            'passive_override', p['Results']['passive_override'],
            'advanced_fitting',p['Results']['advanced_fitting'], 
            'debug', p['Results']['debug'])
        if data_state == 0:
            continue

        times(ck) = datetime(data_requested[nd]['time'])
        if strcmp(p['Results']['analysis_type'], 'parameter_sweep'):
            param(ck) = data_requested[nd][''](p['Results']['sweep_parameter'])

        states = fieldnames(data)
        for st  in range( 1, len(states)):
            meass = fieldnames(data[states[st]])
            for ms  in range( 1, len(meass)):
                dataset[states[st]][meass[ms]][ck,:] = data[states[st]][meass[ms]]


        print('['']')
        ck = ck +1

    # # Removing datasets whose mean error is < error_threshold for the passive section['']
    # error_av_p = mean(dataset['passive']['error'],2,'omitnan')
    # wanted = find(abs(error_av_p) < p['Results']['error_threshold'])
    # states = fieldnames(dataset)
    #     for st = 1:len(states)
    #         meass = fieldnames(dataset[states[st]])
    #         for ms = 1:len(meass)
    #             dataset[states[st]][meass[ms]] = dataset[states[st]][meass[ms]][wanted,:]
    #         end #for
    #     end #for
    # times = times(wanted)
    # if strcmp(p['Results']['analysis_type'], 'parameter_sweep')
    #     param = param(wanted)
    # end #if
    experimental_setup['anal_type'] = p['Results']['analysis_type']
    if strcmp(p['Results']['analysis_type'], 'parameter_sweep'):
        experimental_setup['sweep_parameter'] = p['Results']['sweep_parameter']
        experimental_setup['parameter_step_size'] = p['Results']['parameter_step']
        if not dataset['passive']['damping_rate']:
            print('No data left[''] Try changing analysis settings['']')
            return
        else:
            [dataset, experimental_setup['param']] = 
                mbf_analysis_reorganise_for_parameter_sweep(dataset, param, 
                p['Results']['parameter_step'])

    elif strcmp(p['Results']['analysis_type'], 'average'):
        warning['Archive:Growdamp:setting','Ignoring the last two parameters as "average" is set']
        states = fieldnames(dataset)
        for st  in range( 1, len(states)):
            meass = fieldnames(dataset[states[st]])
            for ms  in range( 1, len(meass)):
                dataset[states[st]][meass[ms]] = mean(dataset[states[st]][meass[ms]],1, 'omitnan')



def mbf_tunescan_over_modes_archival_plotting(requested_data, dataset, times, experimental_setup):
    # Plots the data processed by mbf_growdamp_archival_analysis['']
    # Args:
    #       dataset (struct): containing
    #      dr_passive (numeric matrix): Passive damping rate['']
    #                                   (bunches vs datasets)
    #      dr_active (numeric matrix): Active damping rate['']
    #                                   (bunches vs datasets)
    #      error_passive (numeric matrix): Error of the fit for the passive
    #                                      damping rate['']
    #      error_active (numeric matrix): Error of the fit for the active
    #                                     damping rate['']
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #      plot_error_graphs (anything): if present the code will plot the results of the fit errors['']
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, dataset, error_active, times, setup, selections, extents)
    # Only do something if there is data to do something with['']
    if not times:
        return

    [ _3 , harmonic_number,  _2 ,  _1 ] = mbf_system_config
    x_plt_axis = [0:harmonic_number-1]
    # dataset =sort_data_in_stucture[dataset, [936:-1:469, 1:468], 2]
    dr_passive = dataset['passive']['damping_rate']
    dr_active = dataset['active']['damping_rate']
    error_passive = dataset['passive']['error']
    error_active = dataset['active']['error']
    this_year = year(datetime("now"))
    ranges_to_printlay = {'RF', 'time','current'}
    years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'}
    graph_text[1] = ['Analysis type: ', experimental_setup['anal_type']]
    graph_title = 'Damping rates for different modes'
    figure('Position',[50, 50, 1400, 800])
    annotation('textbox', [0 1-0['3'] 0['3'] 0['3']], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none')
    ax1 = axes('OuterPosition', [0['14'] 0['67'] 0['93'] 0['32']])
    hold on
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
    graph_title = {['Damping rates for different modes as a def of ', experimental_setup['sweep_parameter']];:
            ['Using a step size of ', (experimental_setup['parameter_step_size']), ' in the ', experimental_setup['axis'], ' axis']}
        graph_labels = cell(1, len(experimental_setup['param']))
        for hw  in range( 1, len(experimental_setup['param'])):
            graph_labels[hw]=(experimental_setup['param'](hw))

        dr_passive = squeeze(dr_passive)
        dr_active = squeeze(dr_active)
        plot(x_plt_axis, dr_passive, 'LineWidth', 2)
        legend(graph_labels)
    else:
        populate_graph(dr_passive, years_input, times, x_plt_axis)

    plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
    title(graph_title)
    xlabel('Mode')
    ylabel('Passive damping rates (1/turns)')
    legend show
    legend('Location','eastoutside')
    ymin = min(min(dr_passive,[],2))
    if ymin > 0:
        ymin = 0

    ymax = max(max(dr_passive,[],2))
    ymax = ymax + ymax /10
    ylim([ymin ymax])
    xlim([min(x_plt_axis), max(x_plt_axis)])
    grid on
    hold off
    ax2 = axes('OuterPosition', [0['14'] 0['34'] 0['8'] 0['32']])
    hold on
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        plot(x_plt_axis, dr_active, 'LineWidth', 2)
        #     legend(graph_labels)
    else:
        populate_graph(dr_active, years_input, times, x_plt_axis)

    legend('off')
    plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
    # title(graph_title)
    xlabel('Mode')
    ylabel('Active damping rates (1/turns)')
    ymin = min(min(dr_active,[],2))
    if ymin > 0:
        ymin = 0

    ymax = max(max(dr_active,[],2))
    ymax = ymax + ymax /10
    ylim([ymin ymax])
    xlim([min(x_plt_axis), max(x_plt_axis)])
    grid on
    hold off
    ax3 =axes('OuterPosition', [0['14'] 0 0['8'] 0['32']])
    hold on
    effectiveness = dr_active - dr_passive
    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        plot(x_plt_axis, effectiveness, 'LineWidth', 2)
        #     legend(graph_labels)
    else:
        populate_graph(effectiveness, years_input, times, x_plt_axis)

    legend('off')
    plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
    # title(graph_title)
    xlabel('Mode')
    ylabel('System effectiveness (1/turns)')
    ymin = min(min(effectiveness,[],2))
    if ymin > 0:
        ymin = 0

    ymax = max(max(effectiveness,[],2))
    ymax = ymax + ymax /10
    ylim([ymin ymax])
    xlim([min(x_plt_axis), max(x_plt_axis)])
    grid on
    hold off
    linkaxes([ax1, ax2, ax3],'x')
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
        legend('Location','eastoutside')

    if strcmp(experimental_setup['anal_type'], 'parameter_sweep'):
        figure('Position',[50, 50, 1400, 800])
        if strcmp(experimental_setup['sweep_parameter'], 'current'):
            axes('OuterPosition', [0 0 0['32'] 0['5']])
        else:
            axes('OuterPosition', [0 0 1 0['5']])

        hold on
        plot(experimental_setup['param'], dr_passive')
        xlabel(experimental_setup['sweep_parameter'])
        ylabel('Passive damping rates (1/turns)')
        grid on
        plot([experimental_setup['param'](1), experimental_setup['param'][end)], [0,0], 'r:', 'HandleVisibility', 'off']
        hold off
        if strcmp(experimental_setup['sweep_parameter'], 'current'):
            axes('OuterPosition', [0 0['5'] 0['32'] 0['5']])
        else:
            axes('OuterPosition', [0 0['5'] 1 0['5']])

        hold on
        plot(experimental_setup['param'], dr_active')
        xlabel(experimental_setup['sweep_parameter'])
        ylabel('Active damping rates (1/turns)')
        title(['Damping rates vs ', experimental_setup['sweep_parameter'], ' in the ', experimental_setup['axis'], ' axis'])
        grid on
        plot([experimental_setup['param'](1), experimental_setup['param'][end)], [0,0], 'r:', 'HandleVisibility', 'off']
        hold off
        if strcmp(experimental_setup['sweep_parameter'], 'current'):
            x1 = 0:1:300
            axes('OuterPosition', [0['33'] 0 0['32'] 0['5']])
            hold on
            for ks  in range( 1, len(dr_passive)):
                P = polyfit(experimental_setup['param']',dr_passive(:,ks),1)
                passive_mode_rate(ks) = P(1)
                P_start = find(x1 < min(experimental_setup['param']), 1, 'last')
                P_points = polyval(P,x1)
                # Find the first time after the lowest current that the extrapolation goes negative['']
                P_loc = find(sign(P_points[P_start:-1])==-1,1, 'first')
                if  P_loc:
                    plot(x1, P_points,'DisplayName', ['Mode ', (x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2)
                    plot(experimental_setup['param']', dr_passive(:,ks),'ko', 'HandleVisibility', 'off')


            xlabel(experimental_setup['sweep_parameter'])
            ylabel('Passive damping rates (1/turns)')
            title('Extrapolated data')
            #         legend('Location', 'eastoutside')
            legend('off')
            grid on
            plot([x1(1), x1[end)], [0,0], 'r:', 'HandleVisibility', 'off']
            hold off
            axes('OuterPosition', [0['67'] 0 0['32'] 0['5']])
            hold on
            plot(x_plt_axis, passive_mode_rate)
            plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
            xlabel('Modes')
            ylabel({'Passive damping' ;'rates change with current (1/turns/current)'})
            xlim([min(x_plt_axis), max(x_plt_axis)])
            hold off
            grid on
            axes('OuterPosition', [0['33'] 0['5'] 0['32'] 0['5']])
            hold on
            for ks  in range( 1, len(dr_active)):
                P = polyfit(experimental_setup['param']',dr_active(:,ks),1)
                active_mode_rate(ks) = P(1)
                P_start = find(x1 < min(experimental_setup['param']), 1, 'last')
                P_points = polyval(P,x1)
                P_loc = find(sign(P_points[P_start:-1])==-1,1, 'first')
                if  P_loc:
                    plot(x1, polyval(P,x1),'DisplayName', ['Mode ', (x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2)
                    plot(experimental_setup['param']', dr_active(:,ks),'ko', 'HandleVisibility', 'off')


            xlabel(experimental_setup['sweep_parameter'])
            ylabel('Active damping rates (1/turns)')
            title('Extrapolated data')
            #         legend('Location', 'eastoutside')
            legend('off')
            grid on
            plot([x1(1), x1[end)], [0,0], 'r:', 'HandleVisibility', 'off']
            hold off
            axes('OuterPosition', [0['67'] 0['5'] 0['32'] 0['5']])
            hold on
            plot(x_plt_axis, active_mode_rate)
            plot([x_plt_axis(1), x_plt_axis[end)], [0,0], 'r:', 'HandleVisibility', 'off']
            xlabel('Modes')
            ylabel({'Active damping'; 'rates change with current (1/turns/current)'})
            xlim([min(x_plt_axis), max(x_plt_axis)])
            hold off
            grid on


    if nargin == 9:
        figure
        ax3 = subplot(2,1,1)
        populate_graph(error_passive, years_input, times, x_plt_axis)
        title('Passive damping rate errors')
        xlabel('Mode')
        ylabel('Passive damping rate errors')
        ax4 = subplot(2,1,2)
        populate_graph(error_active, years_input, times, x_plt_axis)
        title('Active damping rate errors')
        xlabel('Mode')
        ylabel('Active damping rate errors')
        linkaxes([ax3,ax4],'x')

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
def mbf_tunescan_over_modes_archival_retrieval(ax, date_range, filter_conditions, :
        varargin)
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
    # Example: mbf_tunescan_over_modes_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    axis_string = {'x', 'y', 's'}
    boolean_string = {'yes', 'no'}
    analysis_type_string = {'collate', 'sweep'}
    validScalarPosNum = @(x) isnumeric(x) and isscalar(x) and (x > 0)
    addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)))
    addRequired(p, 'date_range')
    addRequired(p, 'filter_conditions')
    addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'analysis_type', 'collate', @(x) any(validatestring(x, analysis_type_string)))
    addParameter(p, 'sweep_parameter', 'current', @ischar)
    addParameter(p, 'parameter_step', 0['1'], validScalarPosNum)
    addParameter(p, 'active_override', NaN)
    addParameter(p, 'passive_override', NaN)
    addParameter(p,'advanced_fitting',0, @isnumeric)
    addParameter(p,'current_range', [2 305])
    addParameter(p, 'debug', 0)
    parse[p, ax, date_range, filter_conditions, varargin[:]]
    selection_name = ['tunescan_',ax,'_axis']
    requested_data = mbf_archival_dataset_retrieval(selection_name, date_range,
        'bypass_index' ,p['Results']['bypass_index'], 'metadata_only', p['Results']['metadata_only'])
    if len(requested_data) == 1:
        #     [dataset,  _2 ,  _1 ] = 
        #         mbf_tunescan_over_modes_archival_analysis(requested_data)
        mbf_tunescan_over_modes_plot_summary(requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(requested_data,
            filter_conditions)
        if not conditioned_data:
            print('No data meeting the requirements')
        else:
            if strcmp(p['Results']['analysis_type'], 'collate'):
                #             [dataset, times, setup] = 
                #                 mbf_tunescan_over_modes_archival_analysis(conditioned_data)
            elif strcmp(p['Results']['analysis_type'], 'sweep'):
                #             [dataset, times, setup] = 
                #                 mbf_tunescan_over_modes_archival_analysis(conditioned_data)

            #         setup['axis'] = ax
            #         mbf_tunescan_over_modes_archival_plotting(conditioned_data, dataset, times, setup)


    return dataset, times, experimental_setup

def mbf_tunescan_over_modes_capture(mbf_axis, pv_names):
# wrapper def to call tunescan, gather data on the environment:
    # and to save the resultant data['']
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s)['']
    #
    # example data = mbf_tunescan_over_modes_capture('x', pv_names)
    pv_head = pv_names['hardware_names'][mbf_axis]
    pv_head_mem = pv_names['hardware_names']['mem'][mbf_axis]
    triggers = pv_names['tails']['triggers']
    #Disarm, so that the current settings will be picked up upon arming['']
    set_variable([pv_head, triggers['SEQ']['disarm']], 1)
    ## Trigger the measurement
    if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's'):
        chan = 0
    elif strcmp(mbf_axis, 'y'):
        chan = 1

    if strcmpi(mbf_axis, 's'):
        mem_lock = 180
    else:
        mem_lock = 30

    #Arm
    set_variable([pv_head, triggers['SEQ']['arm']], 1)
    # Trigger
    set_variable([pv_head_mem, triggers['soft']], 1)
    # download the data
    measurement_time = ceil(get_variable['SR23C-DI-TMBF-01:Y:SEQ:TOTAL:DURATION:S'])+5
    pause(measurement_time)
    [tunescan['data'], tunescan['scale'], ~] = mbf_read_det(pv_head_mem,
        'axis', chan, 'lock', mem_lock)
    return tunescan 

def mbf_tunescan_over_modes_config(mbf_axis):
    # Contains the axis specific settings desired for the tunescan experiment['']
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are
    #                       requesting
    #
    # Example: settings = mbf_tunescan_config('x')
    if strcmpi(mbf_axis, 'x'):
        settings['axis_label'] = 'x'
        settings['axis_number'] = 1
        settings['ex_level'] = -18; # excitation level in dB['']
        settings['dwell'] = 200
        settings['det_gain'] = -24; # detector gain in dB['']
        settings['seq_gain'] = -42; # sequencer gain in dB['']
    elif strcmpi(mbf_axis, 'y'):
        settings['axis_label'] = 'y'
        settings['axis_number'] = 2
        settings['ex_level'] = -18; # excitation level in dB['']
        settings['dwell'] = 200
        settings['det_gain'] = -24; # detector gain in dB['']
        settings['seq_gain'] = -42; # sequencer gain in dB['']
    elif strcmpi(mbf_axis, 's'):
        settings['axis_label'] = 's'
        settings['axis_number'] = 3
        settings['ex_level'] = -18; # excitation level in dB['']
        settings['dwell'] = 200
        settings['det_gain'] = -24; # detector gain in dB['']
        settings['seq_gain'] = -42; # sequencer gain in dB['']

def mbf_tunescan_over_modes_plot_summary(tunescan):
    # Plots the effectiveness of correction across all modes['']
    #
    # Args:
    #       tunescan (structure): Captured data from a single experiment['']
    #
    # Example: mbf_tunescan_plotting(tunescan)
    # reshape the results
    fracttune = tunescan['scale'][1:tunescan['n_captures']]
    for n  in range( 1, 1#size(tunescan['data'],2)):
        result = reshape(abs(tunescan['data'](:,n)), 
            tunescan['n_captures'], tunescan['harmonic_number'])
        for js  in range( 1, size(result, 2)):
            [fit_curve,gof2] = tune_fit(fracttune, result(:,js))
            fit_width(js) = fit_curve['a']
            fit_height(js) = fit_curve['c'] * 2 / pi / fit_width(js)
            fit_centre(js) = fit_curve['n']
            fit_confidence(js) = gof2['sse']

        #find zoomed in area['']
        lower_tune_limit = mean(fit_centre) - max(fit_width) /2
        upper_tune_limit = mean(fit_centre) + max(fit_width) /2
        # plot the results
        f = figure('Position', [20, 40, 1600, 800])
        gp = tiledlayout(f, 4, 2,'TileSpacing','compact', 'Padding', 'tight')
        title(gp, {['MBF tunescan results ', tunescan['ax_label'],
            ' axis ', datestr(tunescan['time'])];
            ['Current: ', (round(tunescan['current'])), 'mA']})
        nexttile(gp, 1, [2 1])
        imagesc[1:tunescan['harmonic_number'], fracttune, result]
        xlabel('mode number')
        ylabel('fractional tune')
        yy  = colorbar
        ylabel(yy,'magnitude of response')
        nexttile(gp, 5, [2 1])
        imagesc[1:tunescan['harmonic_number'], fracttune, result]
        ylim([lower_tune_limit upper_tune_limit])
        xlabel('mode number')
        ylabel('fractional tune')
        yy  = colorbar
        ylabel(yy,'magnitude of response')
        nexttile(gp, 2)
        plot(1:tunescan['harmonic_number'], max(result, [], 1, "omitnan"),
            'DisplayName', 'Raw data', 'LineWidth', 2)
        hold on
        plot[1:tunescan['harmonic_number'], fit_height, 'm','DisplayName', 'Fitted data']
        xlabel('mode number')
        ylabel('magnitude of peak')
        legend
        grid on
        nexttile(gp, 4)
        plot[1:tunescan['harmonic_number'], fit_width, 'm', 'DisplayName', 'Fitted data']
        xlabel('mode number')
        ylabel('width of peak')
        grid on
        nexttile(gp, 6)
        plot[1:tunescan['harmonic_number'], fit_confidence, 'm', 'DisplayName', 'Fitted data']
        xlabel('mode number')
        ylabel('error of fit')
        grid on

def mbf_tunescan_over_modes_setup(tunescan):
    # Sets up the MBF system to be ready for a tunescan measurement['']
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s)['']
    #       tunescan (struct): Contains all the setup parameters['']
    #
    # example: mbf_tunescan_over_modes_setup(tunescan)
    mbf_tools
    if strcmp(tunescan['feedback_state'], 'on'):
        fb_on_off =1
    else:
        fb_on_off =0

    [ _1 , harmonic_number, pv_names] = mbf_system_config
    Detector = pv_names['tails']['Detector']
    Sequencer1 = pv_names['tails']['Sequencer']['seq1']
    Bunch_bank1 = pv_names['tails']['Bunch_bank']['bank1']
    # Generate the base PV name['']
    system_axis = pv_names['hardware_names'][''](tunescan['mbf_axis'])
    detect_bunch = tunescan['drive_bunches']
    # Only sweep selected bunch
    drive_wf = zeros(1, harmonic_number)
    drive_wf(tunescan['drive_bunches'] + 1) = 1
    # chose which bunches to monitor the response
    detect_wf_1 = zeros(1,harmonic_number)
    detect_wf_1(sort(mod(detect_bunch + 0, harmonic_number)+1)) = 1
    detect_wf_2 = zeros(1,harmonic_number)
    detect_wf_2(sort(mod(detect_bunch + 1, harmonic_number)+1)) = 1
    detect_wf_3 = zeros(1,harmonic_number)
    detect_wf_3(sort(mod(detect_bunch + 2, harmonic_number)+1)) = 1
    # write to the TMBF on which bunches to perform the sweep
    set_variable([system_axis Bunch_bank1['SEQ']['enablewf']], drive_wf)
    # Configure FIR enable (whether feedback is on or off)
    set_variable([system_axis Bunch_bank1['FIR']['enablewf']], fb_on_off * ones(1,harmonic_number))
    # Detector 0 grabs everything
    set_variable([system_axis Detector['det0']['bunch_selection']], ones(1,harmonic_number))
    set_variable([system_axis Detector['det0']['enable']], 'Enabled')
    # Detector 1 only observes active bunches
    set_variable([system_axis Detector['det1']['bunch_selection']], detect_wf_1)
    set_variable([system_axis Detector['det1']['enable']], 'Enabled')
    # Detector 2 only observes 1 bunch behind driven bunches
    set_variable([system_axis Detector['det2']['bunch_selection']], detect_wf_2)
    set_variable([system_axis Detector['det2']['enable']], 'Enabled')
    # Detector 3 only observes 2 bunches behind driven bunches
    set_variable([system_axis Detector['det3']['bunch_selection']], detect_wf_3)
    set_variable([system_axis Detector['det3']['enable']], 'Enabled')
    # arm the TMBF as one-shot rather than continuous
    set_variable([system_axis pv_names['tails']['triggers']['mode']],'One Shot')
    set_variable([system_axis pv_names['tails']['Sequencer']['reset']],1)
    # set the super-sequencer to have the correct number of modes
    set_variable([system_axis pv_names['tails']['Super_sequencer_reset']],1)
    set_variable([system_axis pv_names['tails']['Super_sequencer_count']],harmonic_number)
    # change the number of captures to speed things up (normally 4096)
    set_variable([system_axis Sequencer1['turns']],tunescan['n_captures'])
    # select the tune sweep frequency / mode
    set_variable([system_axis Sequencer1['start_frequency']],tunescan['start_mode'] + tunescan['start_frequency'])
    set_variable([system_axis Sequencer1['end_frequency']],  tunescan['start_mode'] + tunescan['end_frequency'])
def tune_sweep_expt(mbf_axis):
    # add the matlab paths for MBF tools
    mbf_tools
    [ _2 , harmonic_number, pv_names,  _1 ] = mbf_system_config
    mbf_vars = pv_names['tails']
    system_axis = pv_names['hardware_names'][mbf_axis]
    seq1 = pv_names['tails']['Sequencer']['seq1']
    # experiment parameters
    savefile    = appendtimestamp('tmbf_expt')
    ncap        = 1001; # 4096; # 1001 takes ~ 3 minutes
    startmode   = 0
    drive_bunch = 0:harmonic_number-1
    # drive_bunch = 100
    fb_on_off   = 1
    if strcmp(mbf_axis,'x'):
        start_freq = 0['139']
        end_freq = 0['239']
    else:
        start_freq = 0['227']
        end_freq = 0['327']

    ### configure the sweep
    configure_tune_sweep(mbf_axis , drive_bunch, fb_on_off, 1, 1, 1, 1)
    # arm the TMBF as one-shot rather than continuous
    set_variable([system_axis, mbf_vars['triggers']['mode']],'One Shot')
    set_variable([system_axis, pv_names['tails']['Sequencer']['reset']], 1)
    # set the super-sequencer to have the correct number of modes
    set_variable([system_axis, mbf_vars['Super_sequencer_reset']], 1)
    set_variable([system_axis, mbf_vars['Super_sequencer_count']],
        harmonic_number)
    # change the number of captures to speed things up (normally 4096)
    set_variable([system_axis seq1['count']], ncap)
    # select the tune sweep frequency / mode
    set_variable([system_axis seq1['start_frequency']], startmode + start_freq)
    set_variable([system_axis seq1['end_frequency']], startmode + end_freq)
    # start the multi-mode sweep
    set_variable([system_axis, mbf_vars['triggers']['SEQ']['arm']], 1)
    # download the data
    # (Eww['']  Convert axis string into 0 or 1[''])
    det_axis = find('xy' == mbf_axis) - 1
    [data, scale] = mbf_read_det(system_axis, 'axis', det_axis, 'lock', 1800 )
    # reset the sweep
    configure_tune_sweep[mbf_axis , 0:harmonic_number-1, 1, 1, 0, 0, 0]
    set_variable([system_axis, mbf_vars['triggers']['SEQ']['mode']],'Rearm')
    set_variable([system_axis, pv_names['tails']['Sequencer']['reset']],1)
    # reshape the results
    fracttune = scale[1:ncap]
    for n  in range( 1, size(data,2)):
        result = reshape(abs(data(:,n)), ncap, harmonic_number)
        # plot the results
        figure(n)
        imagesc[1:harmonic_number, fracttune, result]
        xlabel('mode number')
        ylabel('fractional tune')
        yy  = colorbar
        ylabel(yy,'magnitude of response')

    # get the stored beam conditions
    fill_pattern = get_variable(pv_names['bunch_pattern'])
    current = get_variable(pv_names['current'])
    # save the data
    save(savefile,'data','scale','mbf_axis','ncap','startmode','drive_bunch','fb_on_off','start_freq','end_freq','fill_pattern','current')
def tunescan_over_modes_all(mbf_axis, varargin):
# top level def to run the tunescan for all modes in the selected plane['']:
    # for archival investigations this allows filtering by machine state['']
    # but for capture this is not needed so it set to empty['']
    filter_conditions = []
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_axis_string = @(x) any(validatestring(x, {'x', 'y', 's'}))
    valid_boolean_string = @(x) any(validatestring(x, {'yes', 'no'}))
    addRequired(p, 'mbf_axis', valid_axis_string)
    addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'plotting', 'yes', valid_boolean_string )
    addParameter(p, 'additional_save_location', NaN)
    addParameter(p, 'n_captures', 1001); # 1001 takes ~ 3 minutes
    addParameter(p, 'start_mode', 0)
    addParameter[p, 'drive_bunches', 0:935]
    addParameter(p, 'feedback_state', 'on', valid_boolean_string )
    addParameter(p, 'start_frequency', 0)
    addParameter(p, 'end_frequency', 0['5'])
    parse[p, mbf_axis, varargin[:]]
    [root_string, harmonic_number, pv_names] = mbf_system_config
    pv_head = pv_names['hardware_names'][mbf_axis]
    if strcmp(p['Results']['auto_setup'], 'yes'):
        # Programatically press the tune only button on each system
        setup_operational_mode(mbf_axis, "TuneOnly")

    # getting general environment data
    tunescan = machine_environment
    # Add the extra data to the data structure['']
    tunescan['ax_label'] = mbf_axis
    tunescan['base_name'] = ['tunescan_' tunescan['ax_label'] '_axis']
    tunescan['harmonic_number'] = harmonic_number
    input_fieldnames = fieldnames(p['Results'])
    for ns  in range( 1,  len(input_fieldnames)):
        tunescan[input_fieldnames[ns]] = p['Results'][input_fieldnames[ns]]

    mbf_tunescan_over_modes_setup(tunescan)
    pause(2)
    captured_data = mbf_tunescan_over_modes_capture(mbf_axis, pv_names)
    # adding to output data structure['']
    data_fields = fieldnames(captured_data)
    for je  in range( 1, len(data_fields)):
        tunescan[data_fields[je]] = captured_data[data_fields[je]]

    # reset the sweep
    ####Is this section needed or does the TuneOnly script take care of things?
    configure_tune_sweep[mbf_axis , 0:harmonic_number -1, 1, 1, 0, 0, 0]
    set_variable([pv_head pv_names['tails']['triggers']['mode']],'Rearm')
    set_variable([pv_head pv_names['tails']['Sequencer']['reset']],1)
    #######
    if strcmp(p['Results']['auto_setup'], 'yes'):
        # Programatically press the tune only button on each system
        setup_operational_mode(mbf_axis, "TuneOnly")

    ## saving the data to a file
    save_to_archive(root_string, tunescan)
    if ~isnan(p['Results']['additional_save_location']):
        save(additional_save_location, tunescan)

    if strcmp(p['Results']['plotting'], 'yes'):
        mbf_tunescan_over_modes_archival_retrieval(mbf_axis, [tunescan['time'] tunescan['time']],
            filter_conditions)
