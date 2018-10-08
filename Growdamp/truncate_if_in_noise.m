function [data] = truncate_if_in_noise(data, length_averaging)
% truncating the data if it falls into the noise
figure(3)
mm = movmean(abs(data), length_averaging);
plot(abs(data), 'b')
hold all
plot(mm, 'r')
temp = find(diff(mm) > 0);
f2 = temp(find(diff(temp)==1, 1, 'first'));
if ~isempty(f2)
    data = data(1:f2);
    plot(f2,0, 'm*')
end %if
hold off
disp('')
