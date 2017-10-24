function [poly_data, frequency_shifts] = mbf_growdamp_analysis(exp_data)
% takes the data from mbf growdamp capture and fits it with a series of 
% linear fits to get the damping times for each mode.
%
% Args:
%       exp_data (structure): Contains the systems setup and the data
%                             captured
%
% Example: [poly_data, frequency_shifts] = tmbf_growdamp_analysis(exp_data)

[~, harmonic_number, ~] = mbf_system_config;
exp_data.data = reshape(exp_data.data,[],harmonic_number)';
n_modes = size(exp_data.data,1);
% Preallocation
poly_data = NaN(harmonic_number,3,2);
frequency_shifts = NaN(harmonic_number, 1);

% Find the idicies for the end of each period.
end_of_growth = exp_data.growth_turns;
end_of_passive = end_of_growth + exp_data.nat_turns;
end_of_active = end_of_passive + exp_data.act_turns;

for nq = n_modes:-1:1
    %% split up the data into growth, passive damping and active damping.
    
    % growth
    x1 = 1:end_of_growth;
    g_data = exp_data.data(nq,x1);
    s1 = polyfit(x1,log(abs(g_data)),1);
    c1 = polyval(s1,x1);
    delta1 = mean(abs(c1 - log(abs(g_data)))./c1);
    
    % passive damping
    x2 = end_of_growth + 1:end_of_passive;
    pd_data = exp_data.data(nq,x2);
        % truncating the data if it falls into the noise
    f2 = find(movmean(abs(pd_data), 5) <50, 1, 'first');
    if isempty(f2)
        f2 = length(x2);
    end
    pd_data = pd_data(1:f2);
    x2 = x2(1:f2);
    s2 = polyfit(x2,log(abs(pd_data)),1);
    c2 = polyval(s2,x2);
    delta2 = mean(abs(c2 - log(abs(pd_data)))./c2);
    temp = unwrap(angle(pd_data)) / (2*pi);
    p2 = polyfit(x2,temp,1);
    
    %active damping
    x3 = end_of_passive + 1:end_of_active;
    ad_data = exp_data.data(nq,x3);
    % truncating the data if it falls into the noise
    f3 = find(movmean(abs(ad_data), 5) <50, 1, 'first');
    if isempty(f3)
        f3 = length(x3);
    end
    ad_data = ad_data(1:f3);
    x3 = x3(1:f3);
    s3 = polyfit(x3,log(abs(ad_data)),1);
    c3 = polyval(s3,x3);
    delta3 = mean(abs(c3 - log(abs(ad_data)))./c3);
    clear tmp_data

    % Each point is dwell time turns long so the
    % damping time needs to be adjusted accordingly.
    s1(1) = s1(1) ./ exp_data.growth_dwell;
    s2(1) = s2(1) ./ exp_data.nat_dwell;
    s3(1) = s3(1) ./ exp_data.act_dwell;
    
    % Output data structure.
    % axis 1 is mode, axis 2 is expermental state (excitation, natural
    % damping, active damping). axis 3 is damping time, offset and fractional error.
    poly_data(nq,1,1:2) = s1;
    poly_data(nq,2,1:2) = s2;
    poly_data(nq,3,1:2) = s3;
    poly_data(nq,1,3) = delta1;
    poly_data(nq,2,3) = delta2;
    poly_data(nq,3,3) = delta3;
    frequency_shifts(nq) = p2(1);
end
disp('')