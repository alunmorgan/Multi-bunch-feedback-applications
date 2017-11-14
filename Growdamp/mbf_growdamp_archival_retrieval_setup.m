function mbf_growdamp_archival_retrieval_setup(requested_data)

selections = {...
    'current', 350;
    'fill_pattern', 10;
    'tune', 0.5;
    'cavity1_voltage', 0.1;
    'cavity2_voltage', 0.1;
    'wiggler_field_I12', 0.1;
    'wiggler_field_I15', 0.1;
    };

%     'ringmodes', 0;
%     'growth_gains', 0 ...

%Initialisation
n_datasets = length(requested_data);
current = NaN(n_datasets,1);
ringmode = cell(n_datasets,1);
fill_pattern = NaN(n_datasets, 1);
cavity1_voltage = NaN(n_datasets,1);
cavity2_voltage = NaN(n_datasets,1);
wiggler_field_I12 = NaN(n_datasets,1);
wiggler_field_I15 = NaN(n_datasets,1);
tune = NaN(n_datasets,1);

% Mapping values in old datasets to defined variables.
for jgr = n_datasets:-1:1
    try
        current(jgr) = requested_data{jgr}.current;
    catch
        current(jgr) = requested_data{jgr}.I_bpm;
    end %try
    ringmode{jgr} = requested_data{jgr}.ringmode{1};
    try
        fill_pattern(jgr,1:length(requested_data{jgr}.fill_pattern)) = requested_data{jgr}.fill_pattern;
    catch
        fill_pattern(jgr,1:length(requested_data{jgr}.fill)) = requested_data{jgr}.fill;
    end %try
    try
        cavity1_voltage(jgr) = requested_data{jgr}.cavity1_voltage;
    catch
        cavity1_voltage(jgr) = requested_data{jgr}.RFread(1);
    end %try
    try
        cavity2_voltage(jgr) = requested_data{jgr}.cavity2_voltage;
    catch
        cavity2_voltage(jgr) = requested_data{jgr}.RFread(2);
    end %try
    try
        wiggler_field_I12(jgr) = requested_data{jgr}.wiggler_field_I12;
    catch
        wiggler_field_I12(jgr) = requested_data{jgr}.id.i12field;
    end %try
    try
        wiggler_field_I15(jgr) = requested_data{jgr}.wiggler_field_I15;
    catch
        wiggler_field_I15(jgr) = requested_data{jgr}.id.i15field;
    end %try
    try
        tune(jgr) = requested_data{jgr}.tune;
    catch
        try
            if strcmp(requested_data{jgr}.ax_label, 'y')
                tune(jgr) = requested_data{jgr}.qy;
            elseif strcmp(requested_data{jgr}.ax_label, 'x')
                tune(jgr) = requested_data{jgr}.qx;
            end %if
        catch
            tune(jgr) = NaN;
        end %try
    end %try
    try
        growth_gain{jgr} = requested_data{jgr}.growth_gain{1};
    catch
        growth_gain{jgr} = NaN;
    end %try
    dates(jgr) = datenum(requested_data{jgr}.time);
end %for

seen = zeros(size(dates,2),1);
sets = {};
for nwd = 1:size(dates,2)
    if seen(nwd) == 0
        test = NaN(size(selections,1), 1);
        for law = 1:size(selections,1)
            test_vals = eval(selections{law,1});
            if iscell(test_vals)
                temp = strcmp(test_vals{nwd}, test_vals);
            elseif size(test_vals,2) == 1
                temp = abs(test_vals - test_vals(nwd)) < selections{law,2};
            else
                temp = abs(test_vals - repmat(test_vals(nwd,:),size(test_vals,1), 1)) < selections{law,2};
                temp = ~any(~temp,2);
            end %if
            test(law,1:length(temp)) = temp;
            clear temp
        end %for
        
        ref_data = test(:,nwd);
        if isempty(find(ref_data == 0, 1));
            sets{end+1} = find(~any(~test) == 1);
            seen(sets{end}) =1;
        else
            seen(nwd) = 1;
        end %if
        clear test
    end %if
end %for

figure
hold on
for lse = 1:length(sets)
    plot(dates(sets{lse}),current(sets{lse}), 'o:')
end %for
hold off
datetick

for jfwe = 1:length(sets)
    clear full_data temp_data dates_temp
    dates_temp = dates(sets{jfwe});
    if length(dates_temp) ==1
        continue
    end %if
    parfor nse = 1:length(dates_temp)
        temp_data = mbf_growdamp_archival_retrieval('y', [dates_temp(nse)-3e-4, dates_temp(nse)+3e-4]);
        full_data{nse} = temp_data{1};
    end %for
    %     try
    [dr_passive, dr_active, error_passive, error_active, times, setup, extents] = mbf_growdamp_archival_analysis(full_data, 'collate');
    mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents);
    %     catch
    %         disp(num2str(jfwe))
    %     end %try
end %for