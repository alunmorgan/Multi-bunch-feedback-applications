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
pv_head = [pv_names.hardware_names.(ax), BB.Base, num2str(bank)];
% bunch gains
% mbf_get_then_put([pv_head, BB.Gains], ones(1,936)); 
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
if out_type == 0
% all off
lcaput([pv_head, BB.FIR_disable])
lcaput([pv_head, BB.NCO1_disable])
lcaput([pv_head, BB.NCO2_disable])
lcaput([pv_head, BB.SEQ_disable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 1
% FIR only
mbf_get_then_put([pv_head, BB.FIRgains], ones(1,936) .* 1);
lcaput([pv_head, BB.FIR_enable])
lcaput([pv_head, BB.NCO1_disable])
lcaput([pv_head, BB.NCO2_disable])
lcaput([pv_head, BB.SEQ_disable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 2
% NCO only
lcaput([pv_head, BB.FIR_disable])
mbf_get_then_put([pv_head, BB.NCO1gains], ones(1,936) .* 1);
lcaput([pv_head, BB.NCO1_enable])
lcaput([pv_head, BB.NCO2_disable])
lcaput([pv_head, BB.SEQ_disable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 3
% NCO + FIR 
mbf_get_then_put([pv_head, BB.FIRgains], ones(1,936) .* 1);
lcaput([pv_head, BB.FIR_enable])
mbf_get_then_put([pv_head, BB.NCO1gains], ones(1,936) .* 1);
lcaput([pv_head, BB.NCO1_enable])
lcaput([pv_head, BB.NCO2_disable])
lcaput([pv_head, BB.SEQ_disable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 4
% sweep only
lcaput([pv_head, BB.FIR_disable])
lcaput([pv_head, BB.NCO1_disable])
lcaput([pv_head, BB.NCO2_disable])
mbf_get_then_put([pv_head, BB.SEQgains], ones(1,936) .* 1);
lcaput([pv_head, BB.SEQ_enable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 5
% sweep + FIR 
mbf_get_then_put([pv_head, BB.FIRgains], ones(1,936) .* 1);
lcaput([pv_head, BB.FIR_enable])
lcaput([pv_head, BB.NCO1_disable])
lcaput([pv_head, BB.NCO2_disable])
mbf_get_then_put([pv_head, BB.SEQgains], ones(1,936) .* 1);
lcaput([pv_head, BB.SEQ_enable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 6
% sweep + NCO
lcaput([pv_head, BB.FIR_disable])
mbf_get_then_put([pv_head, BB.NCO1gains], ones(1,936) .* 1);
lcaput([pv_head, BB.NCO1_enable])
lcaput([pv_head, BB.NCO2_disable])
lcaput([pv_head, BB.SEQ_disable])
lcaput([pv_head, BB.PLL_disable])
elseif out_type == 7
% sweep + NCO + FIR
mbf_get_then_put([pv_head, BB.FIRgains], ones(1,936) .* 1);
lcaput([pv_head, BB.FIR_enable])
mbf_get_then_put([pv_head, BB.NCO1gains], ones(1,936) .* 1);
lcaput([pv_head, BB.NCO1_enable])
lcaput([pv_head, BB.NCO2_disable])
mbf_get_then_put([pv_head, BB.SEQgains], ones(1,936) .* 1);
lcaput([pv_head, BB.SEQ_enable])
lcaput([pv_head, BB.PLL_disable])

% mbf_get_then_put([pv_head, BB.Output_types], ones(1,936) .* out_type);
% select which FIR filter to use
mbf_get_then_put([pv_head, BB.FIR_select], ones(1,936) .* 0); 

