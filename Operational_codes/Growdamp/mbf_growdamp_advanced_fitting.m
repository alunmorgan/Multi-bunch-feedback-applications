function  [s, delta, p] = mbf_growdamp_advanced_fitting(x_data, y_data, length_averaging, threshold_value)

% Fits to an exponential decay.
%
% Args:
%       x_data (vector of floats): The turns.
%       y_data (vector of floats): The data.
%       length_averaging (int): number of points for the box car average to work
%                               with.
%       threshold_value (float): The data value defined as the noise floor.
%
%   Returns:
%       s(vector of floats): coefficients of the polynomial fit of the
%                            magnitude of data
%       delta(float): deviation of the magnitude data to the 
%                     fit of the magnitude data.
%       p(vector of floats): coefficients of the polynomial fit of the 
%                            phase of data



%Truncate data at the point the decay hits the noise floor.
noise_floor_intercept_pd = find(abs(y_data) <= threshold_value, 1, 'first');
if ~isempty(noise_floor_intercept_pd)
    y_data(noise_floor_intercept_pd:end) = [];
    x_data(noise_floor_intercept_pd:end) = [];
end %if

% Smooth the data
if length(y_data)> length_averaging *8
    mm = movmean(y_data, length_averaging);
end %if

%take the log of the data as we expect an exponential decay. meaning that the
%log(data) should be linear
mag = log(abs(mm));
% Get an initial starting value.
p_initial = polyfit(x_data, mag, 1);
% initial_fit_line = polyval(p_initial, 1:length(mm));
if p_initial(1) < 0
    % damping
    % find the max so as to allow any initial rise in the data to be
    % removed.
    [~,dm_loc] = max(mag);
%     dm_loc = 2 * dm_loc;
else
    %growth
    dm_loc = 0;
end %if
x_ax = 0:length(mag)-1 - dm_loc;

n_tests = 200;
% compare linear fits to the data.
vals = linspace(p_initial(1), p_initial(1) - 2e-7, n_tests);
% sweep the gradient. Large changes in sample length indicate that a large
% fraction of the line has moved from below the line to above it.
sample_length = NaN(n_tests,1);
for gra = 1:n_tests
    y = vals(gra) * x_ax + mag(dm_loc + 1);
    weighted_error = (mag(dm_loc+1:end) - y);% .* linspace(length(mm)-1 - dm_loc, 0 , length(mm)-dm_loc);
    weighted_error(weighted_error >0) = 0;
    [~, min_loc] = min(weighted_error);
    sample_length_temp = find(weighted_error(min_loc:end) == 0, 1, 'first');
    if isempty(sample_length_temp)
        sample_length(gra) = length(x_ax);
    else
        sample_length(gra) = sample_length_temp + min_loc - 1;
    end %if
    if sample_length(gra) < 3
        break
    end %if
end %if

[~, I] = min(diff(sample_length));
if I ~= 1
    I = I-1;
end %if
s = [vals(I), mag(dm_loc + 1)];
c = polyval(s,x_data);
delta = mean(abs(c - mag));
temp = unwrap(angle(mm)) / (2*pi);
p = polyfit(x_data,temp,1);