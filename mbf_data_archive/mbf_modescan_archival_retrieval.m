function mbf_modescan_archival_retrieval(ax, date_range, filter_conditions,...
    varargin)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
% also filters out datasets with machine settings outside the specified
% acceptable range.
%
% Args:
%       ax (str): The number of the axis (x, y, s)
%       date_range (pair of datetime instances): The range of time to extract.
%       bypass_index (str) : 'no' for use the pregnerated index (much faster)
%                            'yes' for work things out from the file metatdata.
%                            the default is 'no'.
%       metadata_only(str): 'no' return all data
%                            'yes' remove the sample data from the output structure.
%                            the default is 'no'.
%       sweep_parameter (str): Parameter to be used. This name must exist
%                              in the data structure. (only needed if
%                              anal_type set to 'parameter sweep')
%       parameter_step_size (float): Defines the spacing of the steps in
%                                    the parameter sweep.
%                                    Multiple data sets which are on the same
%                                    step will be averaged. (only needed if
%                                    anal_type set to 'parameter sweep')
%
% Example: mbf_modescan_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);

addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)));
addRequired(p, 'date_range');
addRequired(p, 'filter_conditions');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', 'current', @ischar);
addParameter(p, 'parameter_step', 0.1, validScalarPosNum);
addParameter(p,'current_range',[2 305]);

parse(p, ax, date_range, filter_conditions, varargin{:});

selection_name = ['Modescan_',ax,'_axis'];

requested_data = mbf_archival_dataset_retrieval(selection_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);

if length(requested_data) == 1
    [data_magnitude, data_phase, ~, ~] = ...
        mbf_modescan_archival_analysis(requested_data, 'analysis_type','collate');
    mbf_modescan_plotting(data_magnitude, data_phase, requested_data{1})
else
    % Only keeping datasets that satify the requested machine conditions.
    conditioned_data = mbf_archival_conditional_filtering(requested_data,...
        filter_conditions);
    if isempty(conditioned_data)
        disp('No data meeting the requirements')
    else
        if strcmp(p.Results.analysis_type, 'collate')
            [data_magnitude, data_phase, times, setup] = ...
                mbf_modescan_archival_analysis(conditioned_data,...
                'analysis_type','collate');
        elseif strcmp(p.Results.analysis_type, 'sweep')
            [data_magnitude, data_phase, times, setup] = ...
                mbf_modescan_archival_analysis(conditioned_data,...
                'analysis_type','parameter_sweep', ...
                'sweep_parameter',p.Results.sweep_parameter,...
                'parameter_step', p.Results.parameter_step);
        else
            error('modescanArchivalRetrieval:InputError', 'Please select collate or sweep as the analysis type');
        end %if
        setup.axis = ax;
        mbf_modescan_archival_plotting(conditioned_data, data_magnitude, data_phase, times, setup);
    end %if
end %if
