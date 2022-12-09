function mbf_growdamp_archival_retrieval_setup(axis, date_range, varargin)

default_sweep_parameter = 'current';
default_current_range = 350;
default_fillpattern_range = 1000;
default_tune_range = 0.5;
default_cavity1_voltage_range = 0.1;
default_cavity2_voltage_range = 0.1;
default_wiggler_field_I12_range = 0.1;
default_wiggler_field_I15_range = 0.1;

default_parameter_step_size = 0.1;
defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;

p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p, 'axis',@ischar);
addRequired(p, 'date_range');
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);
addParameter(p, 'current_range', default_current_range, validScalarPosNum);
addParameter(p, 'fillpattern_range', default_fillpattern_range, validScalarPosNum);
addParameter(p, 'tune_range', default_tune_range, validScalarPosNum);
addParameter(p, 'cavity1_voltage_range', default_cavity1_voltage_range, validScalarPosNum);
addParameter(p, 'cavity2_voltage_range', default_cavity2_voltage_range, validScalarPosNum);
addParameter(p, 'wiggler_field_I12_range', default_wiggler_field_I12_range, validScalarPosNum);
addParameter(p, 'wiggler_field_I15_range', default_wiggler_field_I15_range, validScalarPosNum);
addParameter(p, 'overrides', defaultOverrides);
addParameter(p,'advanced_fitting',defaultAnalysisSetting, @isnumeric);
addParameter(p, 'debug', 0);
p.PartialMatching = false;

parse(p,axis, date_range, varargin{:});

selections = {...
    'current', p.Results.current_range;
    'fill_pattern', p.Results.fillpattern_range;
    'tune', p.Results.tune_range;
    'cavity1_voltage', p.Results.cavity1_voltage_range;
    'cavity3_voltage', p.Results.cavity2_voltage_range;
    'wiggler_field_I12', p.Results.wiggler_field_I12_range;
    'wiggler_field_I15', p.Results.wiggler_field_I15_range;
    };

requested_data = mbf_growdamp_archival_retrieval(axis, date_range, 1);
disp('Retrieval complete')
conditioned_data = condition_mbf_metadata(requested_data);

if iscell(p.Results.sweep_parameter)
    conditioned_data = filter_on_multiple_parameters(conditioned_data, selections);
end %if

if isempty(conditioned_data)
    disp('No data meeting the requirements')
else
    if strcmp(p.Results.analysis_type, 'collate')
        [dr_passive, dr_active, error_passive, error_active, times, setup, extents] = ...
            mbf_growdamp_archival_analysis(conditioned_data, 'analysis_type','collate',...
            'overrides', p.Results.overrides, ...
            'advanced_fitting', p.Results.advanced_fitting,...
            'debug', p.Results.debug);
    elseif strcmp(p.Results.analysis_type, 'sweep')
        [dr_passive, dr_active, error_passive, error_active, times, setup, extents] = ...
            mbf_growdamp_archival_analysis(conditioned_data, 'analysis_type','parameter_sweep', ...
            'sweep_parameter',p.Results.sweep_parameter,...
            'parameter_step', p.Results.parameter_step,...
            'overrides', p.Results.overrides, ...
            'advanced_fitting', p.Results.advanced_fitting,...
            'debug', p.Results.debug);
    else
        error('Please select collate or sweep as the analysis type');
    end %if
    setup.axis = axis;
    mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents);
    
end %if
end %function

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
end %function

function sets = filter_on_multiple_parameters(input_data, selections)
% returns the sets of data which have metatdata values below thoise given in
% selections
%
%   Args:
%       input_data{cell array of structures}
%       selections{cell array}: collumn 1 is the name of the field in the
%                               metatdata, collumn2 is the value to be below.
%   Returns:
%       sets {cell array of structures}: Datasets which matched the criteria.
sets = cell(length(input_data),1);
tk =1;
for nwd = 1:length(input_data)
    test = NaN(size(selections,1), 1);
    for law = 1:size(selections,1)
        ref_val = selections{law,2};
        test_val = input_data.(selections{law,1});
        if iscell(test_val)
            temp = strcmp(test_val{nwd}, test_val);
        elseif size(test_val,2) == 1
            temp = abs(test_val - test_val(nwd)) < ref_val;
        else
            temp = abs(test_val - repmat(test_val(nwd,:),size(test_val,1), 1)) < ref_val;
            temp = ~any(~temp,2);
        end %if
        test(law,1:length(temp)) = temp;
        clear temp
    end %for
    
    ref_data = test(:,nwd);
    if isempty(find(ref_data == 0, 1))
        sets{tk} = find(~any(~test) == 1);
        tk = tk +1;
    end %if
    clear test
end %for
sets(tk:end) = [];
end %function