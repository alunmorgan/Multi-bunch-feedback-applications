    return 

def beamsize_get_data:
    beam_sizes['P1_sigx'] = get_variable['SR-DI-EMIT-01:P1:SIGMAX_MEAN']
    beam_sizes['P1_sigy'] = get_variable['SR-DI-EMIT-01:P1:SIGMAY_MEAN']
    beam_sizes['P2_sigx'] = get_variable['SR-DI-EMIT-01:P2:SIGMAX_MEAN']
    beam_sizes['P2_sigy'] = get_variable['SR-DI-EMIT-01:P2:SIGMAY_MEAN']
    beam_sizes['P3_sigx'] = get_variable['SR-DI-EMIT-02:P1:SIGMAX_MEAN']
    beam_sizes['P3_sigy'] = get_variable['SR-DI-EMIT-02:P1:SIGMAY_MEAN']
    return beam_sizes 

def beamsize_get_from_image(image):
    #takes the provided image structure and performs a 2D gaussian fit over the
    #image[''] Returns correctly scaled sigmas and centres['']
    image_x = linspace(image['xmin'], image['xmax'], image['width'])
    image_y = linspace(image['ymax'], image['ymin'], image['height'])
    # [xData, yData, zData] = prepareSurfaceData(image_x, image_y, image['image'])
    [xData, yData] = meshgrid(image_x,image_y)
    zData =image['image']
    zData = remove_spikes_from_image(zData, 40)
    figure(1); surf(xData, yData, zData, 'EdgeColor','none')
    pixel_max = 255
    centrex_min = image['xmin']; #in mm
    centrex_max = image['xmax']; #in mm
    centrey_min = image['ymin']; #in mm
    centrey_max = image['ymax']; #in mm
    # Set up fittype and options['']
    ft = fittype( 'background + height ['']* exp(-A*(x-centrex)['']^2 - B*(y-centrey)['']^2 - C*(x-centrex)*(y-centrey))',
        'independent', {'x', 'y'}, 'dependent', 'z' , 'coefficients', {'background', 'centrex', 'centrey', 'height', 'A', 'B', 'C';})
    opts = fitoptions( 'Method', 'NonlinearLeastSquares' )
    opts['Display'] = 'notify';#'Off'
    opts['Lower'] = [0, centrex_min, centrey_min, 0, -10000, -10000, -10000]
    opts['StartPoint'] = [0 0 0 230  0['01'] 0['01'] 0['01']]
    opts['Upper'] = [pixel_max, centrex_max, centrey_max, pixel_max, *, 2, 10000, 10000, 10000]
    opts['TolFun'] = 1E-9
    opts['TolX'] = 1E-9
    opts['MaxFunEvals'] = 1200
    # Fit model to data['']
    [beam_info['fitresult'], beam_info['fit_quality']] = fit( [xData(:), yData(:)], zData(:), ft, opts )
    figure(2);plot(beam_info['fitresult'] )
    coeff_names = coeffnames(beam_info['fitresult'])
    coeff_values = coeffvalues(beam_info['fitresult'])
    for tk  in range( 1, len(coeff_names)):
        beam_info[coeff_names[tk]] = coeff_values(tk)

    return beam_info 

def emittance_get_data:
    emittance['emit'] = get_variable['SR-DI-EMIT-01:EMITTANCE_MEAN']
    emittance['coupling'] = get_variable['SR-DI-EMIT-01:COUPLING_MEAN']
    emittance['espread'] = get_variable['SR-DI-EMIT-01:ESPREAD_MEAN']
    emittance['hemit'] = get_variable['SR-DI-EMIT-01:HEMIT_MEAN']
    emittance['veimt'] = get_variable['SR-DI-EMIT-01:VEMIT_MEAN']
    emittance['herror'] = get_variable['SR-DI-EMIT-01:HERROR_MEAN']
    emittance['verror'] = get_variable['SR-DI-EMIT-01:VERROR_MEAN']
    return emittance 

def pinhole_get_data_after_trigger(channel):
    # The camera image PV always returns the maximum size regardless of
    # settings[''] So set the selection area to max so that all of the scale
    # values match['']
    original_imagewidth = get_variable[[channel ':IMAGEWIDTH']]
    set_variable[[channel ':IMAGEWIDTH'], 1024]
    image_pv =[channel, ':PROXY:DATA']
    lcaSetMonitor(image_pv)
    lcaNewMonitorWait(image_pv) # initial data
    lcaNewMonitorWait(image_pv) # experimental data
    [image['image'], image['timestamp']] = get_variable(image_pv,0,'byte')
    im_temp = get_variable({[channel ':WIDTH'];
        [channel ':HEIGHT'];
        [channel ':XSCALEMAX'];
        [channel ':XSCALEMIN'];
        [channel ':YSCALEMAX'];
        [channel ':YSCALEMIN']})
    neg=find(image['image'] < 0)
    image['image'](neg)=256 + image['image'](neg)
    image['width'] = squeeze(im_temp[1, :])
    image['height'] = squeeze(im_temp[2, :])
    image['xmax'] = squeeze(im_temp[3, :])
    image['xmin'] = squeeze(im_temp[4, :])
    image['ymax'] = squeeze(im_temp[5, :])
    image['ymin'] = squeeze(im_temp[6, :])
    # Restore to original slection size['']
    set_variable[[channel ':IMAGEWIDTH'], original_imagewidth]
    image['image'] = reshape(image['image'], image['width'], image['height'])['']'
    return image 

def pinhole_get_image(channel, varargin):
    # Returns the current image from the camera along with size, timestamp and
    # scaling values['']
    default_gamma_correction = 0['097']
    p = inputParser
    p['StructExpand'] = false
    p['CaseSensitive'] = false
    valid_number = @(x) isnumeric(x)
    addRequired(p, 'channel')
    addParameter(p, 'gamma_correction', default_gamma_correction, valid_number)
    parse[p, channel, varargin[:]]
    image['imagewidth'] = get_variable[[channel ':IMAGEWIDTH']]
    [image['image'], image['timestamp']] = get_variable[[channel ':PROXY:DATA'],0,'byte']
    neg=find(image['image'] < 0)
    image['image'](neg)=256 + image['image'](neg)
    image['width'] = get_variable[[channel ':WIDTH']]
    image['height'] = get_variable[[channel ':HEIGHT']]
    image['xmax'] = get_variable[[channel ':XSCALEMAX']]
    image['xmin'] = get_variable[[channel ':XSCALEMIN']]
    image['ymax'] = get_variable[[channel ':YSCALEMAX']]
    image['ymin'] = get_variable[[channel ':YSCALEMIN']]
    # The PV returns the full image regardless of settings['']
    # Remove zero padding
    image['image'] = image['image'][1:image['height']*image['width']]
    image['image'] = reshape(image['image'], image['width'], image['height'])['']'
    # gamma correction
    image['image'] = image['image'] ['']* 
        exp(p['Results']['gamma_correction'] * (image['image'] / 255 - 1))
    # this appears to give the best correction
    return image 

def pinhole_get_settings:
    pinhole_settings['P1_betax'] = get_variable['SR-DI-EMIT-01:P1:BETAX']
    pinhole_settings['P1_betay'] = get_variable['SR-DI-EMIT-01:P1:BETAY']
    pinhole_settings['P2_betax'] = get_variable['SR-DI-EMIT-01:P2:BETAX']
    pinhole_settings['P2_betay'] = get_variable['SR-DI-EMIT-01:P2:BETAY']
    pinhole_settings['P1_printx'] = get_variable['SR-DI-EMIT-01:P1:ETAX']
    pinhole_settings['P1_printy'] = get_variable['SR-DI-EMIT-01:P1:ETAY']
    pinhole_settings['P2_printx'] = get_variable['SR-DI-EMIT-01:P2:ETAX']
    pinhole_settings['P2_printy'] = get_variable['SR-DI-EMIT-01:P2:ETAY']
    pinhole_settings['P1_psf'] = get_variable['SR-DI-EMIT-01:P1:DELTA']
    pinhole_settings['P2_psf'] = get_variable['SR-DI-EMIT-01:P2:DELTA']
    pinhole_settings['P3_psf'] = get_variable['SR-DI-EMIT-02:P1:DELTA']
    pinhole_settings['P1_cam_mag'] = get_variable['SR-DI-EMIT-01:P1:MAG']
    pinhole_settings['P2_cam_mag'] = get_variable['SR-DI-EMIT-01:P2:MAG']
    pinhole_settings['P3_cam_mag'] = get_variable['SR-DI-EMIT-02:P1:MAG']
    pinhole_settings['P1_dsource'] = get_variable['SR-DI-EMIT-01:P1:DSOURCE']
    pinhole_settings['P1_dimage'] = get_variable['SR-DI-EMIT-01:P1:DIMAGE']
    pinhole_settings['P2_dsource'] = get_variable['SR-DI-EMIT-01:P2:DSOURCE']
    pinhole_settings['P2_dimage'] = get_variable['SR-DI-EMIT-01:P2:DIMAGE']
    pinhole_settings['P3_dsource'] = get_variable['SR-DI-EMIT-02:P1:DSOURCE']
    pinhole_settings['P3_dimage'] = get_variable['SR-DI-EMIT-02:P1:DIMAGE']
def pinhole_plot_fit(beam_info):
    # Create a figure for the plots['']
    figure( 'Name', '2D gaussian fit' )
    # Plot fit with data['']
    subplot( 2, 2, 1 )
    plot( beam_info['fitresult'])
    title('Fit')
    xlabel( 'X', 'Interpreter', 'none' )
    ylabel( 'Y', 'Interpreter', 'none' )
    zlabel( 'Intensity', 'Interpreter', 'none' )
    grid off
    shading interp
    view(2)
    axis tight
    subplot( 2, 2, 2 )
    scatter3(xData, yData, zData , 5, zData)
    title('Data')
    xlabel( 'X', 'Interpreter', 'none' )
    ylabel( 'Y', 'Interpreter', 'none' )
    zlabel( 'Intensity', 'Interpreter', 'none' )
    grid off
    view(2)
    axis tight
    # Plot residuals['']
    subplot( 2, 2, 3 )
    plot( beam_info['fitresult'], [xData, yData], zData, 'Style', 'Residuals' )
    title('Residuals')
    xlabel( 'X', 'Interpreter', 'none' )
    ylabel( 'Y', 'Interpreter', 'none' )
    zlabel( 'Error', 'Interpreter', 'none' )
    grid off
    view( 2)
    shading interp
    axis tight
    pinhole_info = cell(len(coeff_names),1)
    for hd  in range( 1, len(coeff_names)):
        pinhole_info[hd] = [coeff_names[hd], ' = ', (coeff_values(hd))]

    dim = [['58'] ['12'] ['3'] ['3']]
    annotation('textbox',dim,'String',pinhole_info,'FitBoxToText','on')
def pinhole_plot_image(image):
    # setting up a new colormap
    jet1=jet
    jet1[1:8,3]=linspace(0,1,8)['']'
    jet1[end,1:3]=[1, 1 1]
    figure
    imagesc(linspace(image['xmin'],image['xmax'],image['height']),
        linspace(image['ymax'],image['ymin'],image['width']),
        image['image'])
    axis image
    set(gca,'YDir','normal')
    colormap(jet1)
    return pinhole_settings 

def remove_spikes_from_image(data, threshold):
    # remove the single point spikes in an image[''] replaces them with the average
    # value of surrounding pixels['']
    # data is a 2D array
    # threshold is the difference between the sample and the surounding values (in
    # pixels)
    #
    # example:  cleaned_data = remove_spikes_from_image(data, threshold, it)
    if nargin == 1:
        error['RemoveSpikesFromImage:IOError', 'Need to put in a threshold level']

    cleaned_data = data
    # for each point calculate the difference between it and the adjacent points
    for sje  in range( 2, size(data,1)-2):
        for hsew  in range( 2, size(data,2)-2):
            diff1 = data(sje, hsew) - data(sje-1, hsew)
            diff2 = data(sje, hsew) - data(sje+1, hsew)
            diff3 = data(sje, hsew) - data(sje, hsew-1)
            diff4 = data(sje, hsew) - data(sje, hsew+1)
            if diff1 > threshold and diff2 > threshold and diff3 > threshold and diff4 > threshold:
                cleaned_data(sje, hsew) = (data(sje-1, hsew)+ data(sje+1, hsew) + data(sje, hsew-1) + data(sje, hsew+1)) ['']/ 4


