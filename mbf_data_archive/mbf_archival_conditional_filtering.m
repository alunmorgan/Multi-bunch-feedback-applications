function conditioned_data = mbf_archival_conditional_filtering(requested_data, varargin)
% returns the sets of data which have metatdata values below thoise given in
% selections
%
%   Args:
%       input_data{cell array of structures}
%       selections{cell array}: collumn 1 is the name of the field in the
%                               metatdata, collumn2 is the value to be below.
%   Returns:
%       sets {cell array of structures}: Datasets which matched the criteria.
%
% Example conditioned_data = mbf_archival_conditional_filtering(requested_data)

default_current_range = [0 350];
default_fillpattern_range = [0 1000];
default_tune_range = [0 0.5];
default_cavity1_voltage_range = [0.1 2];
default_cavity2_voltage_range = [0.1 2];
default_wiggler_field_I12_range = [0 4.5];
default_wiggler_field_I15_range = [0 4.5];

p = inputParser;
validNum = @(x) isnumeric(x);
addRequired(p, 'requested_data');
addParameter(p, 'current_range', default_current_range, validNum);
addParameter(p, 'fillpattern_range', default_fillpattern_range, validNum);
addParameter(p, 'tune_range', default_tune_range, validNum);
addParameter(p, 'cavity1_voltage_range', default_cavity1_voltage_range, validNum);
addParameter(p, 'cavity2_voltage_range', default_cavity2_voltage_range, validNum);
addParameter(p, 'wiggler_field_I12_range', default_wiggler_field_I12_range, validNum);
addParameter(p, 'wiggler_field_I15_range', default_wiggler_field_I15_range, validNum);

p.PartialMatching = false;

parse(p,requested_data, varargin{:});

selections = {...
    'current', p.Results.current_range;
    'fill_pattern', p.Results.fillpattern_range;
    'tune', p.Results.tune_range;
    'cavity1_voltage', p.Results.cavity1_voltage_range;
    'cavity3_voltage', p.Results.cavity2_voltage_range;
    'wiggler_field_I12', p.Results.wiggler_field_I12_range;
    'wiggler_field_I15', p.Results.wiggler_field_I15_range;
    };
select = NaN(length(requested_data),1);
for nwd = 1:length(requested_data)
    test = NaN(size(selections,1), 1);
    for law = 1:size(selections,1)
        ref_val = selections{law,2};
        try
        test_val = requested_data{nwd}.(selections{law,1});
        catch
             % if selection is not in the dataset do not filter it.
            test(law) = 1;
            continue
        end %try
        if strcmp(selections{law}, 'tune')
            if isstruct(test_val)
                test_val = test_val.([requested_data{nwd}.ax_label,'_tune']).tune;
            end %if
        end %if
        if isnan(test_val)
            % If no valid data do not filter.
            temp = 1;
        elseif iscell(test_val)
            temp = strcmp(test_val, ref_val);
        elseif length(test_val) == 1
            temp = test_val >= ref_val(1) && test_val <= ref_val(2);
        else
            temp1 = test_val >= repmat(ref_val(1), size(test_val,1), size(test_val,2));
            temp2 = test_val <= repmat(ref_val(2), size(test_val,1), size(test_val,2));
            temp1 = ~any(~temp1);
            temp2 = ~any(~temp2);
            temp = any([temp1 temp2]);
        end %if
        test(law) = temp;
        clear temp
    end %for
    select(nwd) = ~any(~test);
    clear test
end %for
conditioned_data = requested_data(boolean(select));