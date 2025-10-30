function [data_analysed, times, experimental_setup] = ...
    mbf_ppre_archival_analysis(data_requested, varargin)
% Takes the data extracted by mbf_growdamp_archival_retreval and operates
% across all datasets. Then plots the results.
%
% Args:
%       data_requested (cell array of structures) : Data to be analysed.
%       analysis_type (str): To select the type of analysis
%                       (collate, average, parameter_sweep)
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
% Returns:
%         emittance_x (numeric matrix): Horizontal emittance.
%                                      (bunches vs datasets)
%         emittance_y (numeric matrix): Vertical emittance.
%                                      (bunches vs datasets)
%         beam_size_p1 (numeric matrix): Beam size at pinhole 1.
%         beam_size_p2 (numeric matrix): Beam size at pinhole 2.
%         times (numeric vector): Datetimes of the datasets.
%         experimental_setup (structure): The setup parameters for the
%                                         analysis.
%
% Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

default_sweep_parameter = 'excitation_gain';
default_parameter_step_size = 0.1;
defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;


p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p, 'data_requested',@iscell);
addParameter(p, 'analysis_type', 'collate', @ischar)
addParameter(p, 'sweep_parameter', default_sweep_parameter, @ischar);
addParameter(p, 'parameter_step', default_parameter_step_size, validScalarPosNum);
addParameter(p, 'overrides', defaultOverrides);
addParameter(p, 'debug', 0);
p.PartialMatching = false;

parse(p,data_requested, varargin{:});

anal_type = p.Results.analysis_type;
sweep_parameter = p.Results.sweep_parameter;
parameter_step_size = p.Results.parameter_step;
overrides = p.Results.overrides;
debug = p.Results.debug;

for nd = length(data_requested):-1:1
    data_out = mbf_PPRE_postprocessing(data_requested{nd});
    times(nd) = datetime(data_requested{nd}.time);
    data_fields = fields(data_out);
    for fde = 1:length(data_fields)
        data_analysed.(data_fields{fde})(nd,1:size(data_out.(data_fields{fde}),1),1:size(data_out.(data_fields{fde}),2), ...
            1:size(data_out.(data_fields{fde}),3)) = data_out.(data_fields{fde});
    end %for

    if isfield(data_requested{nd}, 'I_dcct5')
        data_requested{nd}.current = data_requested{nd}.I_dcct5;
    end %if
    if strcmp(anal_type, 'parameter_sweep') && nargin >2
        param(nd) = data_requested{nd}.(sweep_parameter);
    end %if
    fprintf('.')
end %for
fprintf('\n')

experimental_setup.anal_type = anal_type;
data_fields = fields(data_analysed);
if strcmp(anal_type, 'parameter_sweep')
    experimental_setup.sweep_parameter = sweep_parameter;
    experimental_setup.parameter_step_size = parameter_step_size;
    if isempty(dr_passive)
        disp('No data left. Try changing analysis settings.')
        return
    else
        for fde = 1:length(data_fields)
            [data_analysed.(data_fields{fde}), experimental_setup.param] = mbf_analysis_reorganise_for_parameter_sweep(data_analysed.(data_fields{fde}), param, parameter_step_size);
        end %for
        %         [emittance_y, ~] = mbf_analysis_reorganise_for_parameter_sweep(emittance_y, param, parameter_step_size);
        %         [beam_size_p1, ~] = mbf_analysis_reorganise_for_parameter_sweep(beam_size_p1, param, parameter_step_size);
        %         [beam_size_p2, ~] = mbf_analysis_reorganise_for_parameter_sweep(beam_size_p2, param, parameter_step_size);
    end %if
elseif strcmp(anal_type, 'average')
    warning('Archive:Growdamp:setting','Ignoring the last two parameters as "average" is set')
      for fde = 1:length(data_fields)
    data_analysed.(data_fields{fde}) = mean(data_analysed.(data_fields{fde}),1, 'omitnan');
      end %for
%     emittance_y = mean(emittance_y,1, 'omitnan');
%     beam_size_p1 = mean(beam_size_p1,1, 'omitnan');
%     beam_size_p2 = mean(beam_size_p2,1, 'omitnan');
end %if


