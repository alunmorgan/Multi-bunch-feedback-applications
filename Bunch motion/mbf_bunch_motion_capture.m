function bunch_motion = mbf_bunch_motion_capture
% simultaineously captures bunch by bunch centroid data for all three axes.
% When armed by the code each system will start aquisition on the next hardware trigger.
%
% Example: bunch_motion = mbf_bunch_motion_capture

%% Getting the desired system setup parameters.
[root_string, ~] = mbf_system_config;
[turn_count, turn_offset] = mbf_bunch_motion_config;
% getting general environment data.
bunch_motion = machine_environment;

%% construct filename and add it to the structure
bunch_motion.base_name = 'Bunch_motion';

%% Generating the required directory structure.
tree_gen(root_string,bunch_motion.time);

%% Trigger the measurement on all three axes
% Capturing original trigger state for later resoration.
trig_orig_state = lcaGet('LI-TI-MTGEN-01:BS-DI-MODE');
% Temporarily turning of the trigger to make sure the system do not
% premeturely trigger. Deliberately using lcaPut.
lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 'Off')
% Arming the systems
mbf_get_then_put({[ax2dev(1) ':TRG:DDR:ARM_S.PROC'];...
    [ax2dev(2) ':TRG:DDR:ARM_S.PROC'];...
    [ax2dev(3) ':TRG:DDR:ARM_S.PROC']},1);
lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', trig_orig_state)

%% Wait for trigger
disp('Waiting for trigger.\n')
js = 1;
while ~strcmp(lcaGet([ax2dev(1) ':DDR:STATUS']),'Ready') ||...
        ~strcmp(lcaGet([ax2dev(2) ':DDR:STATUS']),'Ready') ||...
        ~strcmp(lcaGet([ax2dev(3) ':DDR:STATUS']),'Ready')
    pause(.2)
    js = js +1;
    if js >20
        fprintf('\n')
        js =1;
    end %if
    fprintf('.')
end %while
%% Wait for DDR buffers to be ready, then read out.
pause(1)

%% Checking that all the Buffers were triggered at the same time
[~,t] = lcaGet({[ax2dev(1) ':DDR:LONGWF']; [ax2dev(2) ':DDR:LONGWF']; [ax2dev(3) ':DDR:LONGWF']});
bunch_motion.time_check = diff(EPICStime2MLtime(t)) .*24 .* 60 .* 60;

bunch_motion.x = tmbf_read(ax2dev(1), turn_count, turn_offset);
bunch_motion.y = tmbf_read(ax2dev(2), turn_count, turn_offset);
bunch_motion.z = tmbf_read(ax2dev(3), turn_count, turn_offset);

%% saving the data to a file
save_to_archive(root_string, bunch_motion)
