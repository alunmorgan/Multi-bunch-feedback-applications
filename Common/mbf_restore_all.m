function mbf_restore_all
% Finds all the stored values in the captured config folder. Restores all
% the found PVs to the stored state, and deletes the value from the store.
% For PROC files it determines if it is was a reset and if so triggers the
% corresponding arm PV. Does not do anything with other types of PROC
% files.
%
% Example: mbf_restore_all_except_triggers

[root_string, ~] = mbf_system_config;
root_string = root_string{1};

[pv_files, file_dir] = dir_list_gen(fullfile(root_string, 'captured_config'), 'mat');
[pv_files1, ~] = dir_list_gen(fullfile(root_string, 'captured_config'), 'PROC');
pv_files = cat(1, pv_files, pv_files1);
for hsaw = 1:length(pv_files)
    if isempty(strfind(pv_files{hsaw}, '.PROC'))
        mbf_restore_pv(pv_files{hsaw})
        delete(fullfile(file_dir, pv_files{hsaw}))
    else
        if ~isempty(strfind(pv_files{hsaw}, ':RESET_S.PROC'))
            %                 Arm the previously disabled trigger
            disp(regexprep(pv_files{hsaw}, ':RESET_S.PROC', ':ARM_S.PROC'))
            lcaPut(regexprep(pv_files{hsaw}, ':RESET_S.PROC', ':ARM_S.PROC'), 1)
            delete(fullfile(file_dir, pv_files{hsaw}))
        else
            [~, individual_pv , ~] = fileparts(pv_files{hsaw});
            disp(['Not touching ', individual_pv ])
        end %if
    end %if
end %for