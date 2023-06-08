function [s, delta, p] = get_damping(data, dwell, override, length_averaging, adv_fitting)
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

% if ~isnan(override)
%     if override < length(data)
%         data = data(1:override);
%     end %if
% else
%     [data] = truncate_to_linear(data, length_averaging);
% end %if
if length(data) < 3
    s = [NaN, NaN];
    delta = NaN;
    p = NaN;
else
    if adv_fitting == 0
        [s, delta, p] = mbf_growdamp_basic_fitting(data);
    else
        [data] = truncate_to_linear(data, length_averaging);
        [s, delta, p] = mbf_growdamp_advanced_fitting(data, length_averaging);
    end %if
end %if
% Each point is dwell time turns long so the
% damping time needs to be adjusted accordingly.
s(1) = s(1) ./ dwell;
