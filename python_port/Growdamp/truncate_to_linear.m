function [data_out] = truncate_to_linear(data_in, length_averaging, n_tests)
% truncating the data if it falls into the noise
if nargin < 3
    n_tests = 100;
end %if

% reduce the high frequency noise.
mm = movmean(abs(data_in), length_averaging);
p = polyfit(1:length(mm), mm, 1);

if p(1) > 0
    %growth
    data_out = data_in;
    return
end %if

% fft_mm = fft(mm);
% % figure(21)
% % plot(abs(fft_mm))
% peaks = [0.1056];
% harmonics = 2;
% for psk = 1:length(peaks)
%     for snw = 1:harmonics
%         peak_ind = round(peaks(psk) * length(fft_mm));
%         window_length = ceil(15/2500 * length(fft_mm));
%         fft_mm = remove_peak(fft_mm, snw * peak_ind, window_length);
%         fft_mm = remove_peak(fft_mm, length(fft_mm) - snw * peak_ind, window_length);
%         fft_mm = remove_peak(fft_mm, (length(fft_mm) - peak_ind) ./ 2 - (snw-1) * peak_ind, window_length);
%         fft_mm = remove_peak(fft_mm, (length(fft_mm) + peak_ind) ./ 2 + (snw-1) * peak_ind, window_length);
%         end %for
% end %for
% mm = abs(ifft(fft_mm));

% hold all
% plot(abs(fft_mm))
% hold off
% figure(22)
% plot(mm, 'r')
% hold all
% plot(abs(ifft(fft_mm)), 'm')
% hold off


truncation_point_end = find_end_trunction_point(mm, n_tests);
if truncation_point_end < 10
    disp('truncate_to_linear: Truncation would be too severe.  Returning original data.')
    data_out = data_in;
    return
end %if

truncation_point_start = find_start_trunction_point(mm(1:truncation_point_end), n_tests);
if truncation_point_start > truncation_point_end - 10
    disp('truncate_to_linear: Truncation would be too severe.  Setting start truncation to 1')
    data_out = data_in(1:truncation_point_end);
    return
end %if

truncation_point_end = find_end_trunction_point(mm(truncation_point_start:end), n_tests);
if truncation_point_end < truncation_point_start + 10
    disp('truncate_to_linear: Truncation would be too severe.  Returning original data.')
    data_out = data_in;
    return
end %if

data_out = data_in(truncation_point_start:truncation_point_end);

% figure(1)
% clf
% hold all
% plot(abs(data_in),'b')
% plot(mm, 'r')
% plot(polyval(p,linspace(1,length(data_in), length(data_in))), 'g')
% plot(truncation_point_end, mm(truncation_point_end), 'oc')
% plot(truncation_point_start, mm(truncation_point_start), 'oc')
% p = polyfit(truncation_point_start:truncation_point_end, mm(truncation_point_start:truncation_point_end), 1);
% plot(polyval(p,linspace(1,length(data_in), length(data_in))), 'c')
% hold off
% ylim([0 inf])
end %function

function truncation_point_end = find_end_trunction_point(mm, n_tests)
% Truncate the end by increasing amounts and find the level of truncation which
% gives the smallest residuals to a linear fit.
for gra = n_tests:-1:1
    ind(gra) = floor(length(mm).* gra / n_tests);
    y = mm(1:ind(gra));
    x = 1:length(y);
    [p, S] = polyfit(x, y, 1);
    [~,  delta] = polyval(p, x, S);
%     The 1/ind is to make the errors at the begining of the decay count for
%     more than the ones at the end.
    overall_error(gra) = mean(abs(delta) * 1/ind(gra));
    if ind(gra) < 100
        ind = ind(gra:end);
        overall_error = overall_error(gra:end);
        break
    end %if
end %for
% figure(2)
% plot(ind, overall_error)
% title('End truncation')
[~, x_of_min] = min(overall_error);
truncation_point_end = ind(x_of_min);
end %function

function truncation_point_start = find_start_trunction_point(mm, n_tests)
% Truncate the begining by increasing amounts and find the level of truncation which
% gives the smallest residuals to a linear fit. This is to deal with odd effects
% which sometimes happen at the beginning (due to delays in the sysytem?)
ind = NaN(n_tests,1);
overall_error = NaN(n_tests,1);
for gra = 1:n_tests
    ind(gra) = ceil(length(mm).* gra / n_tests);
    if ind(gra) >= length(mm) - 5
        break
    end %if
    y = mm(ind(gra):end);
    x = 1:length(y);
    [p, S] = polyfit(x, y, 1);
    [~,  delta] = polyval(p, x, S);
    overall_error(gra) = mean(abs(delta) *  ind(gra)) ./ length(delta);
    
end %for
% figure(3)
% plot(ind(1:end-1), overall_error)
% title('Start truncation')
[~, x_of_min] = min(overall_error);
truncation_point_start = ind(x_of_min);
end %function

% function data = remove_peak(data, centre_x, peak_extent)
% x1 = centre_x - peak_extent;
% x2 = centre_x + peak_extent;
% y1 = data(centre_x - peak_extent);
% y2 = data(centre_x + peak_extent);
% replacement_data = interp1([x1, x2], [y1, y2], x1:x2);
% data(x1:x2) = replacement_data;
% 
% end %function
