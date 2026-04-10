function mbf_set_bank(ax, bank, out_type)
% Setup an individual bank in an individual MBF system.
%
%
% Args:
%       ax (str)          : 'x', 'y', or 's' axis
%       bank (int)        : The bunch bank number.
%       out_type (int)    : Determines which combination of filters and
%                           excitation is required (0=off 1=FIR 2=NCO
%                           3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
%                           7=sweep+NCO+FIR)
%
% Example:  mbf_set_bank(ax, bank, out_type)

[~, harmonic_number, pv_names, ~] = mbf_system_config;
BB = pv_names.tails.Bunch_bank.(['bank', num2str(bank)]);
pv_head = [pv_names.hardware_names.(ax)];

% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
if out_type == 0
    % all off
    set_variable([pv_head, BB.FIR.set_disable],1)
    set_variable([pv_head, BB.NCO1.set_disable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.set_disable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 1
    % FIR only
    set_variable([pv_head, BB.FIR.gainwf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.FIR.set_enable],1)
    set_variable([pv_head, BB.NCO1.set_disable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.set_disable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 2
    % NCO only
    set_variable([pv_head, BB.FIR.set_disable],1)
    set_variable([pv_head, BB.NCO1.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.NCO1.set_enable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.set_disable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 3
    % NCO + FIR
    set_variable([pv_head, BB.FIR.gainwf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.FIR.set_enable],1)
    set_variable([pv_head, BB.NCO1.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.NCO1.set_enable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.set_disable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 4
    % sweep only
    set_variable([pv_head, BB.FIR.set_disable],1)
    set_variable([pv_head, BB.NCO1.set_disable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.SEQ.set_enable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 5
    % sweep + FIR
    set_variable([pv_head, BB.FIR.gainwf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.FIR.set_enable],1)
    set_variable([pv_head, BB.NCO1.set_disable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.SEQ.set_enable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 6
    % sweep + NCO
    set_variable([pv_head, BB.FIR.set_disable],1)
    set_variable([pv_head, BB.NCO1.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.NCO1.set_enable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.set_disable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
elseif out_type == 7
    % sweep + NCO + FIR
    set_variable([pv_head, BB.FIR.gainwf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.FIR.set_enable],1)
    set_variable([pv_head, BB.NCO1.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.NCO1.set_enable],1)
    set_variable([pv_head, BB.NCO2.set_disable],1)
    set_variable([pv_head, BB.SEQ.gainswf], ones(1,harmonic_number) .* 1);
    set_variable([pv_head, BB.SEQ.set_enable],1)
    set_variable([pv_head, BB.PLL.set_disable],1)
end %if
% select which FIR filter to use
set_variable([pv_head, BB.FIR.selectwf], ones(1,harmonic_number) .* 0);

