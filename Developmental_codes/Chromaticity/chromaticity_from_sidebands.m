function chro=chromaticity_from_sidebands(mbf_axis)
% calculates the chromaticity from the sideband ratios 
% and the emittance measurement.
%
% Args:
%       mbf_axis (int): number representing the axis 1 = 'x' 2 = 'y'.
%
% Example: chro=chromaticity_from_sidebands(1)

[~, ~, pv_names] = mbf_system_config;
MBF_PV = ax2dev(mbf_axis);
AL = sqrt(lcaGet([MBF_PV, pv_names.tails.tune.peak.left_area]));
AR = sqrt(lcaGet([MBF_PV, pv_names.tails.tune.peak.right_area]));
AC = sqrt(lcaGet([MBF_PV, pv_names.tails.tune.peak.centre_area]));
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
Q_S = lcaGet([MBF_PV, pv_names.tails.tune.peak.sync_tune]);
sigma_E = lcaGet(pv_names.emittance);
chro = s * Q_S / sigma_E;
