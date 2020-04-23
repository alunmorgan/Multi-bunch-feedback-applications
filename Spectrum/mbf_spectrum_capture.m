function data = mbf_spectrum_capture(mbf_axis, n_turns, fold, repeat)
% captures a set of data from the mbf system runs the analysis and then
% saves the results.
%
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
%                       requesting   .
%       fold (int): The number of times to fold the data along the
%                   frequency axis. This enhances power resolution
%                   at the cost of frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
% Returns:
%       data (cell array): Multiple sets of time data.
% 
% Example: data = mbf_spectrum_capture('x', 1, 10)

[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')
    chan = 0;
elseif strcmp(mbf_axis, 'y')
    chan = 1;
end %if

for k=repeat:-1:1
    if strcmpi(mbf_axis, 's')
            lcaPut([pv_names.hardware_names.L pv_names.tails.MEM.arm],1);
        lcaPut([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
        raw_data{k} = mbf_read_mem(pv_names.hardware_names.L, n_turns,'channel', chan, 'lock', 60);
    else
            lcaPut([pv_names.hardware_names.T pv_names.tails.MEM.arm],1);
        lcaPut([pv_names.hardware_names.T, pv_names.tails.triggers.soft], 1)
        raw_data{k} = mbf_read_mem(pv_names.hardware_names.T, n_turns,'channel', chan, 'lock', 60);
    end %if
end%for
data = mbf_spectrum_analysis(raw_data, n_turns, fold, repeat);
data.time = clock;
data.base_name = ['Spectrum_', mbf_axis, '_axis'];

%% saving the data to a file
save_to_archive(root_string, data, graph_handles)