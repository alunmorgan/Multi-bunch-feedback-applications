function [x_data_out, y_data_out] = truncate_to_linear(x_data_in, y_data_in, n_tests)
% truncating the data if it falls into the noise
if nargin < 3
    n_tests = 100;
end %if


%take the log of the data as we expect an exponential decay. meaning that the
%log(data) should be linear
mm = log(abs(y_data_in));

truncation_point_end = find_end_trunction_point(mm, n_tests);
if truncation_point_end < 10 % if too close to start
    y_data_out = y_data_in;
    x_data_out = x_data_in;
    return
end %if

truncation_point_start = find_start_trunction_point(mm(1:truncation_point_end), n_tests);
if truncation_point_start > truncation_point_end - 10 % if too close to end.
    y_data_out = y_data_in(1:truncation_point_end);
    x_data_out = x_data_in(1:truncation_point_end);
    return
end %if

truncation_point_end = find_end_trunction_point(mm(truncation_point_start:end), n_tests);
if truncation_point_end < truncation_point_start + 10 % iff too close together.
    y_data_out = y_data_in;
    x_data_out = x_data_in;
    return
end %if

y_data_out = y_data_in(truncation_point_start:truncation_point_end + truncation_point_start - 1);
x_data_out = x_data_in(truncation_point_start:truncation_point_end + truncation_point_start - 1);

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
