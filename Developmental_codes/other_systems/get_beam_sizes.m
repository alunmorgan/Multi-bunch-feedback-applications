function beam_sizes = get_beam_sizes

beam_sizes.P1_sigx = lcaGet('SR-DI-EMIT-01:P1:SIGMAX_MEAN');
beam_sizes.P1_sigy = lcaGet('SR-DI-EMIT-01:P1:SIGMAY_MEAN');
beam_sizes.P2_sigx = lcaGet('SR-DI-EMIT-01:P2:SIGMAX_MEAN');
beam_sizes.P2_sigy = lcaGet('SR-DI-EMIT-01:P2:SIGMAY_MEAN');
beam_sizes.P3_sigx = lcaGet('SR-DI-EMIT-02:P1:SIGMAX_MEAN');
beam_sizes.P3_sigy = lcaGet('SR-DI-EMIT-02:P1:SIGMAY_MEAN');