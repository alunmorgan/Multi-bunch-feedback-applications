function [data] = truncate_if_in_noise(data, length_averaging)
% truncating the data if it falls into the noise

mm = movmean(abs(data), length_averaging);
p = polyfit(1:length(mm), mm, 1);
if p(1) < 0
    % damping
[~,dm_loc] = max(mm);
dm_loc = 2 * dm_loc;
else
    %growth
    dm_loc = 0;
end %if
x_ax = 0:length(mm)-1 - dm_loc;
n_tests = 200;

vals = linspace(p(1), p(1) - 2e-7, n_tests);
for gra = 1:n_tests
    y = vals(gra) * x_ax + mm(dm_loc);
    weighted_error = (mm(dm_loc+1:end)-y) .* linspace(length(mm)-1 - dm_loc, 0 , length(mm)-dm_loc);
    weighted_error(weighted_error >0) = 0;
    [fit_quality(gra), min_loc] = min(weighted_error);
    sample_length = find(weighted_error(min_loc:end) == 0, 1, 'first');
    sample_length = sample_length + min_loc - 1;
    fit_quality(gra) = fit_quality(gra) ./ sample_length;
    if sample_length < 3
        break
    end %if
%     figure(6)
%     hold all
%     plot(weighted_error)
%     hold off
end %if
figure(3)
plot(0:length(mm) -1, abs(data), 'b')
hold all
plot([0:dm_loc-1, x_ax + dm_loc], mm, 'r')
[~, I] = min(diff(fit_quality));
if I ~= 1
    I = I-1;
end %if
    
plot(x_ax + dm_loc, vals(I) * x_ax + mm(dm_loc), 'g')
ylim([0 inf])
hold off
figure(4)
plot(diff(fit_quality))
disp('')
