    return 

def MBF_single_kick_capture(mbf_axis, excitation_gain, excitation_frequency, varargin):
    # Sets up the FLL with an additional excitation at a user defined gain and
    # frequency/tune['']
    #   Args:
    #       mbf_axis(str): 'x', or 'y'
    #       excitation_gain(vector of floats): the magnitude of the excitation in dB['']
    #       excitation_frequency(vector of floats): The tune value of the additional excitation
    #       harmonic(vector of ints): The tune harmonic to operate on['']
    #       BPM_data_capture_len(float): Amount of FA data to capture from
    #                                       the BPMs in seconds
    #       save_to_archive(str): 'yes' or 'no'
    #       additional_save_location(str): if specified the data will be saved
    #                                      to this location['']
    #   Returns:
    #       single_kick(struct): data captured from the BPMs['']
    #
    # Example: data = MBF_single_kick_capture('x', -18, 0['27'], 'save_to_archive', 'no')
    # Define input and default values
    binary_string = {'yes', 'no'}
    validScalarNum = @(x) isnumeric(x) and isscalar(x)
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_string = @(x) ischar(x)
    addRequired(p, 'mbf_axis')
    addRequired(p, 'excitation_gain')
    addRequired(p, 'excitation_frequency')
    addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)))
    addParameter(p, 'additional_save_location', NaN, valid_string)
    addParameter(p, 'harmonic', 0, validScalarNum)
    addParameter(p, 'excitation_delay', 1, validScalarNum)
    addParameter[p, 'BPMs_to_capture', 1:173]
    addParameter(p, 'repeat_points', 10, validScalarNum)
    parse[p, mbf_axis, excitation_gain, excitation_frequency, varargin[:]]
    # Set up MBF environment
    [root_string,  _3 ,  _2 ,  _1 ] = mbf_system_config
    root_string = root_string[1]
    ## Get environment data
    # getting general environment data['']
    single_kick = machine_environment
    # Add the axis label to the data structure['']
    single_kick['ax_label'] = mbf_axis
    # construct name and add it to the structure
    single_kick['base_name'] = ['single_kick_' single_kick['ax_label'] '_axis']
    # Excitation frequency and gain
    single_kick['excitation_gain'] = excitation_gain
    single_kick['excitation_frequency'] = excitation_frequency
    single_kick['harmonic'] = p['Results']['harmonic']
    single_kick['excitation_delay'] = p['Results']['excitation_delay']
    ## Set up MBF excitation
    mbf_name = mbf_axis_to_name(mbf_axis)
    orig_seq = get_variable[[mbf_name, 'TRG:SEQ:MODE_S']]
    ## Set up BPM capture
    # bpm_capture_length = 1024; #Turns
    # setup_BPM_TbT_capture(nbpms, bpm_capture_length)
    ## Do measurements
    input_settings = p['Results']
    # gain scan
    if len(p['Results']['excitation_gain']) > 1:
        for whd  in range( 1, len(p['Results']['excitation_gain'])):
            print('Measurement #d\n',whd)
            input_settings['excitation_gain'] = p['Results']['excitation_gain'](whd)
            input_settings['excitation_frequency'] = p['Results']['excitation_frequency'](1)
            input_settings['harmonic'] = p['Results']['harmonic'](1)
            single_kick['scan_label'] = 'Gain'
            single_kick['bpm_data'][whd] = single_kick_aquisition(mbf_axis, input_settings)

        # frequency scan
    elif len(p['Results']['excitation_frequency']) > 1:
        for nwa  in range( 1, len(p['Results']['excitation_frequency'])):
            print('Measurement #d\n',nwa)
            input_settings['excitation_gain'] = p['Results']['excitation_gain'](1)
            input_settings['excitation_frequency'] = p['Results']['excitation_frequency'](nwa)
            input_settings['harmonic'] = p['Results']['harmonic'](1)
            single_kick['scan_label'] = 'Frequency'
            single_kick['bpm_data'][nwa] = single_kick_aquisition(mbf_axis, input_settings)

        # harmonic scan
    elif len(p['Results']['harmonic']) > 1:
        for nwa  in range( 1, len(p['Results']['excitation_frequency'])):
            print('Measurement #d\n',nwa)
            input_settings['excitation_gain'] = p['Results']['excitation_gain'](1)
            input_settings['excitation_frequency'] = p['Results']['excitation_frequency'](1)
            input_settings['harmonic'] = p['Results']['harmonic'](nwa)
            single_kick['scan_label'] = 'Harmonic'
            single_kick['bpm_data'][nwa] = single_kick_aquisition(mbf_axis, input_settings)

    else:
        input_settings['excitation_gain'] = p['Results']['excitation_gain'](1)
        input_settings['excitation_frequency'] = p['Results']['excitation_frequency'](1)
        input_settings['harmonic'] = p['Results']['harmonic'](1)
        single_kick['scan_label'] = ''
        single_kick['bpm_data'][1] = single_kick_aquisition(mbf_axis, input_settings)

    set_variable[[mbf_name, 'TRG:SEQ:MODE_S'], orig_seq]
    ## saving the data to a file
    if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's'):
        #     only save if not on test system
        if strcmp(p['Results']['save_to_archive'], 'yes'):
            save_to_archive(root_string, single_kick)

        if ~isnan(p['Results']['additional_save_location']):
            save(additional_save_location, single_kick)


    if nargout == 1:
        varargout[1] = single_kick

def mbf_single_kick_plotting(single_kick, single_kick_pp):
    if strcmp(single_kick['scan_label'], 'Frequency'):
        plot_single_kick_scan(single_kick['excitation_frequency'], 
            single_kick_pp['beam_oscillation_x'], 'Excitation frequency [tune]',
            'Horizontal kick')
        plot_single_kick_scan(single_kick['excitation_frequency'], 
            single_kick_pp['beam_oscillation_y'], 'Excitation frequency [tune]',
            'Vertical kick')

    if strcmp(single_kick['scan_label'], 'Harmonic'):
        plot_single_kick_scan(single_kick['harmonic'], 
            single_kick_pp['beam_oscillation_x'], 'Excitation frequency [tune]',
            'Horizontal kick')
        plot_single_kick_scan(single_kick['harmonic'], 
            single_kick_pp['beam_oscillation_y'], 'Excitation frequency [tune]',
            'Vertical kick')

    if strcmp(single_kick['scan_label'], 'Gain'):
        plot_single_kick_scan(single_kick['excitation_gain'], 
            single_kick_pp['beam_oscillation_x'], 'Excitation gain [dB]',
            'Horizontal kick')
        plot_single_kick_scan(single_kick['excitation_gain'], 
            single_kick_pp['beam_oscillation_y'], 'Excitation gain [dB]', 
            'Vertical kick')

    if strcmp(single_kick['scan_label'], ''):
        # plots for a single capture['']
        #     # Raw time plots
        used_bpms = single_kick_pp['used_bpms']
        figure
        hold on
        for kds  in range( 1, len(used_bpms)):
            plot(squeeze(single_kick_pp['beam_signal_x'][1, kds, :]))

        legend(used_bpms)
        ylabel('BPM motion [\mum]')
        xlabel('Time')
        figure
        hold on
        for kds  in range( 1, len(used_bpms)):
            plot(squeeze(single_kick_pp['beam_signal_y'][1, kds, :]))

        legend(used_bpms)
        ylabel('BPM motion [\mum]')
        xlabel('Time')
        # RMS motion plots
        figure
        plot(1:len(used_bpms), single_kick_pp['beam_oscillation_x'][1, :], '*')
        ylabel('Ver[''] RMS oscillation (baseline removed) [\mum]')
        title('Horizontal kick')
        figure
        plot(1:len(used_bpms), single_kick_pp['beam_oscillation_y'][1,:], '*')
        ylabel('Ver[''] RMS oscillation (baseline removed) [\mum]')
        title('Vertical kick')

    return varargout 

def mbf_single_kick_postprocessing(single_kick):
    bpm_datatypes = {'bpm_FR_data', 'bpm_FT_data', 'bpm_TbT_data'}
    selected_datatype = bpm_datatypes[1]
    scan_length = len(single_kick['bpm_data'])
    used_bpms = fieldnames(single_kick['bpm_data'][1][selected_datatype][1])
    n_repeats = len(single_kick['bpm_data'][1][selected_datatype])
    for nfe  in range( 1, scan_length):
        for kds  in range( 1, len(used_bpms)):
            x_data_temp = NaN(n_repeats, len(single_kick['bpm_data'][nfe][selected_datatype][1][used_bpms[kds]]['X']))
            y_data_temp = NaN(n_repeats, len(single_kick['bpm_data'][nfe][selected_datatype][1][used_bpms[kds]]['Y']))
            for shd  in range( 1, n_repeats):
                x_data_temp[shd,:] = single_kick['bpm_data'][nfe][selected_datatype][shd][used_bpms[kds]]['X']
                y_data_temp[shd,:] = single_kick['bpm_data'][nfe][selected_datatype][shd][used_bpms[kds]]['Y']

            x_mean = mean(x_data_temp, 1)
            y_mean = mean(y_data_temp, 1)
            single_kick_pp['beam_signal_x'][nfe, kds, :] = x_mean
            single_kick_pp['beam_signal_y'][nfe, kds, :] = y_mean
            single_kick_pp['beam_oscillation_x'](nfe, kds) = std(x_mean)
            single_kick_pp['beam_oscillation_y'](nfe, kds) = std(y_mean)



    single_kick['used_bpms'] = used_bpms
def mbf_single_kick_setup(mbf_axis, varargin):
    # Sets up the Multibunch feedback system to
    #   Args: (All optional)
    #       excitation(float): The power of the oscillator in the selected axis (in dB)['']
    #       harmonic(int): The harmonic to operate on[''] Sometimes higher
    #                      harmonics have better signal to noise ratios['']
    #                      Also where the amplifiers/stripline provide
    #                      better efficiency['']
    #                      This will produce more blowup per RF power['']
    #       excitation_frequency(float): Usually you want the sideband
    #                                    frequency[''] However this allow a user
    #                                    defined tune value to be used['']
    #
    # Example: mbf_emittance_setup('x')
    default_excitation_frequency = 0['28']; #dB
    default_excitation_gain = -60; #dB
    default_harmonic = 10
    default_delay = 1
    validScalarNum = @(x) isnumeric(x) and isscalar(x)
    p = inputParser
    addRequired(p, 'mbf_axis')
    addParameter(p, 'excitation_gain', default_excitation_gain, validScalarNum)
    addParameter(p, 'harmonic', default_harmonic, validScalarNum)
    addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
    addParameter(p, 'delay', default_delay, validScalarNum)
    parse[p,mbf_axis, varargin[:]]
    mbf_name = mbf_axis_to_name(mbf_axis)
    ## Turning off the external trigger
    set_variable['LI-TI-MTGEN-01:BS-DI-MODE', 0]
    ## Setting up the sequencer for single shot
    set_variable[[mbf_name, 'TRG:SEQ:MODE_S'], 'One Shot']
    ## Setting up the excitation
    set_variable[[mbf_name, 'SEQ:PC_S'], 2]
    set_variable[[mbf_name, 'SEQ:2:BANK_S'], 'Bank 1']
    set_variable[[mbf_name, 'SEQ:2:START_FREQ_S'], p['Results']['harmonic'] + p['Results']['excitation_frequency']]
    set_variable[[mbf_name, 'SEQ:2:STEP_FREQ_S'], 0]
    set_variable[[mbf_name, 'SEQ:2:COUNT_S'], 1]
    set_variable[[mbf_name, 'SEQ:2:DWELL_S'], p['Results']['delay']]
    set_variable[[mbf_name, 'SEQ:2:ENABLE_S'], 'Off']
    set_variable[[mbf_name, 'SEQ:1:START_FREQ_S'], p['Results']['harmonic'] + p['Results']['excitation_frequency']]
    set_variable[[mbf_name, 'SEQ:1:STEP_FREQ_S'], 0]
    set_variable[[mbf_name, 'SEQ:1:COUNT_S'], 1]
    set_variable[[mbf_name, 'SEQ:1:DWELL_S'], 1]
    set_variable[[mbf_name, 'SEQ:1:ENABLE_S'], 'On']
    set_variable[[mbf_name, 'SEQ:1:GAIN_DB_S'], p['Results']['excitation_gain']]
def plot_single_kick_scan(data_x, data_y, label_x, graph_title):
    figure
    hold on
    for wse  in range( 1, size(data_y,2)):
        temp = squeeze(data_y(:,wse))['']*1e-3
        temp = temp - min(temp)
        plot(data_x, temp,'['']-')

    xlabel(label_x)
    ylabel('Ver[''] RMS oscillation (baseline removed) [\mum]')
    title(graph_title)
    return single_kick_pp 

def single_kick_aquisition(mbf_axis, input_settings):
    mbf_name = mbf_axis_to_name(mbf_axis)
    for hdr  in range( 1, input_settings['repeat_points']):
        mbf_single_kick_setup(mbf_axis,
            'excitation_gain', input_settings['excitation_gain'],
            'excitation_frequency',input_settings['excitation_frequency'], 
            'harmonic', input_settings['harmonic'],
            'delay', input_settings['excitation_delay'])
        set_variable[[mbf_name, 'TRG:SEQ:ARM_S['PROC']'], 1]
        # arm_BPM_TbT_capture(input_settings['BPMs_to_capture'])
        BPM_set_switching_off(input_settings['BPMs_to_capture'])
        pause(1)
        set_variable['LI-TI-MTGEN-01:BS-DI-MODE', 1]
        # single_kick['bpm_TbT_data'] = get_BPM_TbT_data_XY_only(input_settings['BPMs_to_capture'], bpm_capture_length)
        # single_kick['bpm_FT_data'] = get_BPM_FT_data_XY_only(input_settings['BPMs_to_capture'])
        output['bpm_FR_data'][hdr] = get_BPM_FR_data_XY_only(input_settings['BPMs_to_capture'])
        BPM_set_switching_on(input_settings['BPMs_to_capture'])

    return output 

def single_kick_dataset_capture(nbpms):
    out['bpm_TbT_data'] = get_BPM_TbT_data_XY_only(nbpms)
    # out['bpm_FT_data'] = get_BPM_FT_data_XY_only(nbpms)
    # out['mbf_data_x'] = get_variable['SR23C-DI-TMBF-01:X:ADC:MMS:STD']
    # out['mbf_data_y'] = get_variable['SR23C-DI-TMBF-01:Y:ADC:MMS:STD']
