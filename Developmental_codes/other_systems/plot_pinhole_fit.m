function plot_pinhole_fit(beam_info)
% Create a figure for the plots.
figure( 'Name', '2D gaussian fit' );

% Plot fit with data.
subplot( 2, 2, 1 );
plot( beam_info.fitresult);
title('Fit')
xlabel( 'X', 'Interpreter', 'none' );
ylabel( 'Y', 'Interpreter', 'none' );
zlabel( 'Intensity', 'Interpreter', 'none' );
grid off
shading interp
view(2);
axis tight

subplot( 2, 2, 2 );
scatter3(xData, yData, zData , 5, zData);
title('Data')
xlabel( 'X', 'Interpreter', 'none' );
ylabel( 'Y', 'Interpreter', 'none' );
zlabel( 'Intensity', 'Interpreter', 'none' );
grid off
view(2);
axis tight

% Plot residuals.
subplot( 2, 2, 3 );
plot( beam_info.fitresult, [xData, yData], zData, 'Style', 'Residuals' );
title('Residuals')
xlabel( 'X', 'Interpreter', 'none' );
ylabel( 'Y', 'Interpreter', 'none' );
zlabel( 'Error', 'Interpreter', 'none' );
grid off
view( 2);
shading interp
axis tight
pinhole_info = {};
for hd = 1:length(coeff_names)
    pinhole_info{hd} = [coeff_names{hd}, ' = ', num2str(coeff_values(hd))];
end %for
dim = [.58 .12 .3 .3];
annotation('textbox',dim,'String',pinhole_info,'FitBoxToText','on');
