function [s, delta, p] = mbf_growdamp_basic_fitting(x_data, y_data)
%
% Args:
%       x_data (vector of floats): The turns.
%       y_data (vector of floats): The data.
%
%   Returns:
%       s(vector of floats): coefficients of the polynomial fit of the
%                            magnitude of data
%       delta(float): deviation of the magnitude data to the 
%                     fit of the magnitude data.
%       p(vector of floats): coefficients of the polynomial fit of the 
%                            phase of data
mag = log(abs(y_data));
s = polyfit(x_data, mag, 1);
c = polyval(s,x_data);
delta = mean(abs(c - mag)./c);
temp = unwrap(angle(y_data)) / (2*pi);
p = polyfit(x_data,temp,1);