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
    [MBF_PV, tune_pv.left_height];[MBF_PV, tune_pv.right_height]});
AL = sqrt(get_variable([MBF_PV, tune_pv.left_area]));
AR = sqrt(get_variable([MBF_PV, tune_pv.right_area]));
AC = sqrt(get_variable([MBF_PV, tune_pv.centre_area]));
R = (AL + AR) / AC;
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
Q_S = get_variable([MBF_PV, tune_pv.sync_tune]);
sigma_E = get_variable(pv_names.emittance);
chro = s * Q_S / sigma_E;
