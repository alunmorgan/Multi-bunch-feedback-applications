function beam_sizes = beamsize_get_data

beam_sizes.P1_sigx = get_variable('SR-DI-EMIT-01:P1:SIGMAX_MEAN');
beam_sizes.P1_sigy = get_variable('SR-DI-EMIT-01:P1:SIGMAY_MEAN');
beam_sizes.P2_sigx = get_variable('SR-DI-EMIT-01:P2:SIGMAX_MEAN');
beam_sizes.P2_sigy = get_variable('SR-DI-EMIT-01:P2:SIGMAY_MEAN');
beam_sizes.P3_sigx = get_variable('SR-DI-EMIT-02:P1:SIGMAX_MEAN');
beam_sizes.P3_sigy = get_variable('SR-DI-EMIT-02:P1:SIGMAY_MEAN');