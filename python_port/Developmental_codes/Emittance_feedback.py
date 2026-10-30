    return 

def MBF_excitation_capture(mbf_axis, excitation_gain, varargin):
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
    #       emittance_blowup(struct): data captured from the BPMs and the cameras['']
    #
    # Example: data = MBF_beam_excitation_capture('x', -18, 0['27'], 'save_to_archive', 'no')
    # Define input and default values
    binary_string = {'yes', 'no'}
    validScalarNum = @(x) isnumeric(x) and isscalar(x)
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_string = @(x) ischar(x)
    addRequired(p, 'mbf_axis')
    addRequired(p, 'excitation_gain')
    addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)))
    addParameter(p, 'additional_save_location', NaN, valid_string)
    addParameter(p, 'harmonic', 0, validScalarNum)
    addParameter(p, 'BPM_data_capture_length', 1, validScalarNum)
    parse[p, mbf_axis, excitation_gain, varargin[:]]
    # Set up MBF environment
    [root_string,  _3 ,  _2 ,  _1 ] = mbf_system_config
    root_string = root_string[1]
    ## Get environment data
    # getting general environment data['']
    emittance_blowup = machine_environment
    # Add the axis label to the data structure['']
    emittance_blowup['ax_label'] = mbf_axis
    # construct name and add it to the structure
    emittance_blowup['base_name'] = ['emittance_gain_scan_' emittance_blowup['ax_label'] '_axis']
    emittance_blowup['harmonic'] = p['Results']['harmonic']
    ## Set up MBF excitation
    mbf_name = mbf_axis_to_name(mbf_axis)
    mbf_emittance_setup(mbf_axis, 'excitation', excitation_gain(1),
        'harmonic', p['Results']['harmonic'])
    ## Do measurement
    orig_gain = get_variable[[mbf_name, 'NCO2:GAIN_DB_S']]
    # gain scan
    for whd  in range( 1, len(p['Results']['excitation_gain'])):
        print('Measurement #d\n',whd)
        set_variable[[mbf_name, 'NCO2:ENABLE_S'], 0]
        set_variable([mbf_name, 'NCO2:GAIN_DB_S'],p['Results']['excitation_gain'](whd))
        pause(2)
        for nds  in range( 1, 160):
            if nds >= 40 and nds < 120:
                set_variable[[mbf_name, 'NCO2:ENABLE_S'], 1]
                excitation_gain = p['Results']['excitation_gain'](whd)
            else:
                set_variable[[mbf_name, 'NCO2:ENABLE_S'], 0]
                excitation_gain = 0

            pause(0['25'])
            while ~strcmp('Fit Forced',get_variable['SR-DI-EMIT-01:STATUS']) and ~strcmp('Successful',get_variable['SR-DI-EMIT-01:STATUS']):
                pause(0['2'])

            emittance_blowup['scan'][whd][nds]['emittance'] = emittance_get_data
            emittance_blowup['excitation_gain'][whd][nds] = excitation_gain


    set_variable[[mbf_name, 'NCO2:GAIN_DB_S'], orig_gain]
    set_variable[[mbf_name, 'NCO2:ENABLE_S'], 0]
    ## saving the data to a file
    if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's'):
        #     only save if not on test system
        if strcmp(p['Results']['save_to_archive'], 'yes'):
            save_to_archive(root_string, emittance_blowup)

        if ~isnan(p['Results']['additional_save_location']):
            save(additional_save_location, emittance_blowup)


    if nargout == 1:
        varargout[1] = emittance_blowup

    return varargout 

def emittance_control_loop(selected_axis, emittance_target, varargin):
    # This changes the gain of the excitation for the selected axis in order to
    # reach the requested emittance target['']
    # This presumes that mbf_emittance_setup has been run beforehand['']
    #   Args:
    #       selected_axis(str): 'X' or 'Y'
    #       emittance_target(float): nm rad for horizontal, pm rad for vertical['']
    #
    # Example: emittance_control_loop('Y', 9)
    [ _2 ,  _1 , pv_names] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    selected_axis = lower(selected_axis)
    if ~strcmp(selected_axis, 'x') and ~strcmp(selected_axis, 'y'):
        error['EmittanceControl:Main','Invalid axis selected for emittance control loop']

    # The time needed to get new data from the underlying hardware['']
    hardware_update_time = 0['5']; #sec
    output_lim = 1
    prev_error = 0
    u_I = 0
    u_D = 0
    Kp = 10E3
    Ki = 1
    Kd = 0['1']
    N = 10
    default_slew_rate_limit = 0['2']; # in pm rad for Y and nm rad for X
    default_fraction_to_apply = 0['075']
    default_low_power_limit = 0['00098']; #~-60dB
    default_high_power_limit = 0['0625']; #~-20dB
    default_start_power_level = 0['004']; #~-46dB
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_number = @(x) isnumeric(x)
    addRequired(p, 'selected_axis')
    addRequired(p, 'emittance_target')
    addParameter(p, 'slew_rate_limit', default_slew_rate_limit, valid_number)
    addParameter(p, 'fraction_to_apply', default_fraction_to_apply, valid_number)
    addParameter(p, 'low_power_limit', default_low_power_limit, valid_number)
    addParameter(p, 'high_power_limit', default_high_power_limit, valid_number)
    addParameter(p, 'start_power_level', default_start_power_level, valid_number)
    addParameter(p, 'continual', 'yes')
    addParameter(p, 'loop_type', 'pi')
    parse[p, selected_axis, emittance_target, varargin[:]]
    mbf_device = mbf_names[''](p['Results']['selected_axis'])
    if strcmp(p['Results']['continual'], 'yes'):
        while true:
            main_loop

    else:
        for step  in range( 1, 200):
            main_loop
            emit_val  = get_variable(pv_names['emittance'][''](lower(selected_axis))['val'])
            power_val = get_variable([mbf_device, pv_names['tails']['NCO2']['gain_scalar']])
            # Save into logging vectors
            output['r_log'](step) = emittance_target
            output['y_log'](step) = emit_val
            output['u_log'](step) = power_val
            output['time_log'](step) = (step - 1) * 0['5']; # 0['5'] sec hardware interval


    def main_loop:
            # The loop holds the existing settings if topup is on
            # The !=0 accounts for the -1 when topup is turned off as well as the
            # usual countdown when it is on['']
            # The loop holds the existing settings if the current drops below 10mA
            # The loop holds the existing settings if it is unable to get an up to date
            # emittance reading['']
            if get_variable(pv_names['topup']['countdown']) != 0  and:
                    get_variable(pv_names['current']) > 10 and
                    strcmp(get_variable(pv_names['emittance']['status']), 'Successful')
                heartbeat('['']')
                ## Check the status of the frequency locked loop['']
                error_user = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['stop']])
                error_detector_overflow = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['detector_overflow']])
                error_offset = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['offset_overflow']])
                error_magnitude = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['magnitude_error']])
                if ~strcmp(error_detector_overflow[1], 'Ok') ||:
                        ~strcmp(error_offset[1], 'Ok') ||
                        ~strcmp(error_magnitude[1], 'Ok') ||
                        ~strcmp(error_user[1], 'Ok')
                    error['EmittanceControl:Main',[mbf_device,' frequency locked loop has stopped']]

                if ~strcmp(get_variable([mbf_device, mbf_vars['NCO2']['enable']]), 'On'):
                    error['EmittanceControl:Main',[mbf_device, 'Excitation manually terminated']]

                ## Get current settings
                # This pause is to allow the hardware to update so we know we have fresh
                # data['']
                pause(hardware_update_time)
                tune = get_variable(char(strcat(mbf_device, mbf_vars['tune']['centre'])))
                emit = get_variable(pv_names['emittance'][selected_axis]['val'])
                emit_mean = get_variable(pv_names['emittance'][selected_axis]['mean'])
                power_input = get_variable(char(strcat(mbf_device, mbf_vars['NCO2']['gain_scalar'])))
                if isnan(tune):
                    # pause if tune value is invalid['']
                    print('\nTune value is invalid['']')
                    return

                ## Running the requested control calculation['']
                if strcmp(p['Results']['loop_type'], 'pi'):
                    power_new = pi_loop(emit, emit_mean, power_input)
                elif strcmp(p['Results']['loop_type'], 'position_pid'):
                    power_new = position_pid(emit, power_input)
                else:
                    error('Please select a valid loop type (pi or position_pid)')

                # Apply power limits and apply
                if power_new > p['Results']['low_power_limit'] and power_new < p['Results']['high_power_limit']:
                    set_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']], power_new)

            else:
                # The machine is not in a state for the loop to run so wait and try
                # later['']
                heartbeat('*')
                pause(1)


    return output 

def pi_loop(emit, emit_mean, power_input):
            ## Main feedback def :
            # if the difference between the instantaneous emittance value and the
            # mean value is small then use the mean value[''] This allows faster
            # initial following using the instantainous values but more stable
            # steady state using the mean values['']
            if abs(emit - emit_mean) <0['01']:
                emit = emit_mean

            # Get the error term
            emit_error = p['Results']['emittance_target'] - emit
            # Apply slew rate limit['']
            if abs(emit_error) > p['Results']['slew_rate_limit']:
                emit_error = sign(emit_error) * p['Results']['slew_rate_limit']

            # error scaling from emittance to output power['']
            power_error = sign(emit_error) * abs(1E-3 * log10(abs(emit_error)))
            # fraction to apply
            power_error = power_error * p['Results']['fraction_to_apply']
            # power monitor
            power_new = power_input - power_error

    return power_new 

def position_pid(emit, power_input):
            emit_error = p['Results']['emittance_target'] - emit
            # 1[''] Proportional Term
            u_P = Kp * emit_error
            # 2[''] Filtered Derivative Term (Low-pass filtered differentiator)
            # Formulation: u_D(k) = (1/(1+N*dt))*u_D(k-1) + (Kd*N*dt/(1+N*dt))*(error - prev_error)/dt
            alpha = 1 / (1 + N * hardware_update_time)
            u_D = alpha * u_D + (1 - alpha) * Kd * N * (emit_error - prev_error)
            # 3[''] Calculate ideal output before saturation
            u_ideal = u_P + u_I + u_D
            # 4[''] Apply Actuator Saturation
            u = max(p['Results']['low_power_limit'], min(p['Results']['high_power_limit'], u_ideal))
            # 5[''] Anti-Windup Clamping (Conditional Integration)
            # Only integrate if the controller is NOT saturated, OR if integrating pulls it OUT of saturation
            is_saturated = (u_ideal != u)
            same_sign = (sign(emit_error) == sign(u_ideal))
            if ~(is_saturated and same_sign):
                u_I = u_I + Ki * emit_error * hardware_update_time; # Update integrator

            # 6[''] Update states for next step
            prev_error = emit_error
            power_new = power_input - sign(emit_error) * abs(1E-3 * log10(abs(emit_error)))

    def heartbeat(mark):
            if output_lim >100:
                print([mark, '\n'])
                output_lim = 1
            else:
                print(mark)
                output_lim = output_lim +1



def emittance_control_loop_dd_pid_v1(selected_axis, emittance_target, varargin):
    # This changes the gain of the excitation for the selected axis in order to
    # reach the requested emittance target['']
    # This presumes that mbf_emittance_setup has been run beforehand['']
    #   Args:
    #       selected_axis(str): 'X' or 'Y'
    #       emittance_target(float): nm rad for horizontal, pm rad for vertical['']
    #
    # Example: emittance_control_loop('Y', 9)
    # Example with DD-PID: emittance_control_loop('Y', 9, 'use_data_driven', true, 'database_file', 'emittance_dd_database['mat']')
    [ _2 ,  _1 , pv_names] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    selected_axis = lower(selected_axis)
    if ~strcmp(selected_axis, 'x') and ~strcmp(selected_axis, 'y'):
        error['EmittanceControl:Main','Invalid axis selected for emittance control loop']

    # The time needed to get new data from the underlying hardware['']
    hardware_update_time = 0['5']; #sec
    default_slew_rate_limit = 0['2']; # in pm rad for Y and nm rad for X
    default_fraction_to_apply = 0['075']
    default_low_power_limit = 0['00098']; #~-60dB
    default_high_power_limit = 0['0625']; #~-20dB
    default_start_power_level = 0['004']; #~-46dB
    # Data-Driven PID Defaults
    default_use_data_driven = true
    default_database_file = char(strcat('emittance_dd_database_',selected_axis,'['mat']'))
    default_k_neighbors = 5
    default_pid_gains = [1e-4, 5e-5, 2e-5]; # [Kp, Ki, Kd] default baseline
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_number = @(x) isnumeric(x)
    valid_bool = @(x) islogical(x) || (isnumeric(x) and (x==0 || x==1))
    valid_str_or_struct = @(x) ischar(x) || isstring(x) || isstruct(x)
    addRequired(p, 'selected_axis')
    addRequired(p, 'emittance_target')
    addParameter(p, 'slew_rate_limit', default_slew_rate_limit, valid_number)
    addParameter(p, 'fraction_to_apply', default_fraction_to_apply, valid_number)
    addParameter(p, 'low_power_limit', default_low_power_limit, valid_number)
    addParameter(p, 'high_power_limit', default_high_power_limit, valid_number)
    addParameter(p, 'start_power_level', default_start_power_level, valid_number)
    # Data-Driven PID Parameters
    addParameter(p, 'use_data_driven', default_use_data_driven, valid_bool)
    addParameter(p, 'database_file', default_database_file, valid_str_or_struct)
    addParameter(p, 'k_neighbors', default_k_neighbors, valid_number)
    addParameter(p, 'fixed_pid_gains', default_pid_gains, valid_number)
    parse[p, selected_axis, emittance_target, varargin[:]]
    mbf_device = mbf_names[''](p['Results']['selected_axis'])
    # Load Data-Driven Database if enabled
    use_dd = p['Results']['use_data_driven']
    if use_dd:
        if isstruct(p['Results']['database_file']):
            dd_db = p['Results']['database_file']
        elif isfile(p['Results']['database_file']):
            dd_db = load(p['Results']['database_file'])
            print['Loaded Data-Driven PID database: #s\n', p['Results']['database_file']]
        else:
            warning['EmittanceControl:DD_PID', 'Database file #s not found[''] Falling back to baseline PID['']', p['Results']['database_file']]
            use_dd = false


    # Initialize historical state variables for PID & Query vector
    emit_prev  = NaN
    emit_prev2 = NaN
    power_prev = p['Results']['start_power_level']
    # start the NCO excitation['']
    set_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']], p['Results']['start_power_level'])
    output_lim = 1
    while true:
        # The loop holds the existing settings if topup is on
        # The !=0 accounts for the -1 when topup is turned off as well as the
        # usual countdown when it is on['']
        # The loop holds the existing settings if the current drops below 10mA
        # The loop holds the existing settings if it is unable to get an up to date
        # emittance reading['']
        if get_variable(pv_names['topup']['countdown']) != 0  and:
                get_variable(pv_names['current']) > 10 and
                strcmp(get_variable(pv_names['emittance']['status']), 'Successful')
            ## heartbeat code
            if output_lim >100:
                print('['']\n')
                output_lim = 1
            else:
                print('['']')
                output_lim = output_lim +1

            ## Check the status of the frequency locked loop['']
            error_user = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['stop']])
            error_detector_overflow = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['detector_overflow']])
            error_offset = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['offset_overflow']])
            error_magnitude = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['magnitude_error']])
            if ~strcmp(error_detector_overflow[1], 'Ok') ||:
                    ~strcmp(error_offset[1], 'Ok') ||
                    ~strcmp(error_magnitude[1], 'Ok') ||
                    ~strcmp(error_user[1], 'Ok')
                error['EmittanceControl:Main',[mbf_device,' frequency locked loop has stopped']]

            if ~strcmp(get_variable([mbf_device, mbf_vars['NCO2']['enable']]), 'On'):
                error['EmittanceControl:Main',[mbf_device, 'Excitation manually terminated']]

            ## Get current settings
            # This pause is to allow the hardware to update so we know we have fresh
            # data['']
            pause(hardware_update_time)
            tune = get_variable([mbf_device, mbf_vars['tune']['centre']])
            emit = get_variable(pv_names['emittance'][selected_axis]['val'])
            emit_mean = get_variable(pv_names['emittance'][selected_axis]['mean'])
            power_input = get_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']])
            if isnan(tune):
                # pause if tune value is invalid['']
                print('\nTune value is invalid['']')
                continue

            ## Main feedback def :
            # if the difference between the instantaneous emittance value and the
            # mean value is small then use the mean value[''] This allows faster
            # initial following using the instantainoues values but more stable
            # steady state using the mean values['']
            if abs(emit - emit_mean) <0['01']:
                emit = emit_mean

            # Initialize past history if first valid step
            if isnan(emit_prev):
                emit_prev = emit
                emit_prev2 = emit

            # Get the error term
            emit_error = p['Results']['emittance_target'] - emit
            # Apply slew rate limit['']
            if abs(emit_error) > p['Results']['slew_rate_limit']:
                emit_error = sign(emit_error) * p['Results']['slew_rate_limit']

            if use_dd:
                ## DATA-DRIVEN PID CONTROLLER (Step 1 & Step 2)
                # Form query vector: phi_query = [r(t+1), r(t), y(t), y(t-1), u(t-1)]
                phi_query = [p['Results']['emittance_target'], p['Results']['emittance_target'], emit, emit_prev, power_prev]
                # Step 1: Calculate L1 normalized distance to database items
                N_db = size(dd_db['DB_phi'], 1)
                range_val = dd_db['phi_max'] - dd_db['phi_min']
                range_val(range_val < 1e-12) = 1['0']
                diff_norm = abs(dd_db['DB_phi'] - repmat(phi_query, N_db, 1)) ['']/ repmat(range_val, N_db, 1)
                d = sum(diff_norm, 2)
                # Find k-nearest neighbors
                [sorted_d, sorted_idx] = sort(d, 'ascend')
                k_eff = min(p['Results']['k_neighbors'], N_db)
                knn_idx = sorted_idx[1:k_eff]
                knn_dist = sorted_d[1:k_eff]
                # Step 2: Compute weights and interpolate adaptive PID gains
                if knn_dist(1) < 1e-10:
                    weights = zeros(k_eff, 1)
                    weights(1) = 1['0']
                else:
                    inv_d = 1['0'] ['']/ knn_dist
                    weights = inv_d / sum(inv_d)

                K_t = sum(repmat(weights, 1, 3) ['']* dd_db['DB_K'][knn_idx, :], 1)
                Kp = K_t(1); Ki = K_t(2); Kd = K_t(3)
                # Velocity PID increments
                dy  = emit - emit_prev
                d2y = emit - 2 * emit_prev + emit_prev2
                delta_power = Ki * emit_error - Kp * dy - Kd * d2y
                power_new = power_input + delta_power
            else:
                ## ORIGINAL LOGARITHMIC CONTROL LAW (Fallback)
                # error scaling from emittance to output power['']
                power_error = sign(emit_error) * 1E-3 * log10(abs(emit_error))
                # fraction to apply
                power_error = power_error * p['Results']['fraction_to_apply']
                # power monitor
                power_new = power_input - power_error

            # Update historical state variables
            emit_prev2 = emit_prev
            emit_prev  = emit
            power_prev = power_input
            # Apply power limits and apply
            if power_new > p['Results']['low_power_limit'] and power_new < p['Results']['high_power_limit']:
                set_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']], power_new)

        else:
            # The machine is not in a state for the loop to run so wait and try
            # later['']
            pause(1)
            ## heartbeat code
            if output_lim >100:
                print('*\n')
                output_lim = 1
            else:
                print('*')
                output_lim = output_lim +1



def emittance_control_loop_velocty_pid(selected_axis, emittance_target, varargin):
    # This changes the gain of the excitation for the selected axis in order to
    # reach the requested emittance target['']
    # This presumes that mbf_emittance_setup has been run beforehand['']
    #   Args:
    #       selected_axis(str): 'X' or 'Y'
    #       emittance_target(float): nm rad for horizontal, pm rad for vertical['']
    #
    # Example: emittance_control_loop('Y', 9)
    [ _2 ,  _1 , pv_names] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    selected_axis = lower(selected_axis)
    if ~strcmp(selected_axis, 'x') and ~strcmp(selected_axis, 'y'):
        error['EmittanceControl:Main','Invalid axis selected for emittance control loop']

    # The time needed to get new data from the underlying hardware['']
    hardware_update_time = 0['5']; #sec
    default_slew_rate_limit = 0['2']; # in pm rad for Y and nm rad for X
    default_fraction_to_apply = 0['075']
    default_low_power_limit = 0['00098']; #~-60dB
    default_high_power_limit = 0['0625']; #~-20dB
    default_start_power_level = 0['004']; #~-46dB
    default_pid_gains = [1e-1, 0['5e']-1, 2e-2]; # [Kp, Ki, Kd] default baseline
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_number = @(x) isnumeric(x)
    addRequired(p, 'selected_axis')
    addRequired(p, 'emittance_target')
    addParameter(p, 'slew_rate_limit', default_slew_rate_limit, valid_number)
    addParameter(p, 'fraction_to_apply', default_fraction_to_apply, valid_number)
    addParameter(p, 'low_power_limit', default_low_power_limit, valid_number)
    addParameter(p, 'high_power_limit', default_high_power_limit, valid_number)
    addParameter(p, 'start_power_level', default_start_power_level, valid_number)
    addParameter(p, 'fixed_pid_gains', default_pid_gains, valid_number)
    parse[p, selected_axis, emittance_target, varargin[:]]
    mbf_device = mbf_names[''](p['Results']['selected_axis'])
    Kp = p['Results']['fixed_pid_gains'](1)
    Ki = p['Results']['fixed_pid_gains'](2)
    Kd = p['Results']['fixed_pid_gains'](3)
    # start the NCO excitation['']
    set_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']], p['Results']['start_power_level'])
    output_lim = 1
    emit_input_prev = 0
    emit = 0
    while true:
        # The loop holds the existing settings if topup is on
        # The !=0 accounts for the -1 when topup is turned off as well as the
        # usual countdown when it is on['']
        # The loop holds the existing settings if the current drops below 10mA
        # The loop holds the existing settings if it is unable to get an up to date
        # emittance reading['']
        if get_variable(pv_names['topup']['countdown']) != 0  and:
                get_variable(pv_names['current']) > 10 and
                strcmp(get_variable(pv_names['emittance']['status']), 'Successful')
            ## heartbeat code
            if output_lim >100:
                print('['']\n')
                output_lim = 1
            else:
                print('['']')
                output_lim = output_lim +1

            ## Check the status of the frequency locked loop['']
            error_user = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['stop']])
            error_detector_overflow = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['detector_overflow']])
            error_offset = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['offset_overflow']])
            error_magnitude = get_variable([mbf_device, mbf_vars['pll']['stop_reasons']['magnitude_error']])
            if ~strcmp(error_detector_overflow[1], 'Ok') ||:
                    ~strcmp(error_offset[1], 'Ok') ||
                    ~strcmp(error_magnitude[1], 'Ok') ||
                    ~strcmp(error_user[1], 'Ok')
                error['EmittanceControl:Main',[mbf_device,' frequency locked loop has stopped']]

            if ~strcmp(get_variable([mbf_device, mbf_vars['NCO2']['enable']]), 'On'):
                error['EmittanceControl:Main',[mbf_device, 'Excitation manually terminated']]

            ## Get current settings
            # This pause is to allow the hardware to update so we know we have fresh
            # data['']
            pause(hardware_update_time)
            tune = get_variable(char(strcat(mbf_device, mbf_vars['tune']['centre'])))
            #         emit_mean = get_variable(pv_names['emittance'][selected_axis]['mean'])
            print('Power history')
            emit_input_prev2 = emit_input_prev
            emit_input_prev = emit
            emit = get_variable(pv_names['emittance'][selected_axis]['val'])
            #         emit = get_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']])
            print(emit)
            if isnan(tune):
                # pause if tune value is invalid['']
                print('\nTune value is invalid['']')
                continue

            ## Main feedback def :
            # if the difference between the instantaneous emittance value and the
            # mean value is small then use the mean value[''] This allows faster
            # initial following using the instantainoues values but more stable
            # steady state using the mean values['']
            #         if abs(emit - emit_mean) <0['01']
            #             emit = emit_mean
            #         end #if
            # Get the error term
            emit_error = p['Results']['emittance_target'] - emit
            # Apply slew rate limit['']
            if abs(emit_error) > p['Results']['slew_rate_limit']:
                emit_error = sign(emit_error) * p['Results']['slew_rate_limit']

            # error scaling from emittance to output power['']
            #         power_error = sign(emit_error) * 1E-3 * log10(abs(emit_error))
            # Velocity PID increments
            #             dy  = power_input - power_error
            #             d2y = power_input - 2 * power_input_prev + power_input_prev2
            #
            #             delta_power = Ki * power_error + Kp * dy + Kd * d2y
            #             power_new = power_input - delta_power
            dy  = emit - emit_error
            d2y = emit - 2 * emit_input_prev + emit_input_prev2
            delta_emit = Ki * emit_error - Kp * dy - Kd * d2y
            power_new = 1e-2 * log10(abs(emit + delta_emit))
            #             delta_power = Ki * power_error + Kp * power_error + Kd * power_error
            #             power_new = power_input - delta_power
            # Apply power limits and apply
            if power_new > p['Results']['low_power_limit'] and power_new < p['Results']['high_power_limit']:
                set_variable([mbf_device, mbf_vars['NCO2']['gain_scalar']], power_new)

        else:
            # The machine is not in a state for the loop to run so wait and try
            # later['']
            pause(1)
            ## heartbeat code
            if output_lim >100:
                print('*\n')
                output_lim = 1
            else:
                print('*')
                output_lim = output_lim +1



    # --- SCRIPT: run_and_log_emittance_data['m'] ---
    # Run this to record ~500 to 1000 data points of machine operation
    selected_axis = 'x'
    target_sequence = [2['8'], 3, 3['5'], 4, 4['5'], 2['8']]; # Different target steps (pm rad)
    # target_sequence = [8, 10, 7, 9, 8['5'], 8]; # Different target steps (pm rad)
    steps_per_target = 100;               # Steps to hold each target (100 * 0['5s'] = 50s)
    # Pre-allocate logging arrays
    total_steps = len(target_sequence) * steps_per_target
    r_log = zeros(total_steps, 1);  # Reference emittance targets
    y_log = zeros(total_steps, 1);  # Measured emittance (emit)
    u_log = zeros(total_steps, 1);  # Excitation power (gain_scalar)
    time_log = zeros(total_steps, 1)
    [ _2 ,  _1 , pv_names] = mbf_system_config
    mbf_device = pv_names['hardware_names'][''](lower(selected_axis))
    step = 1
    for i  in range( 1, len(target_sequence)):
        target = target_sequence(i)
        print('Setting emittance target to #g pm rad['']['']['']\n', target)
        [r_log_temp, y_log_temp, u_log_temp, time_log_temp] =
            emittance_control_loop(selected_axis, target)
        if i==1:
            r_log = r_log_temp
            y_log = y_log_temp
            u_log = u_log_temp
            time_log = time_log_temp
        else:
            r_log = cat(1, r_log, r_log_temp)
            y_log = cat(1, y_log, y_log_temp)
            u_log = cat(1, u_log, u_log_temp)
            time_log = cat(1, time_log, time_log_temp)

        #     for s = 1:steps_per_target
        #         # Read current machine variables
        #
        #         emit_val  = get_variable(pv_names['emittance'][''](lower(selected_axis))['val'])
        #         power_val = get_variable([mbf_device, pv_names['tails']['NCO2']['gain_scalar']])
        #
        #         # Save into logging vectors
        #         r_log(step) = target
        #         y_log(step) = emit_val
        #         u_log(step) = power_val
        #         time_log(step) = (step - 1) * 0['5']; # 0['5'] sec hardware interval
        #
        #         # Execute original control step (or call original controller)
        #         # [''][''][''] hardware updates 
        #         pause(0['5'])
        #
        #         step = step + 1
        #     end

    # SAVE THE FILE TO DISK:
    save_name = ['emittance_log_data_',selected_axis,'['mat']']
    save(save_name, 'r_log', 'y_log', 'u_log', 'time_log')
    print[['Operating data saved to:, ',save_name, '\n']]
    selected_axis = 'y'
    I10B_closed8 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    I10B_closed12 = emittance_control_loop(selected_axis, 12, 'continual', 'no')
    I10B_closed8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    lcaPut['SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60']
    I10B_phase8 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    I10B_phase12 = emittance_control_loop(selected_axis, 12, 'continual', 'no')
    I10B_phase8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    lcaPut['SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60']
    I10B_open8 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    I10B_open12 = emittance_control_loop(selected_axis, 12, 'continual', 'no')
    I10B_open8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no')
    lcaPut['SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60']
    figure(3)
    hold on
    x1 = linspace(0,300, 600)
    y1 = cat(2,I10B_closed8 ['u_log'], I10B_closed12 ['u_log'], I10B_closed8_2 ['u_log'])
    y2 = cat(2,I10B_open8 ['u_log'], I10B_open12 ['u_log'], I10B_open8_2 ['u_log'])
    y3 = cat(2,I10B_phase8 ['u_log'], I10B_phase12 ['u_log'], I10B_phase8_2 ['u_log'])
    plot(x1, y1)
    plot(x1, y2)
    plot(x1, y3)
    plot(x1, y4)
    hold off
def fll_outer_loop(name):
    # Monitor the FLL lock state and if unlocked re initialise['']
    # name          <EPICS device>:<axis>
    fll_initialisation(name)
    # SR23C-DI-TMBF-01:X:
    #lcaSetMonitor[[name, 'PLL:CTRL:STATUS']]
    while 1 == 1:
        #    lcaNewMonitorWait[[name, 'PLL:CTRL:STATUS']]
        fll_status = get_variable[[name, 'PLL:CTRL:STATUS']]
        if strcmpi(fll_status, 'Stopped'):
            fll_initialisation(name)

        pause(1)

def generate_emittance_database(select_axis, log_data_file):
    # GENERATE_EMITTANCE_DATABASE Builds and formats DD-PID database from recorded data
    #
    # Inputs:
    #   log_data_file : Path to ['mat'] file containing:
    #                   - r_log (target emittance values)
    #                   - y_log (measured emittance values)
    #                   - u_log (excitation power gain values)
    #   output_db_file: Path to save database (e['g'][''] 'emittance_dd_database['mat']')
    #   initial_PID   : [Kp, Ki, Kd] baseline PID gains (e['g'][''] [1e-4, 5e-5, 2e-5])
    #
    # Example:
    #   generate_emittance_database('emittance_log_data['mat']', 'emittance_dd_database['mat']', [1e-4, 5e-5, 2e-5])
    if nargin < 1 || not log_data_file:
        log_data_file = char(strcat('emittance_log_data_',select_axis,'['mat']'))

    # if nargin < 2 || not output_db_file
    output_db_file = char(strcat('emittance_dd_database_',select_axis,'['mat']'))
    # end
    # if nargin < 3 || not initial_PID
    initial_PID = [1e-4, 5e-5, 2e-5]; # Default [Kp, Ki, Kd]
    # end
    # 1[''] Load the recorded log file
    if ~isfile(log_data_file):
        error('File #s not found! Run data collection first['']', log_data_file)

    raw = load(log_data_file)
    r = raw['r_log'](:);  # Target emittance (pm rad or nm rad)
    y = raw['y_log'](:);  # Measured emittance (emit)
    u = raw['u_log'](:);  # Control power (gain_scalar)
    N = len(y)
    print('Processing #d operating data points from #s['']['']['']\n', N, log_data_file)
    # 2[''] Construct Information Vectors phi_bar(j) (Eq[''] 6 of paper)
    # Format: phi_bar(j) = [r(j+1), r(j), y(j), y(j-1), u(j-1)]
    ny = 2; nu = 2
    L = ny + nu + 1; # 5 elements
    DB_phi = zeros(N, L)
    for t  in range( 3, N-1):
        r_lead = r(min(t+1, N))
        r_curr = r(t)
        y_hist = [y(t), y(t-1)]
        u_hist = u(t-1)
        DB_phi[t, :] = [r_lead, r_curr, y_hist, u_hist]

    DB_phi[1:2, :] = repmat(DB_phi[3, :], 2, 1)
    DB_phi[N, :] = DB_phi[N-1, :]
    # 3[''] Initialize PID Gain Database K(j) (Eq[''] 7 of paper)
    DB_K = repmat(initial_PID(:)', N, 1)
    # 4[''] Compute normalization bounds for distance calculation (Eq[''] 8)
    phi_max = max(DB_phi, [], 1)
    phi_min = min(DB_phi, [], 1)
    # 5[''] Save the structured database file
    save(output_db_file, 'DB_phi', 'DB_K', 'phi_max', 'phi_min', 'initial_PID', 'r', 'y', 'u')
    print['Database successfully saved to: #s\n', output_db_file]
    print['Contains:\n']
    print('  - DB_phi : [#d x #d] Information vectors [r(t+1), r(t), y(t), y(t-1), u(t-1)]\n', size(DB_phi,1), size(DB_phi,2))
    print('  - DB_K   : [#d x 3] PID Gains [Kp, Ki, Kd]\n', size(DB_K,1))
    print['  - phi_max, phi_min : Normalization ranges\n\n']

    return power_new 

def id_gap_control(varargin):
    ## MAIN_ID_GAP_CONTROL['M']
    # =========================================================================
    # Function for controlling Insertion Device (ID) gaps via setIDGap['']
    # Features:
    #   1[''] Pre-motion initialization: Option to set all IDs to 100# (open) or 0# (closed)['']
    #   2[''] Sequential Scan: Step ID gaps one by one through 0-20-40-60-80-100-80-60-40-20-0#['']
    #   3[''] Random Motion: Move random IDs to random percentages within their limits['']
    # =========================================================================
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    ## 1[''] USER CONFIGURATION
    # IDs to include in the motion run (default is all 25 IDs)
    ACTIVE_IDS = { 
        'I02',  'J02',  'I03',  'I04',  'J04',  'I05',  
        'I06A', 'I06B', 'I07',  'I08',  'I09',  
        'J09',  'I10A', 'I10B', 'I11',  'I13',  
        'J13',  'I14',  'I16',  'I18',  'I19',  
        'I20',  'I21',  'I22',  'I23',  'I24'   
        }
    # --- GENERAL / MONITORING SETTINGS ---
    # EPICS PVs to monitor at each step (e['g'][''], beam current)[''] Leave {''} if none['']
    MONITOR_PVs = {'SR-DI-DCCT-01:SIGNAL';'SR-DI-EMIT-01:VEMIT'; 'SR-DI-EMIT-01:HEMIT';
        'SR23C-DI-TMBF-01:X:NCO2:GAIN_SCALAR_S'; 'SR23C-DI-TMBF-01:Y:NCO2:GAIN_SCALAR_S';
        'SR01A-PC-SQUAD-04:I';
        'SR23C-DI-TMBF-01:X:PLL:NCO:FREQ_S';'SR23C-DI-TMBF-01:X:PLL:NCO:FREQ';
        'SR23C-DI-TMBF-01:X:PLL:NCO:OFFSET';'SR23C-DI-TMBF-01:X:PLL:FILT:MAG';
        'SR23C-DI-TMBF-01:X:PLL:FILT:PHASE';
        'SR23C-DI-TMBF-01:Y:PLL:NCO:FREQ_S';'SR23C-DI-TMBF-01:Y:PLL:NCO:FREQ';
        'SR23C-DI-TMBF-01:Y:PLL:NCO:OFFSET';'SR23C-DI-TMBF-01:Y:PLL:FILT:MAG';
        'SR23C-DI-TMBF-01:Y:PLL:FILT:PHASE'}
    # --- INITIAL STATE OPTION (Pre-movement conditioning) ---
    # Options:
    #   'open'   -> Set all IDs to 100# (Maximum gap) before starting motion
    #   'closed' -> Set all IDs to 0#   (Minimum gap) before starting motion
    #   'none'   -> Keep current gaps; do not initialize all IDs
    initial_state =  @(x) any(validatestring(x,{'open', 'closed', 'none'}))
    # --- MODE 1: SEQUENTIAL STEP-WISE PATTERN ---
    # --- MODE 2: RANDOM ID & RANDOM PERCENTAGE MOTION ---
    scan_type =  @(x) any(validatestring(x,{'sequential', 'random'}))
    # 'continuous' (any # in [0, 100]) or 'discrete' (0, 20, 40, 60, 80, 100#)
    random_type =  @(x) any(validatestring(x,{'continuous', 'discrete'}))
    valid_number = @(x) isnumeric(x) and isscalar(x) and (x >= 0)
    addParameter(p, 'active_ids', ACTIVE_IDS)
    addParameter(p, 'monitor_pvs', MONITOR_PVs)
    addParameter(p, 'initial_id_state', 'open', initial_state)
    addParameter(p, 'scan_mode', 'sequential', scan_type)
    addParameter(p, 'step_wait', 10['0'], valid_number); # Pause (seconds) after each percentage step or random movement
    addParameter(p, 'random_percent_type', 'continuous', random_type)
    addParameter(p, 'num_random_moves', 15, valid_number)
    parse[p, varargin[:]]
    ## 2[''] Parameters settings and lookups for the IDs
    [ _1 , lookups] = ID_parameters
    ## 3[''] PRE-MOTION INITIALIZATION (ALL 100# OPEN OR 0# CLOSED)
    if ~strcmpi(p['Results']['initial_id_state'], 'none'):
        print('\n>>> [PRE-CONDITIONING] Setting all IDs phases to HORIZONTAL['']['']['']\n')
        # Set any phases to horizontal
        phase_PV = lookups['phases_set'](ID)
        phase_setups = lookups['phases_settings'](ID)
        lcaPutNoWait(phase_PV, phase_setups[1,:]') # The first entry is horizontal

    switch lower(p['Results']['initial_id_state'])
        case 'open'
            print('\n>>> [PRE-CONDITIONING] Setting all IDs to 100## (FULLY OPEN / MAX GAP)['']['']['']\n')
            for k  in range( 1, numel(p['Results']['active_ids'])):
                id_k = p['Results']['active_ids'][k]
                maxGap = lookups['gaps_max'](id_k)
                gap_pv = lookups['gaps_set'](id_k)
                lcaPutNoWait(gap_pv, maxGap)

            print('>>> Please check all active IDs are successfully OPENED\n')
            print('>>> Then press any key to continue\n')
            pause
        case 'closed'
            print('\n>>> [PRE-CONDITIONING] Setting all IDs to 0## (FULLY CLOSED / MIN GAP)['']['']['']\n')
            for k  in range( 1, numel(p['Results']['active_ids'])):
                id_k = p['Results']['active_ids'][k]
                minGap = lookups['gaps_min'](id_k)
                gap_pv = lookups['gaps_set'](id_k)
                lcaPutNoWait(gap_pv, minGap)

            print('>>> Please check all active IDs are successfully CLOSED\n')
            print('>>> Then press any key to continue\n')
            pause
        case 'none'
            print('\n>>> [PRE-CONDITIONING] Skipped (leaving current ID positions intact)['']\n\n')

    if strcmpi(p['Results']['scan_mode'], 'sequential'):
        ## 4[''] PATTERN 1: SEQUENTIAL STEP-WISE SCAN (ONE BY ONE)
        print('\n>>> MODE 1 (SEQUENTIAL SCAN)['']\n')
        #     Determine percentage profile
        if strcmpi(p['Results']['initial_id_state'], 'open'):
            # Start open (100#), close in 20# steps to 0#, then open back to 100#
            pct_steps = [0['80'], 0['60'], 0['40'], 0['20'], 0['00'], 0['20'], 0['40'], 0['60'], 0['80'], 1['00']]
        else:
            # Start closed (0#), open in 20# steps to 100#, then close back to 0#
            pct_steps = [0['20'], 0['40'], 0['60'], 0['80'], 1['00'], 0['80'], 0['60'], 0['40'], 0['20'], 0['00']]

        for k  in range( 6, numel(p['Results']['active_ids'])):
            currID = p['Results']['active_ids'][k]
            minGap = lookups['gaps_min'](currID)
            maxGap = lookups['gaps_max'](currID)
            gapRange = maxGap - minGap
            # Convert percentage trajectory to physical gap values (mm)
            # Formula: Gap = MinGap + Percentage * (MaxGap - MinGap)
            targetGaps = minGap + pct_steps ['']* gapRange
            print('\n--- Moving ID: #s (#d/#d) ---\n', currID, k, numel(p['Results']['active_ids']))
            print['    Min Gap: #['3f'] mm | Max Gap: #['3f'] mm\n', minGap, maxGap]
            print('    Trajectory Steps (#d points):\n    [', numel(targetGaps))
            print('#['2f'] ', targetGaps)
            print('] mm\n')
            # Call setIDGap with the trajectory vector
            scanResults['sequential'][currID]['gapscan'] = setIDGap(currID, targetGaps,
                p['Results']['monitor_pvs'], p['Results']['step_wait'])
            # Saving a file each time an ID completes as the full scan will take a
            # long time and something is likely to go wrong requiring a restart['']
            save(strcat('~/gap_scan', datestr(datetime), '['mat']'), scanResults)

        print('\n>>> SEQUENTIAL STEP-WISE SCAN COMPLETED FOR ALL IDS['']\n\n')
    elif strcmpi(p['Results']['scan_mode'], 'random'):
        ## 5[''] PATTERN 2: RANDOM ID & RANDOM PERCENTAGE MOTION
        print['Total Random Steps to perform: #d\n', p['Results']['num_random_moves']]
        scanResults['randomLog'] = cell(p['Results']['num_random_moves'], 5); # {Step, ID, Pct, TargetGap, MonitorResult}
        for m  in range( 1, p['Results']['num_random_moves']):
            # 1[''] Pick a random ID from p['Results']['active_ids']
            randIDIdx = randi(numel(p['Results']['active_ids']))
            selectedID = p['Results']['active_ids'][randIDIdx]
            # 2[''] Determine random percentage (0# to 100#)
            if strcmpi(p['Results']['random_percent_type'], 'discrete'):
                discreteOptions = [0['0'], 0['20'], 0['40'], 0['60'], 0['80'], 1['00']]
                randPct = discreteOptions(randi(numel(discreteOptions)))
            else:
                randPct = rand(); # Continuous random in [0['0'], 1['0']]

            # 3[''] Calculate target gap in mm
            minGap = gaps_min(selectedID)
            maxGap = gaps_max(selectedID)
            targetGap = minGap + randPct * (maxGap - minGap)
            print('  [Random Move #d/#d] ID: #s | Pct: #5['1f']## | Target Gap: #['4f'] mm\n', 
                m, p['Results']['num_random_moves'], selectedID, randPct * 100, targetGap)
            # 4[''] Call setIDGap for this single random target
            res = setIDGap(selectedID, targetGap, p['Results']['monitor_pvs'], p['Results']['step_wait'])
            # Log record
            scanResults['randomLog'][m][1] = m
            scanResults['randomLog'][m][2] = selectedID
            scanResults['randomLog'][m][3] = randPct * 100
            scanResults['randomLog'][m][4] = targetGap
            scanResults['randomLog'][m][5] = res

        save(strcat('~/gap_scan', datestr(datetime), '['mat']'), scanResults)
        print('\n>>> RANDOM ID MOTION COMPLETED['']\n\n')

    return scanResults 

def mbf_axis_to_name(mbf_axis):
    if strcmpi(mbf_axis, 'x'):
        name = 'SR23C-DI-TMBF-01:X:'
    elif strcmpi(mbf_axis, 'y'):
        name = 'SR23C-DI-TMBF-01:Y:'
    elif strcmpi(mbf_axis, 's'):
        name = 'SR23C-DI-LMBF-01:IQ:'

def mbf_emittance_control(varargin):
    # Starts the emittance control loop using the multibunch feedback system['']
    #   Args:
    #       hemit_target(float): Target value for horizontal emittance (nm rad)
    #       vemit_target(float): Target value for vertical emittance (pm rad)
    #
    # Example: mbf_emittance_control('hemit_target', 3, 'vemit_target', 9)
    [ _3 ,  _2 , pv_names,  _1 ] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    validScalarPosNum = @(x) isnumeric(x) and isscalar(x) and (x > 0)
    p = inputParser
    addParameter(p, 'hemit_target', NaN, validScalarPosNum)
    addParameter(p, 'vemit_target', NaN, validScalarPosNum)
    parse[p,varargin[:]]
    if isnan(p['Results']['hemit_target']) and isnan(p['Results']['vemit_target']):
        print('You need to select either a hemit_target (nm rad), or a vemit_target (pm rad), or both['']')
        return

    if get_variable(pv_names['current']) < 1 #mA:
        print('This needs to be run with beam[''] No changes have been made['']')
        return

    if ~isnan(p['Results']['hemit_target']):
        existing_excitation_x = get_variable([mbf_names['x'], mbf_vars['NCO2']['gain_db']])
        mbf_emittance_setup('x', 'excitation',existing_excitation_x, 'fll_monitor_bunches', 300)
        emittance_control_loop('X', p['Results']['hemit_target'])

    if ~isnan(p['Results']['vemit_target']):
        existing_excitation_y = get_variable([mbf_names['y'], mbf_vars['NCO2']['gain_db']])
        mbf_emittance_setup('y', 'excitation',existing_excitation_y, 'fll_monitor_bunches', 400)
        emittance_control_loop('Y', p['Results']['vemit_target'])

    return name 

def mbf_emittance_scan_frequency(mbf_axis, f_range):
    # Scans the excitation across the requested frequency range, centred on the
    # inital frequency the system is set to['']
    #   Args:
    #       axis(str): 'x' or 'y'
    #       frange(float): the frequency range away from the centre value['']
    #
    #   Returns:
    #       peakfreq(float): the frequency of the highest value of emittance['']
    #
    # Example: peakfreq = mbf_emittance_scan_frequency(axis, f_range)
    mbf_axis = lower(mbf_axis)
    [ _3 ,  _2 , pv_names,  _1 ] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    f_start = get_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']])
    f = linspace(f_start - f_range, f_start + f_range, 50)
    emit = NaN(len(f),1)
    for n  in range( 1, len(f)):
        set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']], f(n))
        pause(['6'])
        emit(n) = get_variable(pv_names['emittance'][mbf_axis])

    set_variable([mbf_names[mbf_axis] mbf_vars['NCO2']['frequency']], f_start)
    [ _1 , m_ind] = max(emit)
    peakfreq = f(m_ind)
    plot(f, emit, peakfreq, emit(m_ind), 'or')
def mbf_emittance_scan_power(mbf_axis, start_power, stop_power, power_step):
    # Scans the excitation across the requested power range
    #   Args:
    #       axis(str): 'x' or 'y'
    #       start_power(float): power in dB[''] Lowest value of the scan['']
    #       stop_power(float): power in dB[''] Highest value of the scan['']
    #       power_step(float): power in dB[''] Step size of the scan['']
    #
    # Example: mbf_emittance_scan_power('X', -50, -10, 5)
    mbf_axis = lower(mbf_axis)
    [ _3 ,  _2 , pv_names,  _1 ] = mbf_system_config
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    p=linspace(start_power,stop_power,((stop_power - start_power) / power_step) +1 )
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']],p(1))
    pause(30)
    emit = NaN(len(p),1)
    for n in range(1, len(p)):
        set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']],p(n))
        pause(['6'])
        emit(n)=get_variable(pv_names['emittance'][mbf_axis])

    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gain_db']],-50)
    plot(p,emit)
    return peakfreq 

def mbf_emittance_setup(mbf_axis, varargin):
    # Sets up the Multibunch feedback system to run a frequency locked loop on a
    # single bunch in each plane[''] The use the tracked frequency to run an
    # oscillator on the sideband of the tune['']
    #   Args:
    #       mbf_axis(str): the axis to do the setup on (x, y, or s)['']
    #       excitation(float): The power of the oscillator in the selected axis (in dB)['']
    #       fll_monitor_bunches(vector of floats): The bunches to be used by the
    #                                                FLL for tune tracking['']
    #       guardbunches(int): The number of bunches around the FLL monitor bunches
    #                            for which the feedback is turned off['']
    #                            This is to reduce distortion of the monitored signal
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
    mbf_axis = lower(mbf_axis)
    [ _1 , harmonic_number, pv_names] = mbf_system_config
    default_excitation = -60; #dB
    default_excitation_pattern = ones(harmonic_number,1)
    default_fll_monitor_bunches=400
    default_guardbunches = 10
    default_harmonic = 10
    # Grab frequencies of left sideband from swept tune fitter
    tunes = get_all_tunes
    leftSB = tunes['']([mbf_axis, '_tune'])['lower_sideband']
    default_excitation_frequency = leftSB
    validScalarNum = @(x) isnumeric(x) and isscalar(x)
    validNum = @(x) isnumeric(x)
    p = inputParser
    addRequired(p, 'mbf_axis')
    addParameter(p, 'excitation', default_excitation, validScalarNum)
    addParameter(p, 'excitation_pattern', default_excitation_pattern)
    addParameter(p, 'fll_monitor_bunches', default_fll_monitor_bunches, validNum)
    addParameter(p, 'guardbunches', default_guardbunches, validScalarNum)
    addParameter(p, 'harmonic', default_harmonic, validScalarNum)
    addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
    parse[p,mbf_axis, varargin[:]]
    mbf_names = pv_names['hardware_names']
    mbf_vars = pv_names['tails']
    if isnan(p['Results']['excitation']):
        excitation_frequency = default_excitation_frequency
    else:
        excitation_frequency = p['Results']['excitation_frequency']

    # initialise FLL on selected bunches['']
    mbf_pll_start(mbf_axis, 'pllbunches',p['Results']['fll_monitor_bunches'],
        'guardbunches',p['Results']['guardbunches'])
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['frequency']], p['Results']['harmonic'] + excitation_frequency)
    ## Setting up the NCO gains and setting the tune sweep to follow the PLL['']
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['PLL_follow']],'Follow')
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['gaindb']],p['Results']['excitation'])
    ## Extracting the bunches the feedback is operating on
    fillx = get_variable([mbf_names[mbf_axis], pv_names['tails']['Bunch_bank']['bank1']['SEQ']['enablewf']])
    ## Applying the same mapping to the NCO and combining it with the user defined pattern
    pattern = and(fillx, p['Results']['excitation_pattern']')
    set_variable([mbf_names[mbf_axis], mbf_vars['Bunch_bank']['bank0']['NCO2']['enablewf']], double(pattern))
    set_variable([mbf_names[mbf_axis], mbf_vars['Bunch_bank']['bank1']['NCO2']['enablewf']], double(pattern))
    ## Switching on the excitation
    set_variable([mbf_names[mbf_axis], mbf_vars['NCO2']['enable']],'On')
    if nargout > 0:
        varargout[1] = pattern
    end#if
