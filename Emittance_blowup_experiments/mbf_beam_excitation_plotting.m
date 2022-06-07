function mbf_beam_excitation_plotting(emittance_blowup, emittance_blowup_pp)

figure(1)
yyaxis left
hold on

max_sig_x = 0;
max_sig_y = 0;
for ise = 1:size(emittance_blowup_pp.beam_oscillation_x,2)
    temp_y = squeeze(emittance_blowup_pp.beam_oscillation_x(:,ise)).*1e-3;
    temp_y = temp_y - min(temp_y);
    if max(temp_y) > max_sig_x
        bpm_select_x = ise;
        max_sig_x = max(temp_y);
    end %if
    plot(emittance_blowup.excitation_frequency, temp_y, '.-')
end %for
xlabel('Excitation frequency [tune]')
ylabel('Hor. RMS oscillation (baseline removed) [\mum]')
yyaxis right
plot(emittance_blowup.excitation_frequency, ...
    emittance_blowup_pp.emittance_x,'.-')
ylabel('Hor. emittance [nm rad]')

figure(2)
yyaxis left
hold on
for wse = 1:size(emittance_blowup_pp.beam_oscillation_y,2)
     temp_y1 = squeeze(emittance_blowup_pp.beam_oscillation_y(:,wse)).*1e-3;
    temp_y1 = temp_y1 - min(temp_y1);
if max(temp_y1) > max_sig_y
        bpm_select_y = wse;
        max_sig_y = max(temp_y1);
    end %if
    plot(emittance_blowup.excitation_frequency, temp_y1,'.-')
end %for
xlabel('Excitation frequency [tune]')
ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
yyaxis right
plot(emittance_blowup.excitation_frequency, emittance_blowup_pp.emittance_y,'.-')
ylabel('Ver. emittance [pm rad]')

figure(3)
yyaxis left
    plot(emittance_blowup.excitation_frequency, ...
        squeeze(emittance_blowup_pp.beam_oscillation_x(:,bpm_select_x)).*1e-3,'.-',...
        'DisplayName', regexprep(emittance_blowup_pp.used_bpms{bpm_select_x},'_', ' '))
xlabel('Excitation frequency [tune]')
ylabel('Hor. RMS oscillation [\mum]')

yyaxis right
plot(emittance_blowup.excitation_frequency, ...
    emittance_blowup_pp.emittance_x,'.-', 'HandleVisibility', 'off')
ylabel('Hor. emittance [nm rad]')
legend()

figure(4)
yyaxis left
hold on
    plot(emittance_blowup.excitation_frequency, ...
        squeeze(emittance_blowup_pp.beam_oscillation_y(:,bpm_select_y)).*1e-3,'.-',...
        'DisplayName', regexprep(emittance_blowup_pp.used_bpms{bpm_select_y},'_', ' '))
xlabel('Excitation frequency [tune]')
ylabel('Ver. RMS oscillation [\mum]')
yyaxis right
plot(emittance_blowup.excitation_frequency, emittance_blowup_pp.emittance_y,'.-',...
    'HandleVisibility', 'off')
ylabel('Ver. emittance [pm rad]')
legend()


