function monitored_data = scan_id_setting(set_values, Execute, Set_PV, read_PV,...
    monitored_pvs, wait)
nt = 1;
for i = 1:length(set_values)
    lcaPut(Set_PV, num2str(set_values(i)))
    if ~isempty(Execute)
        lcaPutNoWait(Execute, 1)
    end %if
    dist_from_target = 1;
    val_history = zeros(10,1);
    tic
    warn_flag = 0;
    while any(dist_from_target > 0.1)
        val = lcaGet(read_PV);
        val_history = circshift(val_history, -1);
        val_history(10) = val;
        val_history_check = diff(val_history);
        if all(abs(val_history_check) < 0.1) && warn_flag == 0
           fprintf('WARNING  ID does not appear to be moving')
           warn_flag = 1;
        elseif all(abs(val_history_check) >= 0.1) && warn_flag == 1
           fprintf('ID has started moving again')
           warn_flag = 0;
        end %if
        dist_from_target = abs(val - set_values(i));
        pause(0.2)
        duration = toc;
        monitored_data(1:length(monitored_pvs), nt) = lcaGet(monitored_pvs);
        monitored_data(length(monitored_pvs) +1, nt) = now;
        nt = nt+1;
        % 2min timer to break out of the loop
        if duration > 120
            disp('Timeout reached')
            break
        end %if
    end %while
    pause(wait)
end %for