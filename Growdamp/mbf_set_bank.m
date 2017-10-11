function mbf_set_bank(ax, bank, out_type)
% Setup an individual bank in an individual MBF system.
%
%
% Args:
%       ax (int)          : 1,2 or 3 corresponds to x, y, or s axis
%       bank (int)        : The bunch bank number.
%       out_type (int)    : Determines which combination of filters and
%                           excitation is required (0=off 1=FIR 2=NCO 
%                           3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 
%                           7=sweep+NCO+FIR)
%
% Example:  mbf_set_bank(ax, bank, out_type)

% bunch gains
mbf_get_then_put([ax2dev(ax) ':BUN:',num2str(bank),':GAINWF_S'], ones(1,936)); 
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
mbf_get_then_put([ax2dev(ax) ':BUN:',num2str(bank),':OUTWF_S'], ones(1,936) .* out_type);
% select which FIR filter to use
mbf_get_then_put([ax2dev(ax) ':BUN:',num2str(bank),':FIRWF_S'], ones(1,936) .* 0); 