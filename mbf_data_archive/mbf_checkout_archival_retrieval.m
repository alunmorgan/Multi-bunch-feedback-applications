function requested_data = mbf_checkout_archival_retrieval(ax, date_range, varargin)
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
% Returns:
%       conditioned_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_checkout_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);

default_sweep_parameter = 'current';
default_parameter_step_size = 0.1;
defaultCurrentRange = [0 300];

addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)));
addRequired(p, 'date_range');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);
addParameter(p,'current_range',defaultCurrentRange);

parse(p, ax, date_range, varargin{:});
[root_string, ~, ~, ~] = mbf_system_config;
%TEMP OVERRIDE
root_string = '/scihome/afdm76/MBF_loopback_test_data/';

[filter_names, ~] = dir_list_gen(root_string, '', 1);
filter_names = filter_names(contains(filter_names, ['DL_checkout_' ax]));
filter_names = regexprep(filter_names, '_index.mat', '');

for nfe = 1:length(filter_names)
requested_data{nfe} = mbf_archival_dataset_retrieval(filter_names{nfe}, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);
end %for