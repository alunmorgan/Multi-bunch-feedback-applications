function [poly_data, frequency_shifts] = mbf_growdamp_analysis(exp_data, overrides)
% takes the data from mbf growdamp capture and fits it with a series of
% linear fits to get the damping times for each mode.
%
%   Args:
%       exp_data (structure): Contains the systems setup and the data
%                             captured.
%       overrides (list of ints): Two values setting the number of turns to
%                                 analyse (passive, active)
%   Returns:
%       poly_data (3 by 3 matrix): axis 1 is coupling mode.
%                                  axis 2 is expermental state,
%                                  excitation, natural damping, active damping).
%                                  axis 3 is damping time, offset and
%                                  fractional error.
%       frequency_shifts (list of floats): The frequency shift of each mode.
%
% Example: [poly_data, frequency_shifts] = tmbf_growdamp_analysis(exp_data)
if nargin == 2
%     user_overide = 1;
    passive_override = overrides(1);
    active_override = overrides(2);
else
%     user_overide =0;
    % placeholders so that the parfor behaves.
    passive_override = NaN;
    active_override = NaN;
end %if

adv_fitting = 0;
length_averaging = 20;

harmonic_number = length(exp_data.fill_pattern);
% Sometimes there is a problem with data transfer. By truncating the data
% length to a multiple of the harmonic number the analysis can proceed.
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = exp_data.data(1:end - rem(length(exp_data.data), harmonic_number));
exp_data.data = reshape(exp_data.data,[],harmonic_number)';
n_modes = size(exp_data.data,1);
% Preallocation
poly_data = NaN(harmonic_number,3,3);
frequency_shifts = NaN(harmonic_number, 1);

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
parfor nq = 1:n_modes
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
%     if user_overide == 1
%         if passive_override < length(pd_data)
%             pd_data = pd_data(1:passive_override);
%         end %if
%     else
%         [pd_data] = truncate_to_linear(pd_data, length_averaging);
%     end %if
%     if length(pd_data) < 3
%         s2 = [NaN, NaN];
%         delta2 = NaN;
%         p2 = NaN;
%     else
%         [s2, delta2, p2] = mbf_growdamp_basic_fitting(pd_data);
%         %         [s2, delta2, p2] = mbf_growdamp_advanced_fitting(pd_data, length_averaging);
%     end %if
    
    %active damping
    x3 = end_of_passive + 1:end_of_active;
    ad_data = data_mode(x3);
    [s3, delta3, p3] = get_damping(ad_data, act_dwell, active_override, length_averaging, adv_fitting);
%     if user_overide == 1
%         if active_override < length(ad_data)
%             ad_data = ad_data(1:active_override);
%         end %if
%     else
%         [ad_data] = truncate_to_linear(ad_data, length_averaging);
%     end %if
%     if length(x3) < 3
%         s3 = [NaN,NaN];
%         delta3 = NaN;
%     else
%         [s3, delta3, ~] = mbf_growdamp_basic_fitting(ad_data);
%         %         [s3, delta3, ~] = mbf_growdamp_advanced_fitting(ad_data, length_averaging);
%     end %if
%     
%     s2(1) = s2(1) ./ nat_dwell;
%     s3(1) = s3(1) ./ act_dwell;
    
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
disp('')
end %function

function [s, delta, p] = get_damping(data, dwell, override, length_averaging, adv_fitting)

if ~isnan(override) 
    if override < length(data)
        data = data(1:override);
    end %if
else
    [data] = truncate_to_linear(data, length_averaging);
end %if
if length(data) < 3
    s = [NaN, NaN];
    delta = NaN;
    p = NaN;
else
    if adv_fitting == 0
        [s, delta, p] = mbf_growdamp_basic_fitting(data);
    else
        [s, delta, p] = mbf_growdamp_advanced_fitting(pd_data, length_averaging);
    end %if
end %if
    % Each point is dwell time turns long so the
    % damping time needs to be adjusted accordingly.
    s(1) = s(1) ./ dwell;
end %function