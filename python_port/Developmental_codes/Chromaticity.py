def chromaticity_all(mbf_axis, varargin):
# Top level def to run the chromaticity for selected plane['']:
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are requesting
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes['']
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes['']
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive['']
    #       n_repeats(int): How many times to repeat each measurement point['']
    #
    # Example  chromaticity_all('x')
    [root_string, harmonic_number, pv_names] = mbf_system_config
    pv_head = pv_names['hardware_names'][mbf_axis]
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    axis_string = {'x', 'y', 's'}
    boolean_string = {'yes', 'no'}
    valid_positive_number = @(x) isnumeric(x) and isscalar(x) and (x >= 0)
    addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)))
    addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'additional_save_location', NaN)
    addParameter(p, 'n_repeats', 10, valid_positive_number)
    addParameter(p, 'n_trys', 5, valid_positive_number)
    addParameter(p, 'with_measchro', 'no', @(x) any(validatestring(x, boolean_string)))
    parse[p, mbf_axis, varargin[:]]
    # getting general environment data
    chromaticity = machine_environment
    # Add the extra data to the data structure['']
    chromaticity['ax_label'] = mbf_axis
    chromaticity['base_name'] = ['chromaticity_', mbf_axis, '_axis']
    chromaticity['harmonic_number'] = harmonic_number
    input_fields = fieldnames(p['Results'])
    for jltf  in range( 1, len(input_fields)):
        chromaticity[input_fields[jltf]] = p['Results'][input_fields[jltf]]

    if strcmp(p['Results']['auto_setup'], 'yes'):
        # Programatically press the tune only button on each system['']
        setup_operational_mode(mbf_axis, "TuneOnly")

    chromaticity['fir_gain'] = get_variable[[pv_head, ':FIR:GAIN_S']]
    chromaticity['mbf_state'] = get_operational_mode(mbf_axis)
    # Capturing data['']
    captured_data = mbf_chromaticity_capture(chromaticity, pv_names)
    # adding to output data structure['']
    data_fields = fieldnames(captured_data)
    for je  in range( 1, len(data_fields)):
        chromaticity[data_fields[je]] = captured_data[data_fields[je]]

    if strcmp(p['Results']['auto_setup'], 'yes'):
        setup_operational_mode(mbf_axis, "Feedback")
        # Setting the FIR gain to its original value['']
        set_variable[[pv_head, ':FIR:GAIN_S'], chromaticity['fir_gain']]
    else:
        reestablish_tune_measurement(mbf_axis)

    print(['Chromaticity for ', mbf_axis, ' is ', (chromaticity['mean']),
        ' with an uncertainty of ', (chromaticity['std'])])
    if strcmp(p['Results']['with_measchro'], 'yes'):
        [chro_temp,  _1 ] = measchro
        if strcmpi(mbf_axis, 'x'):
            chromaticity['measchro'] = chro_temp(1)
            print('measchro returns ', chromaticity['measchro'])
        elif strcmpi(mbf_axis, 'y'):
            chromaticity['measchro'] = chro_temp(2)
            print('measchro returns ', chromaticity['measchro'])
        else:
            print('measchro only returns data for x and y')


    ## saving the data to a file
    save_to_archive(root_string, chromaticity)
    if ~isnan(p['Results']['additional_save_location']):
        save(additional_save_location, chromaticity)

def chromaticity_aquire_live(save_loc):
    # Measures the live tune waveform for both x and y axis
    # and calculates the chromaticity from that['']
    # Saves data to files at location save_loc every 6 hours['']
    #
    # Example chromaticity_aquire_live(save_loc)
    if nargin == 0:
        error['ChromaticityAquireLive:OutputError', 'Please specify a save location']
    elif nargin > 1:
        error['ChromaticityAquireLive:InputError', 'Wrong number of input arguments[''] Only the save location is needed']

    n_samples =60
    n_per_file = 18000; # about 6 hours of data capture
    while 1==1:
        start_time  = datetime("now")
        chro_x_mean = nan(n_per_file,1)
        chro_x_std = nan(n_per_file,1)
        chro_y_mean = nan(n_per_file,1)
        chro_y_std = nan(n_per_file,1)
        chro_time =  nan(n_per_file,1)
        for nd  in range( 1, n_per_file):
            time_temp = NaN[1:n_samples,1]
            chro_x_temp = NaN[1:n_samples,1]
            chro_y_temp = NaN[1:n_samples,1]
            for kw  in range( 1, n_samples):
                time_temp(kw) = datetime("now")
                chro_x_temp(kw) = chromaticity_from_sidebands('x')
                chro_y_temp(kw) = chromaticity_from_sidebands('y')
                pause(1['2']) # make sure there is new data['']
                # maybe better to use monitors['']


            chro_x_mean(nd) = nonanmean(chro_x_temp)
            chro_x_std(nd) = nonanstd(chro_x_temp)
            chro_y_mean(nd) = nonanmean(chro_y_temp)
            chro_y_std(nd) = nonanstd(chro_y_temp)
            chro_time(nd) = time_temp(1) + (time_temp(end) - time_temp(1)) / 2


        save(fullfile(save_loc, ['chromaticity_', start_time]), "chro_time",
            "chro_y_std", "chro_y_mean","chro_x_std", "chro_x_mean", "start_time")


    return 

def chromaticity_from_sidebands(mbf_axis, n_trys, pv_names):
    # calculates the chromaticity from the sideband ratios
    # and the emittance measurement['']
    #
    # Args:
    #       mbf_axis(str): 'x' or 'y'['']
    #       n_trys(int): Max number of retrys to get complete dataset['']
    #
    # Example: chro=chromaticity_from_sidebands('x')
    MBF_PV = pv_names['hardware_names'][mbf_axis]
    tune_pv = pv_names['tails']['tune']
    for hs  in range( 1, n_trys):
        vars = get_variable({[MBF_PV, tune_pv['centre_width']]; [MBF_PV, tune_pv['left_width']];
            [MBF_PV, tune_pv['right_width']];[MBF_PV, tune_pv['centre_height']];
            [MBF_PV, tune_pv['left_height']];[MBF_PV, tune_pv['right_height']];
            [MBF_PV, tune_pv['sync_tune']]; pv_names['energy_spread']['val']})
        if ~any(isnan(vars)):
            break

        pause(1['2'])

    if any(isnan(vars)):
        chro = NaN
        warning('Chromaticity:Missing_data',
            ['Could not retrive a complete dataset after ',
            (n_trys), ' trys['']'])
        return

    centre_width = vars(1)
    left_width = vars(2)
    right_width = vars(3)
    centre_height = vars(4)
    left_height = vars(5)
    right_height = vars(6)
    Q_S = vars(7)
    sigma_E = vars(8)
    # Generate a Lorentz curve using the width and scale the height to match the
    # measurement[''] The area will scale with the hight and before scaling is 1 by
    # definition['']
    centre_area = centre_height ['']/ max((1/pi) ['']* ((0['5'] ['']* centre_width) ['']/
        ([-1:centre_width/10:1]['']^2 + (0['5'] ['']* centre_width)['']^2)))
    left_area = left_height ['']/ max((1/pi) ['']* ((0['5'] ['']* left_width) ['']/
        ([-1:left_width/10:1]['']^2 + (0['5'] ['']* left_width)['']^2)))
    right_area = right_height ['']/ max((1/pi) ['']* ((0['5'] ['']* right_width) ['']/
        ([-1:right_width/10:1]['']^2 + (0['5'] ['']* right_width)['']^2)))
    R = (sqrt(left_area) + sqrt(right_area)) / sqrt(centre_area)
    #Based on work by GR using the following paper
    # https://proceedings['jacow']['org']/IPAC2014/papers/thpro076['pdf']
    if R < ['25']:
        # If the combined area of the sidebands is less than 25# of the area of
        # the main peak, do this['']
        s=sqrt(R)
    else:
        s = 9['2893']*R^9 - 
            84['038']*R^8 + 
            326['95']*R^7 - 
            714['77']*R^6 + 
            963['33']*R^5 - 
            826['25']*R^4 + 
            449['24']*R^3 - 
            149['08']*R^2 + 
            28['222']*R - 
            1['8186']

    chro = s * Q_S / sigma_E
def chromaticity_plot_live(n_repeats, n_samples, n_trys):
    # This only gives valid results if the MBF feedback is off,
    # as it would otherwise supress the central peak
    #
    # This takes the ratio of the sidebamd areas vs the central peak area and along
    # with measurements of energy spread and synchrotron tune fit to a theoretical
    # model to return the chromaticity value['']
    #
    # Args:
    #       n_repeats(int): Number of repeat sets['']
    #       n_samples(int): Number of repeat measurements in each set['']
    #       n_trys(int): Max number of retrys to get complete dataset['']
    #
    # Outputs a graph of n_repeat points for each axis vs time of measurement['']
    #
    # Example: chromaticity_plot_live(100, 10, 5)
    chro_time = NaT(n_repeats,1)
    chro_x_mean = NaN(n_repeats,1)
    chro_x_std = NaN(n_repeats,1)
    chro_y_mean = NaN(n_repeats,1)
    chro_y_std = NaN(n_repeats,1)
    chro_x_temp = NaN(n_samples,1)
    chro_y_temp = NaN(n_samples,1)
    figure
    for nd  in range( 1, n_repeats):
        chro_time(nd) = datetime('now')
        for kw  in range( 1, n_samples):
            chro_x_temp(kw) = chromaticity_from_sidebands('x', n_trys)
            chro_y_temp(kw) = chromaticity_from_sidebands('y', n_trys)
            pause(1['2']) # make sure there is new data['']

        chro_x_mean(nd) = mean(chro_x_temp, 'omitnan')
        chro_x_std(nd) = std(chro_x_temp, 0, 'omitnan')
        chro_y_mean(nd) = mean(chro_y_temp, 'omitnan')
        chro_y_std(nd) = std(chro_y_temp, 0, 'omitnan')
        grid on
        errorbar(chro_time, chro_x_mean, chro_x_std ,'b*')
        hold on
        errorbar(chro_time, chro_y_mean, chro_y_std,'r^')
        hold off

def chromaticity_plotting_overlay(sb_chro_loc, mc_chro_loc):
    # Compares and plots the data from the measchro routine and the new
    # chromaticity measurements from sidebands['']
    #
    # Example: chromaticity_plotting_overlay('/chromaticity_from_sidebands', fullfile('ops-physics', 'chrodata'))
    sb_chro_files = dir_list_gen(sb_chro_loc, 'mat', 1)
    sb_chro =load(sb_chro_files[1])
    for se  in range( 2, len(sb_chro_files)):
        temp = load(sb_chro_files[se])
        sb_chro['chro_time'] = cat(2, sb_chro['chro_time'], temp['chro_time'])
        sb_chro['chro_x_mean'] = cat(2, sb_chro['chro_x_mean'], temp['chro_x_mean'])
        sb_chro['chro_y_mean'] = cat(2, sb_chro['chro_y_mean'], temp['chro_y_mean'])
        sb_chro['chro_x_std'] = cat(2, sb_chro['chro_x_std'], temp['chro_x_std'])
        sb_chro['chro_y_std'] = cat(2, sb_chro['chro_y_std'], temp['chro_y_std'])

    # Ensuring that the data is acending time order['']
    [ _1 ,I] = sort(sb_chro['chro_time'])
    sb_chro['chro_x_time'] = sb_chro['chro_time'](I)
    sb_chro['chro_y_time'] = sb_chro['chro_time'](I)
    sb_chro['chro_x_mean'] = sb_chro['chro_x_mean'](I)
    sb_chro['chro_y_mean'] = sb_chro['chro_y_mean'](I)
    sb_chro['chro_x_std'] = sb_chro['chro_x_std'](I)
    sb_chro['chro_y_std'] = sb_chro['chro_y_std'](I)
    cmx = find(abs(sb_chro['chro_x_mean']) <100)
    sb_chro['chro_x_mean'] = sb_chro['chro_x_mean'](cmx)
    sb_chro['chro_x_std'] = sb_chro['chro_x_std'](cmx)
    sb_chro['chro_x_time'] = sb_chro['chro_x_time'](cmx)
    cmy = find(abs(sb_chro['chro_y_mean']) <100)
    sb_chro['chro_y_mean'] = sb_chro['chro_y_mean'](cmy)
    sb_chro['chro_y_std'] = sb_chro['chro_y_std'](cmy)
    sb_chro['chro_y_time'] = sb_chro['chro_y_time'](cmy)
    cmx = find(abs(sb_chro['chro_x_std']) <1)
    sb_chro['chro_x_mean'] = sb_chro['chro_x_mean'](cmx)
    sb_chro['chro_x_std'] = sb_chro['chro_x_std'](cmx)
    sb_chro['chro_x_time'] = sb_chro['chro_x_time'](cmx)
    cmy = find(abs(sb_chro['chro_y_std']) <1)
    sb_chro['chro_y_mean'] = sb_chro['chro_y_mean'](cmy)
    sb_chro['chro_y_std'] = sb_chro['chro_y_std'](cmy)
    sb_chro['chro_y_time'] = sb_chro['chro_y_time'](cmy)
    mc_chro_files = dir_list_gen_tree(mc_chro_loc, 'mat', 1)
    chro_ind = find_position_in_cell_lst(strfind(mc_chro_files, fullfile('Chromaticity','Chro_')))
    mc_chro_files = mc_chro_files(chro_ind)
    # generate a list of times generated from the filenames
    file_dates = nan(len(mc_chro_files), 1)
    mc_chro_x = nan(len(mc_chro_files), 1)
    mc_chro_y = nan(len(mc_chro_files), 1)
    mc_chro_time = nan(len(mc_chro_files), 1)
    for wh  in range( 1, len(mc_chro_files)):
        [ _2 , temp_name,  _1 ] = fileparts(mc_chro_files[wh])
        file_dates(wh) = datenum(temp_name[6:-1], 'yyyy-mm-dd_HH-MM-SS')

    inds1 = find(file_dates >  sb_chro['chro_time'](1))
    inds2 = find(file_dates <  sb_chro['chro_time'](end))
    inds3 = intersect(inds1, inds2)
    mc_chro_files = mc_chro_files(inds3)
    for kje  in range( 1, len(mc_chro_files)):
        mc_temp = load(mc_chro_files[kje])
        mc_chro_x(kje) = abs(mc_temp['Chromaticity']['Data'](1))
        mc_chro_y(kje) = abs(mc_temp['Chromaticity']['Data'](2))
        mc_chro_time(kje) = datenum(mc_temp['Chromaticity']['TimeStamp'])


    figure
    sb1 = subplot(2,1,1)
    errorbar(sb_chro['chro_x_time'], sb_chro['chro_x_mean'], sb_chro['chro_x_std'], 'ko')
    if inds3 != 0:
        hold on
        plot(mc_chro_time, mc_chro_x, 'r*')
        hold off

    ylim([0 10])
    grid on
    title('Chromaticity X')
    datetick('x', 'keeplimits')
    sb2 = subplot(2,1,2)
    errorbar(sb_chro['chro_y_time'], sb_chro['chro_y_mean'], sb_chro['chro_y_std'], 'ko')
    if inds3 != 0:
        hold on
        plot(mc_chro_time, mc_chro_y, 'r*')
        hold off

    ylim([0 10])
    grid on
    title('Chromaticity Y')
    datetick('x', 'keeplimits')
    linkaxes([sb1, sb2], 'x')
    print('')
    return chro

def mbf_chromaticity_capture(input_settings, pv_names):
    # Captures chromaticity data['']
    #   Args:
    #       input_settings(struct): containing
    #           mbf_axis (str): Selects which MBF axis to work on (x, y, s)['']
    #           n_repeats (int): The number of repeat datapoints to capture
    #           n_trys (int): How many times to retry on bad data return['']
    #   Returns:
    #       chromaticity (struct): data structure containing the experimental
    #                          results[''] [optional output]
    #
    # example data = mbf_chromaticity_capture(input_settings, pv_names)
    for nd  in range( 1, input_settings['n_repeats']):
        chromaticity['data'](nd) = chromaticity_from_sidebands(
            input_settings['mbf_axis'], input_settings['n_trys'], pv_names)
        pause(1['2']) # make sure there is new data['']

    chromaticity['mean'] = mean(chromaticity['data'], 'omitnan')
    chromaticity['std'] = std(chromaticity['data'], 0, 'omitnan')
