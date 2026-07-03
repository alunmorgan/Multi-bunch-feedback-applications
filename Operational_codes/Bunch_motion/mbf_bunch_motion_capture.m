function bunch_motion = mbf_bunch_motion_capture(pv_names)
% simultaineously captures bunch by bunch centroid data for all three axes.
% When armed by the code each system will start aquisition on the next hardware trigger.
%
% Example: bunch_motion = mbf_bunch_motion_capture(pv_names)

[turn_count, turn_offset] = mbf_bunch_motion_config;

% Generate the base PV names.
pv_head_T = pv_names.hardware_names.T;
pv_head_L = pv_names.hardware_names.L;

%Disarm, so that the current settings will be picked up upon arming.
set_variable([pv_head_T, pv_names.tails.triggers.MEM.disarm], 1)
set_variable([pv_head_L, pv_names.tails.triggers.MEM.disarm], 1)

%% Trigger the measurement on all three axes
% Turn off the External triggering from the Event receiver.
set_variable(pv_names.Hardware_trigger, 0)

pause(0.5)
% Check memory is ready
mem_t = lcaGet([pv_head_T pv_names.tails.TRG.memory_status]);
mem_s = lcaGet([pv_head_L pv_names.tails.TRG.memory_status]);
if strcmp(mem_t{1}, 'Idle') ~= 1 ||...
        strcmp(mem_s{1}, 'Idle') ~= 1
    error('BunchMotionCapture:MemoryError', 'Memory is not ready please try again')
end %if

%Arming the systems
set_variable({[pv_head_T pv_names.tails.triggers.MEM.arm];...
    [pv_head_L pv_names.tails.triggers.MEM.arm]},1);

% Triggering the measurement. %%%% SHOULD TRIGGER ON THE NEXT EXTERNAL
set_variable(pv_names.Hardware_trigger, 1)

% Triggering memory under a lock.
bunch_motion_temp = mbf_read_mem(pv_names.hardware_names.T, turn_count,'offset', turn_offset, 'lock', 60);
bunch_motion.x = bunch_motion_temp(:,1);
bunch_motion.y = bunch_motion_temp(:,2);
bunch_motion.z = mbf_read_mem(pv_names.hardware_names.L, turn_count, 'offset', turn_offset,'channel', 0, 'lock', 60);
