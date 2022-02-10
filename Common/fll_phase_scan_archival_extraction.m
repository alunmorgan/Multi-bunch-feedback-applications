function fll_phase_scan_archival_extraction(mbf_axis, date_range, varargin)

default_scan_type = 'samples';
p = inputParser;
addRequired(p, 'mbf_axis');
addRequired(p, 'date_range');
addParameter(p, 'scan_type', default_scan_type);

parse(p, mbf_axis, date_range, varargin{:});

if strcmp(mbf_axis, 'x')
    filter_name = 'fll_phase_scan_x_axis';
elseif strcmp(mbf_axis, 'y')
    filter_name = 'fll_phase_scan_y_axis';
end %if

wanted_datasets = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index', 1);

requested_data = cell(length(wanted_datasets),1);
for hse = 1:length(wanted_datasets)
    temp = load(wanted_datasets{hse});
    temp.data.f = temp.data.f(:,1); 
    temp.data.mag = temp.data.mag(:,1);
    temp.data.iq = temp.data.iq(:,1);
    requested_data{hse} = temp.data;
    clear temp
end %for

% filter out broken data
data_state = ones(length(requested_data),1);
for wns = 1:length(requested_data)
    if max(requested_data{wns}.f) - min(requested_data{wns}.f) < 1E-9
        if max(requested_data{wns}.mag) - min(requested_data{wns}.mag) < 8E-6
            data_state(wns) = 0;
        end %if
    end %if
end %for
   
requested_data(data_state==0) = [];
fll_phase_scan_plotting_multi(requested_data, 'scan_type', p.Results.scan_type)
