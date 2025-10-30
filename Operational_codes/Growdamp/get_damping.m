function [s, delta, p] = get_damping(x_data, y_data, override, length_averaging, adv_fitting, threshold_value)
%
%
% Args:
%       data (vector of floats): The data.
%       dwell(int): The dwell time set for this data.
%       override (int): The number of turns to analyse (if NaN analyse everything)
%       length_averaging(int): Determines the strength of the filtering out
%                              of high frequecies in the data.
%       advanced_fitting (bool): switches between simple (0)
%                                and advanced fitting (1).
%       threshold_value(float): The value considered to be the noise floor.
%
%   Returns:
%       s(vector of floats): coefficients of the polynomial fit of the
%                            magnitude of data
%       delta(float): deviation of the magnitude data to the
%                     fit of the magnitude data.
%       p(vector of floats): coefficients of the polynomial fit of the
%                            phase of data

if ~isnan(override)
    if override < length(y_data)
        y_data = y_data(1:override);
    end %if
end %if
if length(y_data) < 3
    s = [NaN, NaN];
    delta = NaN;
    p = NaN;
else
   
    if adv_fitting == 0
        [s, delta, p] = mbf_growdamp_basic_fitting(x_data, y_data, length_averaging, threshold_value);
    else
        [s, delta, p] = mbf_growdamp_advanced_fitting(x_data, y_data, length_averaging, threshold_value);
    end %if
end %if
