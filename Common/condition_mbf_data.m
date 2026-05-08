function output_data = condition_mbf_data(input_data)
% Mapping values in old datasets to defined variables.

%Initialisation
n_datasets = length(input_data);
output_data = input_data;

for jgr = n_datasets:-1:1
    if isfield(input_data{jgr}, 'data')
        continue
    end %if
    if isfield(input_data{jgr}, 'gddata')
        output_data{jgr}.data = input_data{jgr}.gddata;
        output_data{jgr} = rmfield(output_data{jgr}, 'gddata');
    end %if
    if isfield(input_data{jgr}, 'gddata_freq')
        output_data{jgr}.data_freq = input_data{jgr}.gddata_freq;
        output_data{jgr} = rmfield(output_data{jgr}, 'gddata_freq');
    end %if

end %for
