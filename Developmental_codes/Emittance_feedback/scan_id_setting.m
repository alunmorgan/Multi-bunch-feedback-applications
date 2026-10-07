function monitored_data = scan_id_setting(set_values, Execute, Set_PV, read_PV,...
    monitored_pvs, wait)
nt = 1;
for i = 1:size(set_values, 1)
    lcaPut(Set_PV, set_values(i,:)')
    lcaPutNoWait(Execute, 1)
    dist_from_target = 1;
    tic
    while any(dist_from_target > 0.1)
        dist_from_target = abs(lcaGet(read_PV) - set_values(i,:)');
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