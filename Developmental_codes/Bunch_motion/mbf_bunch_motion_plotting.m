function mbf_bunch_motion_plotting(data, metadata, selected_bunches, selected_turns)

x = reshape(data.x, data.num_buckets, []);
y = reshape(data.y, data.num_buckets, []);
z = reshape(data.z, data.num_buckets, []);

bucket_numbers = 0:data.num_buckets-1;
turn_numbers = 1:size(x, 2);

% Normalise each bunch signal to the average of the first 100 turns
x_ref = repmat(mean(x(:,1:100),2),1,length(turn_numbers));
y_ref = repmat(mean(y(:,1:100),2),1,length(turn_numbers));
z_ref = repmat(mean(z(:,1:100),2),1,length(turn_numbers));
x = x - x_ref;
y = y - y_ref;
z = z - z_ref;

% Find the location of the largest disturbance.
[minx, minindx] = min(x(:));
[maxx, maxindx] = max(x(:));
[miny, minindy] = min(y(:));
[maxy, maxindy] = max(y(:));
[minz, minindz] = min(z(:));
[maxz, maxindz] = max(z(:));

[~,loc] = max([abs(minx), maxx, abs(miny), maxy, abs(minz), maxz]);
indexes = [minindx, maxindx, minindy, maxindy, minindz, maxindz];
index_of_peak = indexes(loc);
[peak_row, peak_col] = ind2sub(size(x), index_of_peak);
turn_of_peak = peak_col;
bucket_of_peak = peak_row -1;
disp(['Start turn of kick is ' num2str(turn_of_peak)])
disp(['Main bucket kicked ' num2str(bucket_of_peak)])
fill_pattern = data.fill_pattern2;

% xlimits = [minx maxx];
% ylimits = [miny maxy];
% zlimits = [minz maxz];
% max_fp = max(fill_pattern);
% charge_scale = fill_pattern ./ max_fp;
% for js = 1:data.num_buckets
%     warning('off','all')
%     shp3 = alphaShape(double(cat(2,squeeze(z(js,:))', squeeze(x(js,:))', ...
%         squeeze(y(js,:))')));
%     warning('on','all')
%     plot(shp3, 'FaceAlpha', charge_scale(js), 'EdgeAlpha', 0  ,...
%         'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
%         'Parent', ax1)
% end %for
% axis(ax1, [zlimits(1) zlimits(2) xlimits(1) xlimits(2) ylimits(1) ylimits(2)])
% view(ax1, 30, 30)
% title({'Red -> Blue along bunch train', 'alpha ~ bunch charge'})
% ylabel(ax1, 'Horizontal')
% zlabel(ax1, 'Vertical')
% xlabel(ax1, 'Beam direction')
% grid on
meanx = mean(x, 2);
meany = mean(y, 2);
meanz = mean(z, 2);

stdx = std(x, 1, 2);
stdy = std(y, 1, 2);
stdz = std(z, 1, 2);

f1 = figure('OuterPosition',[20, 20, 1800 1000]);
t = tiledlayout(4,1);
title(t, data.filename, 'Interpreter', 'None')
xlabel(t, 'Bunches')
ax1 = nexttile;
plot(bucket_numbers, fill_pattern)
ylabel('Charge')
grid on
ax2 = nexttile;
hold on
plot(bucket_numbers, meanx, 'k', 'LineWidth', 2, 'DisplayName','Mean motion over all turns')
plot(bucket_numbers, meanx + stdx, 'm', 'DisplayName','Std motion over all turns')
plot(bucket_numbers, meanx - stdx, 'm', 'HandleVisibility','off')
title('Horizontal motion')
ylabel('Motion')
legend
grid on
ax3 = nexttile;
hold on
plot(bucket_numbers, meany, 'k', 'LineWidth', 2, 'DisplayName','Mean motion over all turns')
plot(bucket_numbers, meany + stdy, 'm', 'DisplayName','Std motion over all turns')
plot(bucket_numbers, meany - stdy, 'm', 'HandleVisibility','off')
title('Vertical motion')
ylabel('Motion')
legend
grid on
ax4 = nexttile;
hold on
plot(bucket_numbers, meanz, 'k', 'LineWidth', 2, 'DisplayName','Mean motion over all turns')
plot(bucket_numbers, meanz + stdz, 'm', 'DisplayName','Std motion over all turns')
plot(bucket_numbers, meanz - stdz, 'm', 'HandleVisibility','off')
title('Longitudinal motion')
ylabel('Motion')
legend
grid on
linkaxes([ax1, ax2, ax3, ax4],'x')

f2 = figure('OuterPosition',[20, 20, 1800 1000]);
t = tiledlayout(3,3);
title(t, data.filename, 'Interpreter', 'None')
xlabel(t, 'Turns')
ax1 = nexttile(1);
imagesc(turn_numbers, bucket_numbers, x)
title('Horizontal motion')
ylabel('Bunches')
colorbar

figure(f2) % Sometimes matlab has a delay plotting the previous plot and this breaks everything.
ax4 = nexttile(4);
imagesc(turn_numbers, bucket_numbers, y)
title('Vertical motion')
colorbar
ylabel('Bunches')

figure(f2)
ax7 = nexttile(7);
imagesc(turn_numbers, bucket_numbers, z)
title('Longitudinal motion')
colorbar
ylabel('Bunches')
linkaxes([ax1 ax4 ax7], 'xy')

figure(f2)
nexttile(2)
hold on
for sje = 1:length(selected_bunches)
    plot(x(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Horizontal motion')
grid on

figure(f2)
nexttile(5)
hold on
for sje = 1:length(selected_bunches)
    plot(y(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
title('Vertical motion')
grid on

figure(f2)
nexttile(8)
hold on
for sje = 1:length(selected_bunches)
    plot(z(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
title('Longitudinal motion')
grid on

figure(f2)
nexttile(3)
hold on
for sje = 1:length(selected_bunches)
    plot(selected_turns, x(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Horizontal motion')
grid on

figure(f2)
nexttile(6)
hold on
for sje = 1:length(selected_bunches)
    plot(selected_turns, y(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
title('Vertical motion')
grid on

figure(f2)
nexttile(9)
hold on
for sje = 1:length(selected_bunches)
    plot(selected_turns, z(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
title('Longitudinal motion')
grid on

saveas(f1, [data.filename, '_bunches'], 'png')
saveas(f2, [data.filename, '_turns'], 'png')
% close(f1)
% close(f2)