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

[~, ~, pv_names, ~] = mbf_system_config;
BB = pv_names.tails.Bunch_bank;
% pv_head = [pv_names.hardware_names.(ax), BB.Base, num2str(bank)];
pv_head = [pv_names.hardware_names.(ax), BB.Base, ':',num2str(bank)];

%'SR23C-DI-TMBF-01:X:BUN:0:BUNCH_SELECT_S' %FIXME
% bunch gains
% mbf_get_then_put([pv_head, BB.Gains], ones(1,936));
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
if out_type == 0
    % all off
    set_variable([pv_head, BB.FIR_set_disable],1)
    set_variable([pv_head, BB.NCO1_disable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    set_variable([pv_head, BB.SEQ_disable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 1
    % FIR only
    mbf_get_then_put([pv_head, BB.FIR_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.FIR_set_enable],1)
    set_variable([pv_head, BB.NCO1_disable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    set_variable([pv_head, BB.SEQ_disable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 2
    % NCO only
    set_variable([pv_head, BB.FIR_set_disable],1)
    mbf_get_then_put([pv_head, BB.NCO1_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.NCO1_enable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    set_variable([pv_head, BB.SEQ_disable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 3
    % NCO + FIR
    mbf_get_then_put([pv_head, BB.FIR_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.FIR_set_enable],1)
    mbf_get_then_put([pv_head, BB.NCO1_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.NCO1_enable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    set_variable([pv_head, BB.SEQ_disable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 4
    % sweep only
    set_variable([pv_head, BB.FIR_set_disable],1)
%     Error using set_variable
% multi_ezca_get_nelem -  ezcaGetNelem(): could not find process variable :
% SR23C-DI-TMBF-01:X:BUN1:FIR:SET_DISABLE_S
    set_variable([pv_head, BB.NCO1_disable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    mbf_get_then_put([pv_head, BB.SEQ_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.SEQ_enable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 5
    % sweep + FIR
    mbf_get_then_put([pv_head, BB.FIR_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.FIR_set_enable],1)
    set_variable([pv_head, BB.NCO1_disable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    mbf_get_then_put([pv_head, BB.SEQ_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.SEQ_enable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 6
    % sweep + NCO
    set_variable([pv_head, BB.FIR_set_disable],1)
    mbf_get_then_put([pv_head, BB.NCO1_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.NCO1_enable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    set_variable([pv_head, BB.SEQ_disable],1)
    set_variable([pv_head, BB.PLL_disable],1)
elseif out_type == 7
    % sweep + NCO + FIR
    mbf_get_then_put([pv_head, BB.FIR_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.FIR_set_enable],1)
    mbf_get_then_put([pv_head, BB.NCO1_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.NCO1_enable],1)
    set_variable([pv_head, BB.NCO2_disable],1)
    mbf_get_then_put([pv_head, BB.SEQ_gains], ones(1,936) .* 1);
    set_variable([pv_head, BB.SEQ_enable],1)
    set_variable([pv_head, BB.PLL_disable],1)
end %if
% mbf_get_then_put([pv_head, BB.Output_types], ones(1,936) .* out_type);
% select which FIR filter to use
mbf_get_then_put([pv_head, BB.FIR_select], ones(1,936) .* 0);

