function  [s, delta, p] = mbf_growdamp_advanced_fitting(data, length_averaging)

mm = movmean(abs(data), length_averaging);
% Get an initial starting value.
p_initial = polyfit(1:length(mm), mm, 1);
if p_initial(1) < 0
    % damping
    % find the max so as to allow any initial rise in the data to be
    % removed.
    [~,dm_loc] = max(mm);
    dm_loc = 2 * dm_loc;
else
    %growth
    dm_loc = 0;
end %if
x_ax = 0:length(mm)-1 - dm_loc;
n_tests = 200;
% compare linear fits to the data.
vals = linspace(p_initial(1), p_initial(1) - 2e-7, n_tests);
% sweep the gradient. Large changes in sample length indicate that a large
% fraction of the line has moved from below the line to above it.
for gra = 1:n_tests
    y = vals(gra) * x_ax + mm(dm_loc + 1);
    weighted_error = (mm(dm_loc+1:end) - y);% .* linspace(length(mm)-1 - dm_loc, 0 , length(mm)-dm_loc);
    weighted_error(weighted_error >0) = 0;
    [~, min_loc] = min(weighted_error);
    sample_length_temp = find(weighted_error(min_loc:end) == 0, 1, 'first');
    if isempty(sample_length_temp)
        sample_length(gra) = length(x_ax);
    else
        sample_length(gra) = sample_length_temp + min_loc - 1;
    end %if
    if sample_length(gra) < 3
        break
    end %if
end %if
% figure(4)
% plot(diff(sample_length))

[~, I] = min(diff(sample_length));
if I ~= 1
    I = I-1;
end %if
s = [vals(I), mm(dm_loc + 1)];
c = polyval(s,1:length(mm));
delta = mean(abs(c - log(abs(data)))./c);
temp = unwrap(angle(data)) / (2*pi);
p = polyfit(1:length(mm),temp,1);
% figure(3)
% plot(0:length(mm) -1, abs(data), 'b')
% hold all
% plot([0:dm_loc-1, x_ax + dm_loc], mm, 'r')
% plot(x_ax + dm_loc, p_initial(1) * x_ax + p_initial(2), 'm')
% plot(x_ax + dm_loc, vals(I) * x_ax + mm(dm_loc + 1), 'g')
% ylim([0 inf])
% hold off
% disp('')