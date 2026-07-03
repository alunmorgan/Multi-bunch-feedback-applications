function chro=chromaticity_from_sidebands(mbf_axis)
% calculates the chromaticity from the sideband ratios 
% and the emittance measurement.
%
% Args:
%       mbf_axis (str): 'x' or 'y'.
%
% Example: chro=chromaticity_from_sidebands(1)

[~, ~, pv_names] = mbf_system_config;
MBF_PV = pv_names.hardware_names.(mbf_axis);
tune_pv = pv_names.tails.tune;
vars = get_variable({[MBF_PV, tune_pv.centre_width]; [MBF_PV, tune_pv.left_width];...
    [MBF_PV, tune_pv.right_width];[MBF_PV, tune_pv.centre_height];...
    [MBF_PV, tune_pv.left_height];[MBF_PV, tune_pv.right_height];...
    [MBF_PV, tune_pv.sync_tune]; pv_names.emittance.(mbf_axis).mean});
centre_width = vars(1);
left_width = vars(2);
right_width = vars(3);
centre_height = vars(4);
left_height = vars(5);
right_height = vars(6);
Q_S = vars(7);
sigma_E = vars(8);
% Generate a Lorentz curve using the width and scale the height to match the
% measurement. The area will scale with the hight and before scaling is 1 by
% definition.
centre_area = centre_height ./ max((1/pi) .* ((0.5 .* centre_width) ./ ([-1:centre_width/10:1].^2 + (0.5 .* centre_width).^2)));
left_area = left_height ./ max((1/pi) .* ((0.5 .* left_width) ./ ([-1:left_width/10:1].^2 + (0.5 .* left_width).^2)));
right_area = right_height ./ max((1/pi) .* ((0.5 .* right_width) ./ ([-1:right_width/10:1].^2 + (0.5 .* right_width).^2)));

R = (sqrt(left_area) + sqrt(right_area)) / sqrt(centre_area);
if R < .25
    % If the combined area of the sidebands is less than 25% of the area of
    % the main peak, do this.
      s=sqrt(R);
else
      s = 9.2893*R^9 - ...
          84.038*R^8 + ...
          326.95*R^7 - ...
          714.77*R^6 + ...
          963.33*R^5 - ...
          826.25*R^4 + ...
          449.24*R^3 - ...
          149.08*R^2 + ...
          28.222*R - ...
          1.8186;
end

chro = s * Q_S / sigma_E;
