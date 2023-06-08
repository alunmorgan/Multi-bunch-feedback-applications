function [poly_data, frequency_shifts] = mbf_growdamp_analysis(exp_data, varargin)
% takes the data from mbf growdamp capture and fits it with a series of
% linear fits to get the damping times for each mode.
%
%   Args:
%       exp_data (structure): Contains the systems setup and the data
%                             captured.
%       overrides (list of ints): Two values setting the number of turns to
%                                 analyse (passive, active)
%       advanced_fitting (bool): switches between simple (0)
%                                and advanced fitting (1).
%       length_averaging(int): Determines the strength of the filtering out
%                              of high frequecies in the data.
%       debug(int): if 1 then outputs graphs of individual modes to allow
%                                    selection of appropriate overrides.
%
%   Returns:
%       poly_data (3 by 3 matrix): axis 1 is coupling mode.
%                                  axis 2 is expermental state,
%                                  excitation, natural damping, active damping).
%                                  axis 3 is damping time, offset and
%                                  fractional error.
%       frequency_shifts (list of floats): The frequency shift of each mode.
%
% Example: [poly_data, frequency_shifts] = tmbf_growdamp_analysis(exp_data)

defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;
defaultLengthAveraging = 20;
defaultDebug = 0;

p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addRequired(p,'exp_data', @isstruct);
addOptional(p,'overrides',defaultOverrides);
addParameter(p,'advanced_fitting',defaultAnalysisSetting, @isnumeric);
addParameter(p,'length_averaging',defaultLengthAveraging, validScalarPosNum);
addParameter(p,'debug',defaultDebug, @isnumeric);
parse(p,exp_data,varargin{:});

passive_override = p.Results.overrides(1);
active_override = p.Results.overrides(2);
adv_fitting = p.Results.advanced_fitting;
length_averaging = p.Results.length_averaging;

harmonic_number = length(exp_data.fill_pattern);

% Preallocation
poly_data = NaN(harmonic_number,3,3);
frequency_shifts = NaN(harmonic_number, 1);

if ~isfield(exp_data, 'data') && isfield(exp_data, 'gddata')
    exp_data.data = exp_data.gddata;
end %if
if ~isfield(exp_data, 'data')
    return
end %if
% Sometimes there is a problem with data transfer. By truncating the data
% length to a multiple of the harmonic number the analysis can proceed.
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = reshape(exp_data.data,[],harmonic_number)';
n_modes = size(exp_data.data,1);

% Find the idicies for the end of each period.
try
    end_of_growth = exp_data.growth_turns;
catch
    poly_data = NaN(1,3,3);
    return
end %try
end_of_passive = end_of_growth + exp_data.nat_turns;
end_of_active = end_of_passive + exp_data.act_turns;

if size(exp_data.data, 2) < end_of_active
    warning(['No valid data for ', exp_data.filename])
    return
end %if
data = exp_data.data;
if isfield(exp_data, 'growth_dwell')
    growth_dwell = exp_data.growth_dwell;
else
    growth_dwell = NaN;
end %if
if isfield(exp_data, 'growth_dwell')
    nat_dwell =  exp_data.nat_dwell;
else
    nat_dwell = NaN;
end %if
if isfield(exp_data, 'growth_dwell')
    act_dwell =  exp_data.act_dwell;
else
    act_dwell = NaN;
end %if

%parfor
s1_acum = NaN(n_modes,2);
s2_acum = NaN(n_modes,2);
s3_acum = NaN(n_modes,2);
delta1_acum = NaN(n_modes,1);
delta2_acum = NaN(n_modes,1);
delta3_acum = NaN(n_modes,1);
p2_acum = NaN(n_modes,1);
parfor nq = 1:n_modes %par if it behaving
    %% split up the data into growth, passive damping and active damping.
    data_mode = data(nq,:);
    % growth
    x1 = 1:end_of_growth;
    g_data = data_mode(x1);
    s1 = polyfit(x1,log(abs(g_data)),1);
    c1 = polyval(s1,x1);
    delta1 = mean(abs(c1 - log(abs(g_data)))./c1);
    % Each point is dwell time turns long so the
    % damping time needs to be adjusted accordingly.
    s1(1) = s1(1) ./ growth_dwell;

    % passive damping
    x2 = end_of_growth + 1:end_of_passive;
    pd_data = data_mode(x2);
    [s2, delta2, p2] = get_damping(pd_data, nat_dwell, passive_override, length_averaging, adv_fitting);

    %active damping
    x3 = end_of_passive + 1:end_of_active;
    ad_data = data_mode(x3);
    [s3, delta3, p3] = get_damping(ad_data, act_dwell, active_override, length_averaging, adv_fitting);

    s1_acum(nq,:) = s1;
    s2_acum(nq,:) = s2;
    s3_acum(nq,:) = s3;
    delta1_acum(nq) = delta1;
    delta2_acum(nq) = delta2;
    delta3_acum(nq) = delta3;
    p2_acum(nq) = p2(1);
    p3_acum(nq) = p3(1);
end %parfor
% Output data structure.
% axis 1 is mode, axis 2 is expermental state (excitation, natural
% damping, active damping). axis 3 is damping time, offset and fractional error.
poly_data(:,1,1:2) = s1_acum;
poly_data(:,2,1:2) = s2_acum;
poly_data(:,3,1:2) = s3_acum;
poly_data(:,1,3) = delta1_acum;
poly_data(:,2,3) = delta2_acum;
poly_data(:,3,3) = delta3_acum;
frequency_shifts(:,1) = p2_acum;
frequency_shifts(:,2) = p3_acum;

if p.Results.debug == 1
    h = figure;
    for hs = 1:size(data,1)
        hold on
        debug_data = abs(data(hs,:));

        x_p = end_of_growth + 1:end_of_passive;
        debug_passive = debug_data(x_p);
        [debug_passive_s_basic, ~, ~] = get_damping(debug_passive, nat_dwell, NaN, 20, 0);
        %         [debug_passive_s, ~, ~] = mbf_growdamp_basic_fitting(debug_passive);
        %         debug_passive_s = polyfit(x_p,log(abs(debug_passive)),1);
        debug_fit_passive_basic = polyval(debug_passive_s_basic,1:length(debug_passive));
        [debug_passive_s_advanced, ~, ~] = get_damping(debug_passive, nat_dwell, NaN, 20, 1);
        debug_fit_passive_advanced = polyval(debug_passive_s_advanced,1:length(debug_passive));

        x_a = end_of_passive + 1:end_of_active;
        debug_active = debug_data(x_a);
        [debug_active_s_basic, ~, ~] = get_damping(debug_active, act_dwell, NaN, 20, 0);
        %         [debug_active_s, ~, ~] = mbf_growdamp_basic_fitting(debug_active);
        %         debug_active_s = polyfit(x_a,log(abs(debug_active)),1);
        debug_fit_active_basic = polyval(debug_active_s_basic,1:length(debug_active));
        [debug_active_s_advanced, ~, ~] = get_damping(debug_active, act_dwell, NaN, 20, 1);
        debug_fit_active_advanced = polyval(debug_active_s_advanced,1:length(debug_active));

        data_range = [min(debug_data), max(debug_data)];
        plot(debug_data, 'DisplayName', ['Index ', num2str(hs)])
        plot(x_p, exp(debug_fit_passive_basic), 'r', 'DisplayName', 'Passive fit (Basic)', 'LineWidth', 2)
        plot(x_a, exp(debug_fit_active_basic), 'k', 'DisplayName', 'Active fit (Basic)', 'LineWidth', 2)
        plot(x_p, exp(debug_fit_passive_advanced), ':r', 'DisplayName', 'Passive fit (Advanced)', 'LineWidth', 2)
        plot(x_a, exp(debug_fit_active_advanced), ':k', 'DisplayName', 'Active fit (Advanced)', 'LineWidth', 2)
        plot([end_of_growth, end_of_growth], data_range, ':g','DisplayName', 'End of growth', 'LineWidth', 2)
        plot([end_of_passive, end_of_passive], data_range, ':m','DisplayName', 'End of passive', 'LineWidth', 2)
        plot([end_of_active, end_of_active], data_range, ':c','DisplayName', 'end of active', 'LineWidth', 2)
        legend
        hold off
        pause(0.3)
        clf(h)
    end %for
    close(h)
end %if
