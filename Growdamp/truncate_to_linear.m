function [data_out] = truncate_if_in_noise(data_in, length_averaging, n_tests)
% truncating the data if it falls into the noise
if nargin < 3
    n_tests = 100;
end %if

% try
% reduce the high frequency noise.
data_in = cat(2, data_in, repmat(mean(abs(data_in(end-10:end))),1,1000)); % TEMP FOR TESTING ONLY
mm = movmean(abs(data_in), length_averaging);
p = polyfit(1:length(mm), mm, 1);
figure(1)
clf
subplot(2,1,1)
hold all
plot(abs(data_in),'b')
plot(mm, 'r')
plot(polyval(p,linspace(1,length(data_in), length(data_in))), 'g')
hold off

if p(1) > 0
    %growth
    data_out = data_in;
    return
end %if

for gra = n_tests:-1:1
    ind(gra) = floor(length(mm).* gra / n_tests);
    y = mm(1:ind(gra));
    x = 1:length(y);
    [p, S] = polyfit(x, y, 1);
    [~,  delta] = polyval(p, x, S);
    overall_error(gra) = sum(abs(delta)) ./ length(delta);
    if ind(gra) < 100
        ind = ind(gra:end);
        overall_error = overall_error(gra:end);
        break
    end %if
end %for
[~, x_of_min] = min(overall_error);
truncation_point = ind(x_of_min);

% figure(1)
% subplot(2,1,1)
% hold all
% plot(truncation_point, mm(truncation_point), 'oc')
% hold off
% subplot(2,1,2)
% hold all
% plot(abs(data_in(1:truncation_point)),'b')
% plot(mm(1:truncation_point), 'r')
% p = polyfit(1:truncation_point, mm(1:truncation_point), 1);
% plot(polyval(p,linspace(1,length(mm(1:truncation_point)), truncation_point)), 'g')
% hold off

if truncation_point < 10
    disp('truncate_if_noise: Truncation would be too severe.  Returning original data.')
    data_out = data_in;
else
    data_out = data_in(1:truncation_point);
end %if
disp('')
% plot(0:length(mm) -1, abs(data_in), 'b')
% hold all
% plot([0:dm_loc-1, x_ax + dm_loc], mm, 'r')
% [~, I] = min(diff(fit_quality));
% if I ~= 1
%     I = I-1;
% end %if
% plot(x_ax + dm_loc, vals(I) * x_ax + mm(dm_loc), 'g')
% ylim([0 inf])
% hold off
%
% figure(4)
% plot(diff(fit_quality))
% title('fit quality - truncation')
% catch
%     data_out = data_in;
%     disp('truncate_if_in_noise: Unable to usefully operate. Returning original data.')
% end %try
