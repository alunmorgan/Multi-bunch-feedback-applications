function bunch_motion = mbf_bunch_motion_capture
% simultaineously captures bunch by bunch centroid data for all three axes.
% When armed by the code each system will start aquisition on the next hardware trigger.
%
% Example: bunch_motion = mbf_bunch_motion_capture

%% Getting the desired system setup parameters.
[root_string, num_buckets, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

[turn_count, turn_offset] = mbf_bunch_motion_config;
% getting general environment data.
bunch_motion = machine_environment;

%% construct filename and add it to the structure
bunch_motion.base_name = 'Bunch_motion';

%% Generating the required directory structure.
tree_gen(root_string,bunch_motion.time);

% Generate the base PV names.
pv_head_T = pv_names.hardware_names.T;
pv_head_L = pv_names.hardware_names.L;

%Disarm, so that the current settings will be picked up upon arming.
set_variable([pv_head_T, pv_names.tails.triggers.MEM.disarm], 1)
set_variable([pv_head_L, pv_names.tails.triggers.MEM.disarm], 1)


%% Trigger the measurement on all three axes

% Turn off the External triggering from the Event receiver.
set_variable(pv_names.Hardware_trigger, 0)

% Arming the systems
if strcmp([pv_head_T pv_names.tails.TRG.memory_status], 'Idle') == 1 &&...
        strcmp([pv_head_L pv_names.tails.TRG.memory_status], 'Idle') == 1
    mbf_get_then_put({[pv_head_T pv_names.tails.triggers.MEM.arm];...
        [pv_head_L pv_names.tails.triggers.MEM.arm]},1);
else
    error('BunchMotionCapture:MemoryError', 'Memory is not ready please try again')
end %if


% Triggering the measurement. %%%% SHOULD TRIGGER ON THE NEXT EXTERNAL
set_variable(pv_names.Hardware_trigger, 1)

% Triggering memory under a lock.
bunch_motion_temp = mbf_read_mem(pv_names.hardware_names.T, turn_count,'offset', turn_offset, 'lock', 60);
bunch_motion.x = bunch_motion_temp(:,1);
bunch_motion.y = bunch_motion_temp(:,2);
bunch_motion.z = mbf_read_mem(pv_names.hardware_names.L, turn_count, 'offset', turn_offset,'channel', 0, 'lock', 60);
bunch_motion.num_buckets = num_buckets;

%% saving the data to a file
save_to_archive(root_string, bunch_motion)
