function archive_retreval_investigate_metadata(requested_data)


% mapping older and newer metadata
for nfe = 1:length(requested_data)
    if isfield(requested_data{nfe}, 'I_bpm')
        requested_data{nfe}.('current') = requested_data{nfe}.('I_bpm');
    end %if
    if isfield(requested_data{nfe}, 'fill')
        requested_data{nfe}.('fill_pattern') = requested_data{nfe}.('fill');
    end %if
end %for

for nfe = 1:length(requested_data)
    temp = fieldnames(requested_data{nfe});
    if nfe == 1
        fields = temp;
    else
    fields = intersect(fields, temp);
    end
end %for

% remove the fields which are not useful to compare.
inds = any(cat(2, strcmp(fields, 'ax_label'), strcmp(fields, 'filename'),...
    strcmp(fields, 'data'), strcmp(fields, 'time')),2);

fields(inds) = [];

metadata = cell(length(fields), length(requested_data));
for hse = 1:length(fields)
    for wak = 1:length(requested_data)
        metadata{hse, wak} = requested_data{wak}.(fields{hse});
    end %for
end %for

% % find out if each line has variation
% for sen = 1:size(metadata, 1)
%     reference_data = metadata{sen,1};
%     if iscell(reference_data)
%         reference_data = reference_data{1};
%     end %if
%     for ens = size(metadata, 2):-1:2
%         test_data = metadata{sen, ens};
%         if iscell(test_data)
%             test_data = test_data{1};
%         end %if
%         if ischar(reference_data)
%             variation(sen, ens) = ~strcmp(test_data, reference_data);
%         elseif isvector(reference_data)
%             variation(sen, ens) = max(test_data - reference_data) > 0.01;
%         else
%             variation(sen, ens) = test_data - reference_data > 0.0001;
%         end %if
%     end %for
% end %for
% 
% % remove non varying ones
% vary = any(variation,2);

for nfe = 1:length(requested_data)
        disp([requested_data{nfe}.('current'), '  ', requested_data{nfe}.('ringmode')])  
end %for
