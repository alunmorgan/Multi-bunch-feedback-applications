function beam_info = get_beamsize_from_image(image)
%takes the provided image structure and performs a 2D gaussian fit over the
%image. Returns correctly scaled sigmas and centres.

image_x = linspace(image.xmin, image.xmax, image.width);
image_y = linspace(image.ymin, image.ymax, image.height);
[xData, yData, zData] = prepareSurfaceData(image_x, image_y, image.image);

pixel_max = 255;
sigma_min = 1E-6; %assuming mm
sigma_max = 1; %assuming mm
% Set up fittype and options.
ft = fittype( 'background + height.*exp(-((((x-centrex).*cos(rho) - (y-centrey).*sin(rho))./sigmax).^2 + (((x-centrex).*sin(rho) + (y-centrey).*cos(rho))./sigmay).^2)./2)', 'independent', {'x', 'y'}, 'dependent', 'z' );
opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
opts.Display = 'notify';%'Off';
opts.Lower = [0 image.xmin image.ymin 0 0 sigma_min sigma_min];
opts.StartPoint = [0 image.xmax - (image.xmax-image.xmin)./2 image.ymax - (image.ymax-image.ymin)./2 max(max(image.image)) 0 0.01 0.01];
opts.Upper = [pixel_max image.xmax image.ymax pixel_max * 2 6.28 sigma_max sigma_max];
opts.TolFun = 1E-9;
opts.TolX = 1E-9;
opts.MaxFunEvals = 1200;

% Fit model to data.
[beam_info.fitresult, beam_info.fit_quality] = fit( [xData, yData], zData, ft, opts );
coeff_names = coeffnames(beam_info.fitresult);
coeff_values = coeffvalues(beam_info.fitresult);
for tk = 1:length(coeff_names)
    beam_info.(coeff_names{tk}) = coeff_values(tk);
end %for

% % Create a figure for the plots.
% figure( 'Name', '2D gaussian fit' );
% 
% % Plot fit with data.
% subplot( 2, 2, 1 );
% h = plot( beam_info.fitresult);
% title('Fit')
% xlabel( 'X', 'Interpreter', 'none' );
% ylabel( 'Y', 'Interpreter', 'none' );
% zlabel( 'Intensity', 'Interpreter', 'none' );
% grid off
% shading interp
% view(2);
% axis tight
% 
% subplot( 2, 2, 2 );
% h = scatter3(xData, yData, zData , 5, zData);
% title('Data')
% xlabel( 'X', 'Interpreter', 'none' );
% ylabel( 'Y', 'Interpreter', 'none' );
% zlabel( 'Intensity', 'Interpreter', 'none' );
% grid off
% view(2);
% axis tight
% 
% % Plot residuals.
% subplot( 2, 2, 3 );
% h = plot( beam_info.fitresult, [xData, yData], zData, 'Style', 'Residuals' );
% title('Residuals')
% xlabel( 'X', 'Interpreter', 'none' );
% ylabel( 'Y', 'Interpreter', 'none' );
% zlabel( 'Error', 'Interpreter', 'none' );
% grid off
% view( 2);
% shading interp
% axis tight
% 
% for hd = 1:length(coeff_names)
%     info{hd} = [coeff_names{hd}, ' = ', num2str(coeff_values(hd))];
% end %for
% dim = [.58 .12 .3 .3];
% annotation('textbox',dim,'String',info,'FitBoxToText','on');



