function mbf_bunch_motion_setup(pv_names)
% Sets up all three axis so that they will take a single set of data each
% when armed and triggered
%
% Example: mbf_bunch_motion_setup

memory_triggers = pv_names.tails.triggers.MEM;
memory_buffers = pv_names.tails.MEM;

mbf_setup_wait_for_hw_trigger(pv_names)

PVt = pv_names.tails;
mbf_systems = {'T', 'L'};
for hse = 1:2
    % Generate the base PV name.
    pv_head = pv_names.hardware_names.(mbf_systems{hse});

    set_variable([pv_head memory_triggers.('ADC0').blanking_status], 'Blanking')
        set_variable([pv_head memory_triggers.('ADC1').blanking_status], 'Blanking')
    
    %  set up the memory buffer to capture ADC data.
    set_variable([pv_head, memory_buffers.channel_select], 'ADC0/ADC1')
end %for