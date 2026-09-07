% --- SCRIPT: run_and_log_emittance_data.m ---
% Run this to record ~500 to 1000 data points of machine operation

selected_axis = 'x';
target_sequence = [2.8, 3, 3.5, 4, 4.5, 2.8]; % Different target steps (pm rad)
% target_sequence = [8, 10, 7, 9, 8.5, 8]; % Different target steps (pm rad)
steps_per_target = 100;               % Steps to hold each target (100 * 0.5s = 50s)

% Pre-allocate logging arrays
total_steps = length(target_sequence) * steps_per_target;
r_log = zeros(total_steps, 1);  % Reference emittance targets
y_log = zeros(total_steps, 1);  % Measured emittance (emit)
u_log = zeros(total_steps, 1);  % Excitation power (gain_scalar)
time_log = zeros(total_steps, 1);
     [~, ~, pv_names] = mbf_system_config;
             mbf_device = pv_names.hardware_names.(lower(selected_axis));

step = 1;
for i = 1:length(target_sequence)
    target = target_sequence(i);
    fprintf('Setting emittance target to %g pm rad...\n', target);
    [r_log_temp, y_log_temp, u_log_temp, time_log_temp] =...
        emittance_control_loop(selected_axis, target);
if i==1
    r_log = r_log_temp;
    y_log = y_log_temp;
    u_log = u_log_temp;
    time_log = time_log_temp;
else
    r_log = cat(1, r_log, r_log_temp);
    y_log = cat(1, y_log, y_log_temp);
    u_log = cat(1, u_log, u_log_temp);
    time_log = cat(1, time_log, time_log_temp);
end %if
    %     for s = 1:steps_per_target
%         % Read current machine variables
%          
%         emit_val  = get_variable(pv_names.emittance.(lower(selected_axis)).val);
%         power_val = get_variable([mbf_device, pv_names.tails.NCO2.gain_scalar]);
%         
%         % Save into logging vectors
%         r_log(step) = target;
%         y_log(step) = emit_val;
%         u_log(step) = power_val;
%         time_log(step) = (step - 1) * 0.5; % 0.5 sec hardware interval
%         
%         % Execute original control step (or call original controller)
%         % ... hardware updates ...
%         pause(0.5);
%         
%         step = step + 1;
%     end
end

% SAVE THE FILE TO DISK:
save_name = ['emittance_log_data_',selected_axis,'.mat'];
save(save_name, 'r_log', 'y_log', 'u_log', 'time_log');
fprintf(['Operating data saved to: ',save_name, '\n']);