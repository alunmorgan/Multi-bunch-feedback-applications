function [recorded_stage_names, samples_of_stage, turns_of_stage] = get_stage_details(exp_data)

if isfield(exp_data, ['seq1', '_capture_state'])
    for n = 1:length(exp_data.states)
        if contains(exp_data.(['seq' num2str(n), '_capture_state']), 'Discard')
            stage_names{n} = 'spacer';
        else
            if contains(exp_data.(['seq' num2str(n), '_enable']), 'On')
                stage_names{n} = 'growth';
            else
                if contains(exp_data.(['seq' num2str(n), '_bank_select']), 'Bank 2')
                    stage_names{n} = 'active';
                else
                    stage_names{n} = 'passive';
                end %if
            end %if
        end %if
    end %for
    ck = 1;
    % change the ordering so that the first stage in time is at index 1.
    % works out which samples in the time series correspond to each stage.
    for jjse = length(stage_names): -1: 1
        if ~contains(stage_names{jjse}, 'spacer')
            recorded_stage_names{ck} = stage_names{jjse};
            length_of_stage = exp_data.states{jjse}.duration;
            dwell_of_stage = exp_data.states{jjse}.dwell;
            if ck == 1
                end_of_stage(ck) = length_of_stage;
                samples_of_stage{ck} = (1:end_of_stage(ck));
                turns_of_stage(ck) = length(samples_of_stage{ck}) ./ dwell_of_stage;
            else
                end_of_stage(ck) = end_of_stage(ck -1) + length_of_stage;
                samples_of_stage{ck} = (end_of_stage(ck -1) + 1): end_of_stage(ck);
                turns_of_stage(ck) = length(samples_of_stage{ck}) ./ dwell_of_stage;
            end %if
            ck = ck +1;
        end %if
    end %for
else
    % Old dataset use implict order in structure to order stages.
    test = fieldnames(exp_data);
    names = test(contains(test, '_turns'));
    names = names(~contains(names, 'spacer'));
    for nrs = 1:length(names)
        turns_of_stage(nrs) = exp_data.(names{nrs});
    end %for
    turns_of_stage = flip(turns_of_stage);
    for nrs = 1:length(names)
        samples_of_stage{nrs} = sum(turns_of_stage(1:nrs-1))+1: sum(turns_of_stage(1:nrs));
    end %for
    for hs = 1:length(names)
        recorded_stage_names{hs} = regexprep(names{hs}, '_turns', '');
    end
    recorded_stage_names = flip(recorded_stage_names);
end %if

