function [s, delta, p] = mbf_growdamp_basic_fitting(x_data, y_data, length_averaging, threshold_value)
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

% Smooth the data
if length(y_data)> length_averaging *8
    y_data = movmean(y_data, length_averaging);
end %if

%Truncate data at the point the decay hits the noise floor.
noise_floor_intercept_pd = find(abs(y_data) <= threshold_value, 1, 'first');
if ~isempty(noise_floor_intercept_pd)
    y_data(noise_floor_intercept_pd:end) = [];
    x_data(noise_floor_intercept_pd:end) = [];
end %if

%Take the log and fit a linear to it
mag = log(abs(y_data));
s = polyfit(x_data, mag, 1);
c = polyval(s,x_data);
%Construct an error metric.
delta = mean(abs(c - mag));

temp = unwrap(angle(y_data)) / (2*pi);
p = polyfit(x_data,temp,1);