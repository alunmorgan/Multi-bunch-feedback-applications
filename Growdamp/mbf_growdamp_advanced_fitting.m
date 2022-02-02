function  [s, delta, p] = mbf_growdamp_advanced_fitting(data, length_averaging, debug)


temp = unwrap(angle(data)) / (2*pi);
p = polyfit(1:length(data),temp,1);

mm = movmean(abs(data), length_averaging);
%take the log of the data as we expect an exponential decay. meaning that the
%log(data) should be linear
mm = log(abs(mm));
% Get an initial starting value.
p_initial = polyfit(1:length(mm), mm, 1);
initial_fit_line = polyval(p_initial, 1:length(mm));
if p_initial(1) < 0
    % damping
    % find the max so as to allow any initial rise in the data to be
    % removed.
    [~,dm_loc] = max(mm);
%     dm_loc = 2 * dm_loc;
else
    %growth
    dm_loc = 0;
end %if
x_ax = 0:length(mm)-1 - dm_loc;

if debug == 1 && p_initial(1) < 0
    figure(3)
    plot(0:length(mm) -1, log(abs(data)), 'b', 'DisplayName', 'Raw data')
    hold all
    plot([0:dm_loc-1, x_ax + dm_loc], mm, 'r', 'DisplayName', 'Averaged data')
    plot(1:length(mm), initial_fit_line, 'm', 'DisplayName', 'initial fit')
%     plot(x_ax + dm_loc, p_initial(1) * x_ax + p_initial(2), 'm', 'DisplayName', 'initial fit')
%     ylim([0 inf])
    legend
    hold off
end %if

n_tests = 200;
% compare linear fits to the data.
vals = linspace(p_initial(1), p_initial(1) - 2e-7, n_tests);
% sweep the gradient. Large changes in sample length indicate that a large
% fraction of the line has moved from below the line to above it.
sample_length = NaN(n_tests,1);
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
if debug == 1 && p_initial(1) < 0
    figure(4)
    plot(diff(sample_length),'*')
end %if
[~, I] = min(diff(sample_length));
if I ~= 1
    I = I-1;
end %if
s = [vals(I), mm(dm_loc + 1)];
c = polyval(s,1:length(mm));
delta = mean(abs(c - log(abs(data)))./c);

if debug == 1 && p_initial(1) < 0
    figure(3)
    hold all
    plot(1:length(mm), c, 'g', 'DisplayName', 'final fit')
%     ylim([0 inf])
    hold off
    test1 = mm-initial_fit_line;
    test2 = mm-c;
    figure(5)
    plot(1:length(mm), test1, 1:length(mm), test2)
end %if
% disp('')