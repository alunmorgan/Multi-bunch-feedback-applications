function pinhole_settings = get_pinhole_settings

pinhole_settings.P1_betax = get_variable('SR-DI-EMIT-01:P1:BETAX');
pinhole_settings.P1_betay = get_variable('SR-DI-EMIT-01:P1:BETAY');
pinhole_settings.P2_betax = get_variable('SR-DI-EMIT-01:P2:BETAX');
pinhole_settings.P2_betay = get_variable('SR-DI-EMIT-01:P2:BETAY');

pinhole_settings.P1_dispx = get_variable('SR-DI-EMIT-01:P1:ETAX');
pinhole_settings.P1_dispy = get_variable('SR-DI-EMIT-01:P1:ETAY');
pinhole_settings.P2_dispx = get_variable('SR-DI-EMIT-01:P2:ETAX');
pinhole_settings.P2_dispy = get_variable('SR-DI-EMIT-01:P2:ETAY');

pinhole_settings.P1_psf = get_variable('SR-DI-EMIT-01:P1:DELTA');
pinhole_settings.P2_psf = get_variable('SR-DI-EMIT-01:P2:DELTA');
pinhole_settings.P3_psf = get_variable('SR-DI-EMIT-02:P1:DELTA');

pinhole_settings.P1_cam_mag = get_variable('SR-DI-EMIT-01:P1:MAG');
pinhole_settings.P2_cam_mag = get_variable('SR-DI-EMIT-01:P2:MAG');
pinhole_settings.P3_cam_mag = get_variable('SR-DI-EMIT-02:P1:MAG');

pinhole_settings.P1_dsource = get_variable('SR-DI-EMIT-01:P1:DSOURCE');
pinhole_settings.P1_dimage = get_variable('SR-DI-EMIT-01:P1:DIMAGE');
pinhole_settings.P2_dsource = get_variable('SR-DI-EMIT-01:P2:DSOURCE');
pinhole_settings.P2_dimage = get_variable('SR-DI-EMIT-01:P2:DIMAGE');
pinhole_settings.P3_dsource = get_variable('SR-DI-EMIT-02:P1:DSOURCE');
pinhole_settings.P3_dimage = get_variable('SR-DI-EMIT-02:P1:DIMAGE');