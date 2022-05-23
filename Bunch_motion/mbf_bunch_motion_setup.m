function mbf_bunch_motion_setup
% Sets up all three axis so that they will take a single set of data each
% when armed and triggered
%
% Example: mbf_bunch_motion_setup

mbf_setup_wait_for_hw_trigger

[~, ~, pv_names, ~] = mbf_system_config;
PVt = pv_names.tails;
mbf_systems = {'T', 'L'};
for hse = 1:2
    % Generate the base PV name.
    pv_head = pv_names.hardware_names.(mbf_systems{hse});

    lcaPut([pv_head PVt.triggers.MEM.('ADC0').blanking_status], 'Blanking')
        lcaPut([pv_head PVt.triggers.MEM.('ADC1').blanking_status], 'Blanking')
    
    %  set up the memory buffer to capture ADC data.
    mbf_get_then_put([pv_head, PVt.MEM.channel_select], 'ADC0/ADC1')
end %for