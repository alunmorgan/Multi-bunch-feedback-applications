    return 

def BPM_FA_get_data(sample_time):
    # Get FA data from all BPMS['']
    #   Args:
    #       sample_time(float): length of time in seconds to return['']
    # The +5 is to give the fast archiver time to deal with the data ingest
    # before requesting it['']
    pause(sample_time + 5)
    BPM_names = fa_id2name[1:173]
    try:
        output = fa_load( convertTo(datetime("now"),'datenum') + [-[sample_time +5)['']/60['']/60['']/24 -5['']/60['']/60['']/24], 1:173]
    except:
        pause(5)
        output = fa_load( convertTo(datetime("now"),'datenum') + [-[sample_time +5)['']/60['']/60['']/24 -5['']/60['']/60['']/24], 1:173]

    output['bpm_names'] = BPM_names
    output['X'] = squeeze(output['data'][1,:,:])
    output['Y'] = squeeze(output['data'][2,:,:])
    if size(output['data'],3)< 10000 * sample_time:
        print('Did not get a full set of data[''] Trying again['']['']['']')
        output = BPM_FA_get_data(sample_time)

def BPM_FA_plot_data(data):
    # Plot the data returned from get_BPM_FA_data['']
    timescale = (data['t'] - data['t'](1)) * 24 * 3600
    figure
    subplot(2,1,1)
    plot(timescale,data['X'])
    title('BPM FA data')
    xlabel('Time(s)')
    ylabel('X Position (nm)')
    subplot(2,1,2)
    plot(timescale, data['Y'])
    xlabel('Time(s)')
    ylabel('Y Position (nm)')
    Xrel = data['X'][:,:] - data['X'](:,1)
    Yrel = data['Y'][:,:] - data['Y'](:,1)
    figure
    subplot(2,1,1)
    plot(timescale, Xrel)
    title('BPM FA data (relative movement)')
    xlabel('Time(s)')
    ylabel('X Position (nm)')
    subplot(2,1,2)
    plot(timescale, Yrel)
    xlabel('Time(s)')
    ylabel('Y Position (nm)')
    fx = spectra(timescale,Xrel')
    fy = spectra(timescale,Yrel')
    figure
    subplot(2,1,1)
    plot(fx['frequency'] * 1E-3, fx['dft_y'])
    title('BPM FA data (FFT)')
    xlabel('Frequency (kHz)')
    ylabel('X Position (nm)')
    subplot(2,1,2)
    plot(fy['frequency'] * 1E-3, fy['dft_y'])
    xlabel('Frequency (kHz)')
    ylabel('Y Position (nm)')
    return output 

def BPM_FR_get_data_XY_only(bpm_list):
    # Captures 2048 turns of data
    for n  in range( 1, len(bpm_list)):
        bpm_name = bpm_list[n]
        bpm_label = regexprep(bpm_name, '-', '_')
        for tk  in range( 1, 10):
            try:
                BPM_data_temp = get_variable[{[bpm_name, ':FR:WFX'];[bpm_name, ':FR:WFY'];}]
                output[bpm_label]['X'] = BPM_data_temp[1, :]
                output[bpm_label]['Y'] = BPM_data_temp[2, :]
                print('['']')
                break
            except:
                print(['Failed to get BPM Free run data for, ', bpm_name])



    return output 

def BPM_FT_get_data_XY_only(bpm_list):
    BPM_FT_data = NaN(len(bpm_list), 2)
    for n  in range( 1, len(bpm_list)):
        bpm_name = bpm_list[n]
        bpm_label = regexprep(bpm_name, '-', '_')
        for tk  in range( 1, 10):
            try:
                BPM_data_temp = get_variable({
                    [bpm_name, ':FT:WFX'];
                    [bpm_name, ':FT:WFY'];
                    })
                BPM_FT_data(n, 1:size(BPM_data_temp,1), 1:size(BPM_data_temp,2)) = BPM_data_temp
                output[bpm_label]['X'] = squeeze(BPM_data_temp[1, :])
                output[bpm_label]['Y'] = squeeze(BPM_data_temp[2, :])
                print('['']')
                break
            except:
                print(['Failed to get BPM first turn data for, ', bpm_name])



    return output 

def BPM_SA_get_data(bpm_list, varargin):
    # Defaults to X and Y waveforms, ABCD, Q and current can be added
    # with the flag 'all_channels'
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    boolean_string = {'yes', 'no'}
    addRequired(p, 'bpm_list')
    addParameter(p, 'n_samples', 30)
    addParameter(p, 'all_channels', 'no', @(x) any(validatestring(x, boolean_string)))
    parse[p, bpm_list, varargin[:]]
    n_bpms = len(bpm_list)
    for n  in range[ n_bpms:-1, 1]:
        for jsp  in range[ p['Results']['n_samples']:-1, 1]:
            bpm_name = bpm_list[n]
            bpm_label = regexprep(bpm_name, '-', '_')
            BPM_data_temp = get_variable({char(strcat[bpm_name, ':SA:X']); 
                char(strcat[bpm_name, ':SA:Y'])})
            output[bpm_label]['X'](jsp) = squeeze(BPM_data_temp(1))
            output[bpm_label]['Y'](jsp) = squeeze(BPM_data_temp(2))
            if strcmp(p['Results']['all_channels'], 'yes'):
                BPM_data_temp_add = get_variable({char(strcat[bpm_name, ':SA:Q']);
                    char(strcat[bpm_name, ':SA:CURRENT']);
                    char(strcat[bpm_name, ':SA:A']);
                    char(strcat[bpm_name, ':SA:B']);
                    char(strcat[bpm_name, ':SA:C']);
                    char(strcat[bpm_name, ':SA:D'])})
                output[bpm_label]['Q'](jsp) = squeeze(BPM_data_temp_add(1))
                output[bpm_label]['CURRENT'](jsp) = squeeze(BPM_data_temp_add(2))
                output[bpm_label]['A'](jsp) = squeeze(BPM_data_temp_add(3))
                output[bpm_label]['B'](jsp) = squeeze(BPM_data_temp_add(4))
                output[bpm_label]['C'](jsp) = squeeze(BPM_data_temp_add(5))
                output[bpm_label]['D'](jsp) = squeeze(BPM_data_temp_add(6))



    return output 

def BPM_TbT_analyse_data(data_path):
    load(data_path, 'output')
    print('')
    bpms = fields(output)
    summary['bpms'] = bpms
    buttons = {'A', 'B', 'C', 'D'}
    for ewhs  in range( 1, len(bpms)):
        summary['meanx'](ewhs) = output[bpms[ewhs]]['meanx']
        summary['meany'](ewhs) = output[bpms[ewhs]]['meany']
        summary['stdx'](ewhs) = output[bpms[ewhs]]['stdx']
        summary['stdy'](ewhs) = output[bpms[ewhs]]['stdy']
        summary['minx'](ewhs) = output[bpms[ewhs]]['minx']
        summary['miny'](ewhs) = output[bpms[ewhs]]['miny']
        summary['maxx'](ewhs) = output[bpms[ewhs]]['maxx']
        summary['maxy'](ewhs) = output[bpms[ewhs]]['maxy']
        for dsw  in range( 1, len(buttons)):
            summary[''](['mean', buttons[dsw]])(ewhs) = mean(output[bpms[ewhs]][buttons[dsw]])
            summary[''](['std', buttons[dsw]])(ewhs) = std(output[bpms[ewhs]][buttons[dsw]])
            summary[''](['min', buttons[dsw]])(ewhs) = min(output[bpms[ewhs]][buttons[dsw]])
            summary[''](['max', buttons[dsw]])(ewhs) = max(output[bpms[ewhs]][buttons[dsw]])


    return summary 

def BPM_TbT_capture(bpm_list, capture_length):
    #sets up and arms a turn by turn capture on the requested set of BPMs['']
    # the BPMs will trigger on the next hardware trigger['']
    # the output is then captured into a structure['']
    # use fa_id2name to pregenerate a list of BPM names['']
    #
    # Example: output = BPM_TbT_capture({'SR01C-DI-EBPM-01', 'SR01C-DI-EBPM-02'}, 1000)
    BPM_TbT_capture_setup(bpm_list, capture_length)
    BPM_TbT_capture_arm(bpm_list)
    pause(0['2'])
    output = BPM_TbT_get_data(bpm_list, capture_length,
        'capture_stats', 'yes', 'all_waveforms', 'yes')
    print('\n')
def BPM_TbT_capture_arm(bpm_list):
    for n  in range( len[bpm_list):-1, 1]:
        BPM_name = bpm_list[n]
        BPM_names[n][1] = [BPM_name, ':TT:ARM']

    set_variable(BPM_names, 1)
def BPM_TbT_capture_setup(bpm_list, capture_length):
    for n  in range( 1, len(bpm_list)):
        BPM_name = bpm_list[n]
        set_variable[[BPM_name, ':TT:DELAY_S'], 0]
        set_variable[[BPM_name, ':TT:OFFSET_S'], 0]
        set_variable[[BPM_name, ':TT:CAPLEN_S'], capture_length]; # Turns
        set_variable[[BPM_name, ':TT:LENGTH_S'], capture_length]; # Turns

    return output 

def BPM_TbT_get_data(bpm_list, capture_length, varargin):
    # Defaults to X and Y waveforms, ABCD and procomputed statistics can be added
    # with the flags 'all_waveforms' and 'capture_stats'
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    boolean_string = {'yes', 'no'}
    addRequired(p, 'bpm_list')
    addRequired(p, 'capture_length')
    addParameter(p, 'xy_waveforms', 'yes', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'all_waveforms', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'capture_stats', 'no', @(x) any(validatestring(x, boolean_string)))
    addParameter(p, 'n_trys', 5)
    parse[p, bpm_list, capture_length,  varargin[:]]
    update_tick = 1
    n_trys = p['Results']['n_trys']
    for n  in range( 1, len(bpm_list)):
        bpm_name = bpm_list[n]
        bpm_label = regexprep(bpm_name, '-', '_')
        fail_tick = 0
        for tk  in range( 1, n_trys):
            try:
                if strcmp(p['Results']['xy_waveforms'], 'yes'):
                    BPM_data_temp = get_variable[{[bpm_name, ':TT:WFX']; [bpm_name, ':TT:WFY']}]
                    output[bpm_label]['X'] = BPM_data_temp[1,1:capture_length]
                    output[bpm_label]['Y'] = BPM_data_temp[2,1:capture_length]


                if strcmp(p['Results']['all_waveforms'], 'yes'):
                    bpm_data_temp = get_variable({[bpm_name, ':TT:WFS'];
                        [bpm_name, ':TT:WFA']; [bpm_name, ':TT:WFB'];
                        [bpm_name, ':TT:WFC']; [bpm_name, ':TT:WFD']});
                        output[bpm_label]['intensity'] = bpm_data_temp[1,1:capture_length]
                    output[bpm_label]['A'] = bpm_data_temp[2,1:capture_length]
                    output[bpm_label]['B'] = bpm_data_temp[3,1:capture_length]
                    output[bpm_label]['C'] = bpm_data_temp[4,1:capture_length]
                    output[bpm_label]['D'] = bpm_data_temp[5,1:capture_length]


                # Statistics of waveforms
                if strcmp(p['Results']['capture_stats'], 'yes'):
                    bpm_stats_temp = get_variable({[bpm_name, ':TT:MEANX'];
                        [bpm_name, ':TT:MEANY']; [bpm_name, ':TT:STDX'];
                        [bpm_name, ':TT:STDY']; [bpm_name, ':TT:MINX'];
                        [bpm_name, ':TT:MINY']; [bpm_name, ':TT:MAXX'];
                        [bpm_name, ':TT:MAXY']})
                    output[bpm_label]['meanx'] = bpm_stats_temp[1,:]
                    output[bpm_label]['meany'] = bpm_stats_temp[2,:]
                    output[bpm_label]['stdx'] = bpm_stats_temp[3,:]
                    output[bpm_label]['stdy'] = bpm_stats_temp[4,:]
                    output[bpm_label]['minx'] = bpm_stats_temp[5,:]
                    output[bpm_label]['miny'] = bpm_stats_temp[6,:]
                    output[bpm_label]['maxx'] = bpm_stats_temp[7,:]
                    output[bpm_label]['maxy'] = bpm_stats_temp[8,:]


                print('['']')
                update_tick = update_tick + 1
                if rem(update_tick, 50) == 0:
                    print('\n')

                break
            except ME:
                print(['\nRetrying to get BPM TbT data for ', bpm_name, '(', ME['identifier'], ')'])
                fail_tick = fail_tick + 1


        if fail_tick == n_trys:
            print(['\nFailed to get BPM TbT data for, ', bpm_name, '\n'])


def BPM_set_switching_off(nbpms):
    for n  in range( 1, len(nbpms)):
        BPM_name = fa_id2name(nbpms(n))
        set_variable[[BPM_name, ':CF:AUTOSW_S'], 'Manual']

def BPM_set_switching_on(nbpms):
    for n  in range( 1, len(nbpms)):
        BPM_name = fa_id2name(nbpms(n))
        set_variable[[BPM_name, ':CF:AUTOSW_S'], 'Automatic']

    return output 

def generate_ebpm_list:
    ebpm_list =[]
    for cell  in range( 1, 24):
        cell_name = compose("#02u", cell)
        for position  in range( 1, 7):
            ebpm_list{end +1} = strcat('SR',cell_name,'C-DI-EBPM-0',(position))


    current = lcaGet['SR-DI-DCCT-01:SIGNAL']
    ebpm_list = generate_ebpm_list
    output = BPM_SA_get_data(ebpm_list, 'all_channels', 'yes')
    for n  in range( 1, len(ebpm_list)):
        scale_names[n] = char(strcat[ebpm_list[n], ':CF:ISCALE_S'])

    ebpm_scales = lcaGet(scale_names')
    for hww  in range( 1, len(ebpm_list)):
        fractional_errors(hww,1) = mean(output[''](regexprep(ebpm_list[hww], '-', '_'))['CURRENT'] ['']/ current)
        new_scales(hww,1) = ebpm_scales(hww) *fractional_errors(hww,1)

    # for js  = 1:len(ebpm_list)
    # lcaPut(scale_names[js], new_scales(js))
    # end
