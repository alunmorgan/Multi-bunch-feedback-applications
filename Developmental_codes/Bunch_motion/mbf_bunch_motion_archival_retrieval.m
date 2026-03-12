function requested_data = mbf_bunch_motion_archival_retrieval(date_range, varargin)
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
% Returns:
%       conditioned_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_bunch_motion_archival_retrieval([now-5, now])


p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'date_range');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, date_range, varargin{:});

filter_name = 'Bunch_motion';

requested_data = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);
