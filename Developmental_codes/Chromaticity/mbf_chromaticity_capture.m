function chromaticity = mbf_chromaticity_capture(input_settings, pv_names)
% Captures chromaticity data.
%   Args:
%       input_settings(struct): containing
%           mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%           n_repeats (int): The number of repeat datapoints to capture
%           n_trys (int): How many times to retry on bad data return.
%   Returns:
%       chromaticity (struct): data structure containing the experimental
%                          results. [optional output]
%
% example data = mbf_chromaticity_capture(input_settings, pv_names)

for nd = 1:input_settings.n_repeats
    chromaticity.data(nd) = chromaticity_from_sidebands(...
        input_settings.mbf_axis, input_settings.n_trys, pv_names);
    pause(1.2) % make sure there is new data.
end %for
    chromaticity.mean = mean(chromaticity.data, 'omitnan');
    chromaticity.std = std(chromaticity.data, 0, 'omitnan');
