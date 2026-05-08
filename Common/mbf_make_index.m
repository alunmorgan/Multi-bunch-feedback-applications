function mbf_make_index(application_type, ax)
% Writes index files to speed up archive retrival functions
% Args:
%       application_type(str): either 'Growdamp', 'Bunch_motion', 'Modescan',
%                           'Spectrum', 'LO_scan', 'system_phase_scan', 
%                           'clock_phase_scan'.
%       ax(str): 'x', 'y', or 's'
%
% Example mbf_make_index('Growdamp', 'x')

[root_string, ~, ~, ~] = mbf_system_config;

if ~strcmp(application_type, 'Growdamp') && ~strcmp(application_type, 'Bunch_motion') ...
        && ~strcmp(application_type, 'Modescan') && ~strcmp(application_type, 'Spectrum') ...
        && ~strcmp(application_type, 'LO_scan') && ~strcmp(application_type, 'system_phase_scan') ...
        && ~strcmp(application_type, 'clock_phase_scan')...
        && ~strcmp(application_type, 'fll_phase_scan')
    error('makeIndex:InputError', 'No valid application given (Growdamp, Bunch_motion, Modescan, Spectrum, LO_scan, system_phase_scan, clock_phase_scan, fll_phase_scan)')
end %if
if nargin < 2
    ax = '';
    if strcmp(application_type, 'Growdamp') || strcmp(application_type, 'Modescan') || strcmp(application_type, 'Spectrum')
        error('makeIndex:InputError', 'An axis needs to be specified')
    end %if
end %if


if strcmp(application_type, 'Bunch_motion') || strcmp(application_type, 'LO_scan') || ...
        strcmp(application_type, 'system_phase_scan') || strcmp(application_type, 'clock_phase_scan')
    index_name = 'index';
    filter_name = application_type;
else
    if strcmpi(ax, 'x')
        index_name = 'x_axis_index';
        filter_name = [application_type, '_x_axis'];
    elseif  strcmpi(ax, 'y')
        index_name = 'y_axis_index';
        filter_name = [application_type, '_y_axis'];
    elseif strcmpi(ax, 's')
        index_name = 's_axis_index';
        filter_name = [application_type, '_s_axis'];
    else
        error('makeIndex:InputError', 'No valid axis given (should be x, y or s)')
    end %if
end %if
tic
datasets = {};
for nes = 1:length(root_string)
    sets_temp = dir_list_gen_tree(root_string{nes}, '.mat', 1);
    datasets = cat(1, datasets, sets_temp);
end %for
datasets = datasets(2:end);
wanted_datasets_type = datasets(find_position_in_cell_lst(strfind(datasets, filter_name)));
disp(['Creating lookup index for ',application_type, ' ' ax])
if isempty(wanted_datasets_type)
    disp('No files to index')
else
    for kse = 1:length(wanted_datasets_type) %parfor chokes the server
        try % handelling corrupted input files
            temp = load(wanted_datasets_type{kse});
        catch me1
            ok(kse) = 0;
            disp(me1.message)
        end %try
        data_name = fieldnames(temp);
        % Although the code saves eveything in 'data', older datasets have
        % a variety of names.
        if strcmp(data_name{1}, 'data') || ...
           strcmp(data_name{1}, 'growdamp') || ...
           strcmp(data_name{1}, 'what_to_save')
            file_time{kse} = temp.(data_name{1}).time;
            file_name{kse} = wanted_datasets_type{kse};
            ok(kse) = 1;
         else
%             disp(fieldnames(temp))
            ok(kse) = 0;
        end %if
    end %for
    file_index = cat(1, file_name(ok==1), file_time(ok==1));
    toc
    save(fullfile(root_string{1}, [application_type, '_', index_name]), 'file_index')
end %if