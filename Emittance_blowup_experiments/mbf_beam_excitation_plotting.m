function mbf_beam_excitation_plotting(emittance_blowup)

figure(1)
yyaxis left
plot(emittance_blowup.excitation_frequency, ...
    emittance_blowup.beam_oscillation_x.*1e-3,'.-')
xlabel('Excitation frequency [tune]')
ylabel('Hor. RMS oscillation [\mum]')
yyaxis right
plot(emittance_blowup.excitation_frequency, ...
    emittance_blowup.emittance_x,'.-')
ylabel('Hor. emittance [nm rad]')

figure(2)
yyaxis left
plot(emittance_blowup.excitation_frequency, ...
    emittance_blowup.beam_oscillation_y.*1e-3,'.-')
xlabel('Excitation frequency [tune]')
ylabel('Ver. RMS oscillation [\mum]')
yyaxis right
plot(emittance_blowup.excitation_frequency, emittance_blowup.emittance_y,'.-')
ylabel('Ver. emittance [pm rad]')