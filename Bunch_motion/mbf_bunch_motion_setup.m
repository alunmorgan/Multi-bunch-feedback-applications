function mbf_bunch_motion_setup
% Sets up all three axis so that they will take a single set of data each
% when armed and triggered
%
% Example: mbf_bunch_motion_setup

[~, ~, pv_names, trigger_inputs] = mbf_system_config;
PVt = pv_names.tails;

mbf_axes = {'x', 'y', 's'};
% Disarm all the sequencers
for ekf = 1:length(mbf_axes)
mbf_get_then_put([pv_names.hardware_names.(mbf_axes{ekf}) pv_names.tails.triggers.SEQ.disarm], 1)
end %for

mbf_systems = {'T', 'L'};
for hse = 1:2
    % Generate the base PV name.
    pv_head = pv_names.hardware_names.(mbf_systems{hse});
    % set up the appropriate triggering
    % Stop triggering first, otherwise there's a good chance the first thing
    % we'll do is loose the beam as we change things.
    for trigger_ind = 1:length(trigger_inputs)
        trigger = trigger_inputs{trigger_ind};
        mbf_get_then_put([pv_head PVt.triggers.MEM.(trigger).enable_status], 'Ignore');
        mbf_get_then_put([pv_head PVt.triggers.MEM.(trigger).blanking_status], 'All');
    end %for
    % Set the trigger to one shot
    mbf_get_then_put([pv_head PVt.triggers.MEM.mode], 'One Shot');
    % Set the triggering to External only
    lcaPut([pv_head PVt.triggers.MEM.('EXT').enable_status], 'Enable')
  
    lcaPut([pv_head PVt.triggers.MEM.('ADC0').blanking_status], 'Blanking')
        lcaPut([pv_head PVt.triggers.MEM.('ADC1').blanking_status], 'Blanking')
    
    %  set up the memory buffer to capture ADC data.
    mbf_get_then_put([pv_head, PVt.MEM.channel_select], 'ADC0/ADC1')
end %for