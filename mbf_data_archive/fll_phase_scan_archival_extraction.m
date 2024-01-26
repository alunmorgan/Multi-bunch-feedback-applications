function fll_phase_scan_archival_extraction(mbf_axis, date_range, varargin)

default_scan_type = 'samples';
default_filter_type = 'none';
default_filter_range = [-inf, inf];
p = inputParser;
addRequired(p, 'mbf_axis');
addRequired(p, 'date_range');
addParameter(p, 'scan_type', default_scan_type);
addParameter(p, 'filter_type', default_filter_type);
addParameter(p, 'filter_range', default_filter_range);

parse(p, mbf_axis, date_range, varargin{:});

if strcmp(mbf_axis, 'x')
    filter_name = 'fll_phase_scan_x_axis';
elseif strcmp(mbf_axis, 'y')
    filter_name = 'fll_phase_scan_y_axis';
end %if

requested_data = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index', 'no');

% some data had many NaN collumns - this is to remove them.
for nds = 1:length(requested_data)
    requested_data{nds}.f = requested_data{nds}.f(:,1);
    requested_data{nds}.mag = requested_data{nds}.mag(:,1);
    requested_data{nds}.iq = requested_data{nds}.iq(:,1);
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
if ~strcmpi(p.Results.filter_type, 'none')
    %user defined filters

    for wns = 1:length(requested_data)
        if iscell(p.Results.filter_type)
            % need to unpack the substructure.
            data_temp = requested_data{wns};
            for ehf = 1:length(p.Results.filter_type)
                data_temp = data_temp.(p.Results.filter_type{ehf});
            end %for
        end %if

        if data_temp < p.Results.filter_range(1) || ...
                data_temp> p.Results.filter_range(2)
            data_state(wns) = 0;
        end %if
    end %for
end %if


requested_data(data_state==0) = [];
fll_phase_scan_plotting_multi(requested_data, 'scan_type', p.Results.scan_type)
