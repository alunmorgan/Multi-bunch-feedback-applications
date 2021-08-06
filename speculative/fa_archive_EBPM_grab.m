function [varargout] = fa_archive_EBPM_grab(time_range, output_location)
% Extracts full rate data from the fa_archiver for all bpms.
% Time range is a cell array of strings, with each string having the format
% yyymmddTHHMMSS.
% saves the results to a file, named by the pv name in the folder
% specified by output_location.
%
% example: fa_archive_EBPM_grab({'20170307T160000','20170307T200000'},  '/scratch/data');


for nwa = length(time_range):-1:1
    tse(nwa) = datenum(time_range{nwa},'yyyymmddTHHMMSS');
end %for

names = fa_getids;
pv_select = find_position_in_cell_lst(strfind(names, 'EBPM'));
ids = fa_name2id(names(pv_select));
pv_data = fa_load(tse,ids);
save(fullfile(output_location, ['EBPM_fa_data-',time_range{1}, '_to_', time_range{2} '.mat']), 'pv_data', '-v7.3')
if nargout == 1
    varargout{1} = pv_data;
end %if