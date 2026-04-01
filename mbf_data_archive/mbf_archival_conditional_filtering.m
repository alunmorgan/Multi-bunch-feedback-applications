function conditioned_data = mbf_archival_conditional_filtering(requested_data, selections)
% returns the sets of data which have metatdata values below thoise given in
% selections
%
%   Args:
%       input_data{cell array of structures}
%       selections{cell array}: collumn 1 is the name of the field in the
%                               metadata, collumn 2 is the value to be below.
%   Returns:
%       sets {cell array of structures}: Datasets which matched the criteria.
%
% Example conditioned_data = mbf_archival_conditional_filtering(requested_data)

select = zeros(length(requested_data),1);
for nwd = 1:length(requested_data)
    test = NaN(size(selections,1), 1);
    for law = 1:size(selections,1)
        ref_val = selections{law,2};
        if iscell(selections{law,1})
            test_val = requested_data{nwd};
            for jsw = 1:length(selections{law,1})
                if isfield(test_val, selections{law,1}{jsw})
                    test_val = test_val.(selections{law,1}{jsw});
                else
                    test_val = NaN;
                    continue
                end %if
            end %for
        else
            if isfield(requested_data{nwd}, selections{law,1})
                test_val = requested_data{nwd}.(selections{law,1});
            else
                test_val = NaN;
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
        clear temp temp1 temp2
    end %for
    select(nwd) = ~any(~test);
    clear test
end %for
conditioned_data = requested_data(boolean(select));