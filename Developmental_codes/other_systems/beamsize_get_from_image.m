function beam_info = get_beamsize_from_image(image)
%takes the provided image structure and performs a 2D gaussian fit over the
%image. Returns correctly scaled sigmas and centres.

image_x = linspace(image.xmin, image.xmax, image.width);
image_y = linspace(image.ymax, image.ymin, image.height);
% [xData, yData, zData] = prepareSurfaceData(image_x, image_y, image.image);
[xData, yData] = meshgrid(image_x,image_y);
zData =image.image;
zData = remove_spikes_from_image(zData, 40);
figure(1); surf(xData, yData, zData, 'EdgeColor','none')
pixel_max = 255;
centrex_min = image.xmin; %in mm
centrex_max = image.xmax; %in mm
centrey_min = image.ymin; %in mm
centrey_max = image.ymax; %in mm
% Set up fittype and options.
ft = fittype( 'background + height .* exp(-A*(x-centrex).^2 - B*(y-centrey).^2 - C*(x-centrex)*(y-centrey))',...
    'independent', {'x', 'y'}, 'dependent', 'z' , 'coefficients', {'background', 'centrex', 'centrey', 'height', 'A', 'B', 'C';});
opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
opts.Display = 'notify';%'Off';
opts.Lower = [0 centrex_min centrey_min 0 -10000 -10000 -10000];
opts.StartPoint = [0 0 0 230  0.01 0.01 0.01];
opts.Upper = [pixel_max centrex_max centrey_max pixel_max * 2 10000, 10000, 10000];
opts.TolFun = 1E-9;
opts.TolX = 1E-9;
opts.MaxFunEvals = 1200;

% Fit model to data.
[beam_info.fitresult, beam_info.fit_quality] = fit( [xData(:), yData(:)], zData(:), ft, opts );
figure(2);plot(beam_info.fitresult );
coeff_names = coeffnames(beam_info.fitresult);
coeff_values = coeffvalues(beam_info.fitresult);
for tk = 1:length(coeff_names)
    beam_info.(coeff_names{tk}) = coeff_values(tk);
end %for



