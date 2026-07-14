function mbf_setup_wait_for_hw_trigger(pv_names)

memory_triggers = pv_names.tails.triggers.MEM;
sequencer_triggers = pv_names.tails.triggers.SEQ;

mbf_axes = {'x', 'y', 's'};
% Disarm all the sequencers
for ekf = 1:length(mbf_axes)
    set_variable([pv_names.hardware_names.(mbf_axes{ekf}) sequencer_triggers.disarm], 1)
end %for

mbf_systems = {'T', 'L'};
for hse = 1:2
    % Generate the base PV name.
    pv_head = pv_names.hardware_names.(mbf_systems{hse});
    % set up the appropriate triggering
    % Stop triggering first, otherwise there's a good chance the first thing
    % we'll do is loose the beam as we change things.
    for trigger_ind = 1:length(pv_names.trigger_inputs)
        trigger = pv_names.trigger_inputs{trigger_ind};
        set_variable([pv_head memory_triggers.(trigger).enable_status], 'Ignore');
        set_variable([pv_head memory_triggers.(trigger).blanking_status], 'All');
    end %for
    % Set the trigger to one shot
    set_variable([pv_head memory_triggers.mode], 'One Shot');
    % Set the triggering to External only
    set_variable([pv_head memory_triggers.('EXT').enable_status], 'Enable')
end %for