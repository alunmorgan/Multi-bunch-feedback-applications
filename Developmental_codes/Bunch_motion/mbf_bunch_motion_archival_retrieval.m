function mbf_bunch_motion_archival_retrieval(date_range, filter_conditions,...
    varargin)
% Extracts requested data from the data archive between
% the requested times(date_range)
%
% Args:
%       date_range (pair of datetime instances): The range of time to extract.
%       bypass_index (str) : 'no' for use the pregnerated index (much faster)
%                            'yes' for work things out from the file metatdata.
%                            the default is 'no'.
%       metadata_only(str): 'no' return all data
%                            'yes' remove the sample data from the output structure.
%                            the default is 'no'.
%
% Example: mbf_bunch_motion_archival_retrieval([now-5, now])


p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);

addRequired(p, 'date_range');
addRequired(p, 'filter_conditions');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', 'current', @ischar);
addParameter(p, 'parameter_step', 0.1, validScalarPosNum);
addParameter(p, 'selected_bunches', [150:160]);
addParameter(p, 'selected_turns', [600:650]);

parse(p, date_range, filter_conditions, varargin{:});

selection_name = 'Bunch_motion';

requested_data = mbf_archival_dataset_retrieval(selection_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);

if length(requested_data) == 1
    [dataset, ~, ~] = ...
        mbf_bunch_motion_archival_analysis(requested_data, 'analysis_type','collate');
    mbf_bunch_motion_plotting(dataset, requested_data{1},...
        p.Results.selected_bunches, p.Results.selected_turns)
else
    % Only keeping datasets that satify the requested machine conditions.
    conditioned_data = mbf_archival_conditional_filtering(requested_data,...
        filter_conditions);
    if isempty(conditioned_data)
        disp('No data meeting the requirements')
    else
        if strcmp(p.Results.analysis_type, 'collate')
            [dataset, times, setup] = ...
                mbf_bunch_motion_archival_analysis(conditioned_data,...
                'analysis_type','collate');
        elseif strcmp(p.Results.analysis_type, 'sweep')
            [dataset, times, setup] = ...
                mbf_bunch_motion_archival_analysis(conditioned_data,...
                'analysis_type','parameter_sweep', ...
                'sweep_parameter',p.Results.sweep_parameter,...
                'parameter_step', p.Results.parameter_step);
        else
            error('bunch_motionArchivalRetrieval:InputError', 'Please select collate or sweep as the analysis type');
        end %if
        mbf_bunch_motion_archival_plotting(conditioned_data, dataset, times, setup);
    end %if
end %if