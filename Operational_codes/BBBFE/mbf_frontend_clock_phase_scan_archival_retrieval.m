function conditioned_data = mbf_frontend_clock_phase_scan_archival_retrieval(ax,...
    date_range, filter_conditions, varargin)
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
%
% Returns:
%       conditioned_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_modescan_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = @(x) any(validatestring(x, {'x', 'y', 's'}));
boolean_string = @(x) any(validatestring(x, {'yes', 'no'}));
analysis_type_string = @(x) any(validatestring(x, {'collate', 'sweep'}));
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);

default_sweep_parameter = 'current';
default_parameter_step_size = 0.1;

addRequired(p, 'ax', axis_string);
addRequired(p, 'date_range');
addRequired(p, 'filter_conditions');
addParameter(p, 'bypass_index', 'no', boolean_string);
addParameter(p, 'metadata_only', 'no', boolean_string);
addParameter(p, 'analysis_type', 'collate', analysis_type_string)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);

parse(p, ax, date_range, filter_conditions, varargin{:});

selection_name = ['clock_phase_scan_', ax, '_axis'];

requested_data = mbf_archival_dataset_retrieval(selection_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);

if length(requested_data) == 1
   BBBFE_clock_phase_scan_plotting(requested_data{1} )
else
    conditioned_data = mbf_archival_conditional_filtering(requested_data,'current_range', p.Results.current_range);

    if isempty(conditioned_data)
        disp('No data meeting the requirements')
    else
        if strcmp(p.Results.analysis_type, 'collate')
            [leading, excited, following, times, setup] = ...
                mbf_frontend_clock_phase_scan_archival_analysis(conditioned_data, 'analysis_type','collate');
        elseif strcmp(p.Results.analysis_type, 'sweep')
            [leading, excited, following, times, setup] = ...
                mbf_frontend_clock_phase_scan_archival_analysis(conditioned_data, 'analysis_type','parameter_sweep', ...
                'sweep_parameter',p.Results.sweep_parameter,...
                'parameter_step', p.Results.parameter_step);
        end %if
        setup.axis = ax;
        mbf_frontend_clock_phase_scan_archival_plotting(conditioned_data, leading, excited, following, times, setup);
    end %if
end %if