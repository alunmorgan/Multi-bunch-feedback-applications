function td = mbf_transverse_damping_capture(mbf_axis)
pinhole_trig_orig = lcaGet('SR01C-DI-EVR-01:SET_HW.OT3D');
disp(['Original pinhole trigger ', pinhole_trig_orig])

rf=lcaGet('LI-RF-MOSC-01:FREQ');
for n=1:25
%      lcaPut('SR01C-DI-EVR-01:SET_HW.OT3D',1e-3/(1/rf*4)*(45+n));
    mbf_growdamp_capture(mbf_axis,...
        'excitation_location', 'Sideband', 'save_to_archive', 'no');
    td.beam_size.pinhole1.x(n) = lcaGet('SR-DI-EMIT-01:P1:SIGMAX');
    td.beam_size.pinhole1.y(n) = lcaGet('SR-DI-EMIT-01:P1:SIGMAY');
    td.beam_size.pinhole2.x(n) = lcaGet('SR-DI-EMIT-01:P2:SIGMAX');
    td.beam_size.pinhole2.y(n) = lcaGet('SR-DI-EMIT-01:P2:SIGMAY');
    td.ph1.image(n) = get_Pinhole_image('SR01C-DI-DCAM-04');
    td.ph2.image(n) = get_Pinhole_image('SR01C-DI-DCAM-05');
end %for
for n=1:25
    td.ph1.beam_info(n) = get_beamsize_from_image(td.ph1.image(n));
    td.ph2.beam_info(n) = get_beamsize_from_image(td.ph2.image(n));
end %fir
% Restore original trigger
% lcaPut('SR01C-DI-EVR-01:SET_HW.OT3D', pinhole_trig_orig)