function BBBFE_full_frontend_checkout(single_bunch_location)
%BBBFE_FULL_FRONTEND_CHECKOUT 
% This assumes that the machine is set up with a single bunch in the machine at
% the single_bunch_location

BBBFE_system_phase_scan('X', single_bunch_location)
BBBFE_system_phase_scan('Y', single_bunch_location)
BBBFE_system_phase_scan('S', single_bunch_location)

BBBFE_clock_phase_scan('X', single_bunch_location)
BBBFE_clock_phase_scan('Y', single_bunch_location)
BBBFE_clock_phase_scan('S', single_bunch_location)


