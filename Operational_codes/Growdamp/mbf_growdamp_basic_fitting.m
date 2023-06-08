function [s, delta, p] = mbf_growdamp_basic_fitting(data)
%
% Args:
%       data (vector of floats): The data.
%       debug(int): if 1 then outputs graphs of individual modes to allow
%                                    selection of appropriate overrides.
%
%   Returns:
%       s(vector of floats): coefficients of the polynomial fit of the
%                            magnitude of data
%       delta(float): deviation of the magnitude data to the 
%                     fit of the magnitude data.
%       p(vector of floats): coefficients of the polynomial fit of the 
%                            phase of data
x_ax = 1:length(data);
mag = log(abs(data));
s = polyfit(x_ax, mag, 1);
c = polyval(s,x_ax);
delta = mean(abs(c - mag)./c);
temp = unwrap(angle(data)) / (2*pi);
p = polyfit(x_ax,temp,1);