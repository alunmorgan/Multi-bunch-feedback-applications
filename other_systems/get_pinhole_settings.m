function pinhole_settings = get_pinhole_settings

pinhole_settings.P1_betax = lcaGet('SR-DI-EMIT-01:P1:BETAX');
pinhole_settings.P1_betay = lcaGet('SR-DI-EMIT-01:P1:BETAY');
pinhole_settings.P2_betax = lcaGet('SR-DI-EMIT-01:P2:BETAX');
pinhole_settings.P2_betay = lcaGet('SR-DI-EMIT-01:P2:BETAY');

pinhole_settings.P1_dispx = lcaGet('SR-DI-EMIT-01:P1:ETAX');
pinhole_settings.P1_dispy = lcaGet('SR-DI-EMIT-01:P1:ETAY');
pinhole_settings.P2_dispx = lcaGet('SR-DI-EMIT-01:P2:ETAX');
pinhole_settings.P2_dispy = lcaGet('SR-DI-EMIT-01:P2:ETAY');

pinhole_settings.P1_psf = lcaGet('SR-DI-EMIT-01:P1:DELTA');
pinhole_settings.P2_psf = lcaGet('SR-DI-EMIT-01:P2:DELTA');
pinhole_settings.P3_psf = lcaGet('SR-DI-EMIT-02:P1:DELTA');

pinhole_settings.P1_cam_mag = lcaGet('SR-DI-EMIT-01:P1:MAG');
pinhole_settings.P2_cam_mag = lcaGet('SR-DI-EMIT-01:P2:MAG');
pinhole_settings.P3_cam_mag = lcaGet('SR-DI-EMIT-02:P1:MAG');

pinhole_settings.P1_dsource = lcaGet('SR-DI-EMIT-01:P1:DSOURCE');
pinhole_settings.P1_dimage = lcaGet('SR-DI-EMIT-01:P1:DIMAGE');
pinhole_settings.P2_dsource = lcaGet('SR-DI-EMIT-01:P2:DSOURCE');
pinhole_settings.P2_dimage = lcaGet('SR-DI-EMIT-01:P2:DIMAGE');
pinhole_settings.P3_dsource = lcaGet('SR-DI-EMIT-02:P1:DSOURCE');
pinhole_settings.P3_dimage = lcaGet('SR-DI-EMIT-02:P1:DIMAGE');