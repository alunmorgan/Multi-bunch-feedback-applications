function output_data = condition_mbf_metadata(input_data)
% Mapping values in old datasets to defined variables.

%Initialisation
n_datasets = length(input_data);
output_data = input_data;

for jgr = n_datasets:-1:1
    if isfield(input_data{jgr}, 'I_bpm')
        output_data{jgr}.current(jgr) = input_data{jgr}.I_bpm;
    end %if

    if isfield(input_data{jgr}, 'fill')
        output_data{jgr}.fill_pattern = input_data{jgr}.fill;
    end %if

    if isfield(input_data{jgr}, 'RFread')
        output_data{jgr}.cavity1_voltage = input_data{jgr}.RFread(1);
        output_data{jgr}.cavity2_voltage = input_data{jgr}.RFread(2);
    end %if

    if isfield(input_data{jgr}, 'id')
        output_data{jgr}.wiggler_field_I12 = input_data{jgr}.id.i12field;
        output_data{jgr}.wiggler_field_I15 = input_data{jgr}.id.i15field;
    end %if

    if isfield(input_data{jgr}, 'qy')
        output_data{jgr}.tune = input_data{jgr}.qy;
    end %if

    if isfield(input_data{jgr}, 'qx')
        output_data{jgr}.tune = input_data{jgr}.qx;
    end %if

end %for
