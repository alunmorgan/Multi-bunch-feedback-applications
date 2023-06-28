function conditioned_data = mbf_growdamp_archival_retrieval(ax, date_range, varargin)
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
%       analysis_type(str): determines the type of analysis to run 'collate' or
%                           'sweep', the default is 'collate'.
%       sweep_parameter (str): Parameter to be used. This name must exist
%                              in the data structure. (only needed if
%                              anal_type set to 'parameter sweep')
%       parameter_step_size (float): Defines the spacing of the steps in
%                                    the parameter sweep.
%                                    Multiple data sets which are on the same
%                                    step will be averaged. (only needed if
%                                    anal_type set to 'parameter sweep')
%       overrides (list of ints): Two values setting the number of turns to
%                                    analyse (passive, active)
%       debug(int): if 1 then outputs graphs of individual modes to allow
%                                    selection nof appropriate overrides.
%
%
% Returns:
%       conditioned_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_growdamp_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);

default_sweep_parameter = 'current';
default_parameter_step_size = 0.1;
defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;
defaultCurrentRange = [2 150];

addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)));
addRequired(p, 'date_range');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);
addParameter(p, 'overrides', defaultOverrides);
addParameter(p,'advanced_fitting',defaultAnalysisSetting, @isnumeric);
addParameter(p,'current_range',defaultCurrentRange);
addParameter(p, 'debug', 0);

parse(p, ax, date_range, varargin{:});

if strcmpi(ax, 'x')
    filter_name = 'Growdamp_x_axis';
elseif  strcmpi(ax, 'y')
    filter_name = 'Growdamp_y_axis';
elseif strcmpi(ax, 's')
    filter_name = 'Growdamp_s_axis';
else
    error('mbf_archival_dataset_retrieval: No valid axis given (should be x, y or s)')
end %if
requested_data = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);

% Only keeping datasets that satify the requested machine conditions.
conditioned_data = mbf_archival_conditional_filtering(requested_data,'current_range', p.Results.current_range);
if isempty(conditioned_data)
    disp('No data meeting the requirements')
else
    if strcmp(p.Results.analysis_type, 'collate')
        [dr_passive, dr_active, error_passive, error_active, times, setup] = ...
            mbf_growdamp_archival_analysis(conditioned_data, 'analysis_type','collate',...
            'overrides', p.Results.overrides, ...
            'advanced_fitting', p.Results.advanced_fitting,...
            'debug', p.Results.debug);
    elseif strcmp(p.Results.analysis_type, 'sweep')
        [dr_passive, dr_active, error_passive, error_active, times, setup] = ...
            mbf_growdamp_archival_analysis(conditioned_data, 'analysis_type','parameter_sweep', ...
            'sweep_parameter',p.Results.sweep_parameter,...
            'parameter_step', p.Results.parameter_step,...
            'overrides', p.Results.overrides, ...
            'advanced_fitting', p.Results.advanced_fitting,...
            'debug', p.Results.debug);
    else
        error('Please select collate or sweep as the analysis type');
    end %if
    setup.axis = ax;
    mbf_growdamp_archival_plotting(conditioned_data, dr_passive, dr_active, error_passive, error_active, times, setup);
end %if
