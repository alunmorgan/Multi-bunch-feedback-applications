function output = BPM_FA_get_data(sample_time)
% Get FA data from all BPMS.
%   Args:
%       sample_time(float): length of time in seconds to return.

% The +5 is to give the fast archiver time to deal with the data ingest
% before requesting it.
pause(sample_time + 5)
BPM_names = fa_id2name(1:173);
try
    output = fa_load( convertTo(datetime("now"),'datenum') + [-(sample_time +5)./60./60./24 -5./60./60./24], 1:173);
catch
    pause(5)
    output = fa_load( convertTo(datetime("now"),'datenum') + [-(sample_time +5)./60./60./24 -5./60./60./24], 1:173);
end %try
output.bpm_names = BPM_names;
output.X = squeeze(output.data(1,:,:));
output.Y = squeeze(output.data(2,:,:));
if size(output.data,3)< 10000 * sample_time
    disp('Did not get a full set of data. Trying again...')
    output = BPM_FA_get_data(sample_time);
end %if