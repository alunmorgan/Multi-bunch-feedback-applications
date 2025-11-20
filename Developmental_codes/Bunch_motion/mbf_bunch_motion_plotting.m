function mbf_bunch_motion_plotting(data, selected_bunches, selected_turns)


x = reshape(data.x, data.num_buckets, []);
y = reshape(data.y, data.num_buckets, []);
z = reshape(data.z, data.num_buckets, []);

% Normalise each bunch signal to the average of the first 100 turns
x_ref = mean(x(:,1:100),2);
y_ref = mean(y(:,1:100),2);
z_ref = mean(z(:,1:100),2);
x = x - x_ref;
y = y - y_ref;
z = z - z_ref;

xlimits = [min(x(:)) max(x(:))];
ylimits = [min(y(:)) max(y(:))];
zlimits = [min(z(:)) max(z(:))];

fill_pattern = data.fill_pattern;
max_fp = max(fill_pattern);
charge_scale = fill_pattern ./ max_fp;
% FIXME temp override
charge_scale = cat(1, ones(450, 1), zeros(936-450,1));

f1 = figure('OuterPosition',[20, 20, 800 800]);
t = tiledlayout(1,1);
title(t, data.filename, 'Interpreter', 'None')
ax1 = nexttile;
hold on
for js = 1:data.num_buckets
    warning('off','all')
    shp3 = alphaShape(double(cat(2,squeeze(z(js,:))', squeeze(x(js,:))', ...
        squeeze(y(js,:))')));
    warning('on','all')
    plot(shp3, 'FaceAlpha', charge_scale(js), 'EdgeAlpha', 0  ,...
        'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
        'Parent', ax1)
end %for
axis(ax1, [zlimits(1) zlimits(2) xlimits(1) xlimits(2) ylimits(1) ylimits(2)])
view(ax1, 30, 30)
title({'Red -> Blue along bunch train', 'alpha ~ bunch charge'})
ylabel(ax1, 'Horizontal')
zlabel(ax1, 'Vertical')
xlabel(ax1, 'Beam direction')
grid on

f2 = figure('OuterPosition',[20, 20, 1800 1000]);
t = tiledlayout(3,3);
title(t, data.filename, 'Interpreter', 'None')
nexttile(1)
imagesc(x)
title('Horizontal motion')
xlabel('Turns')
ylabel('Bunches')
colorbar

nexttile(4)
imagesc(y)
title('Vertical motion')
colorbar
xlabel('Turns')
ylabel('Bunches')

nexttile(7)
imagesc(z)
title('Longitudinal motion')
colorbar
xlabel('Turns')
ylabel('Bunches')

nexttile(2)
hold on
for sje = 1:length(selected_bunches)
    plot(x(selected_bunches(sje),:), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Horizontal motion')
xlabel('Turns')
grid on

nexttile(5)
hold on
for sje = 1:length(selected_bunches)
    plot(y(selected_bunches(sje),:), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Vertical motion')
xlabel('Turns')
grid on

nexttile(8)
hold on
for sje = 1:length(selected_bunches)
    plot(z(selected_bunches(sje),:), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Longitudinal motion')
xlabel('Turns')
grid on

nexttile(3)
hold on
for sje = 1:length(selected_turns)
    plot(selected_bunches, x(selected_bunches,selected_turns(sje)), 'DisplayName', ['Turn ', num2str(selected_turns(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Horizontal motion')
xlabel('Bunches')
grid on

nexttile(6)
hold on
for sje = 1:length(selected_turns)
    plot(selected_bunches, y(selected_bunches,selected_turns(sje)), 'DisplayName', ['Turn ', num2str(selected_turns(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Vertical motion')
xlabel('Bunches')
grid on

nexttile(9)
hold on
for sje = 1:length(selected_turns)
    plot(selected_bunches, z(selected_bunches,selected_turns(sje)), 'DisplayName', ['Turn ', num2str(selected_turns(sje))])
end %for
legend('Location','northoutside', 'NumColumns', 2)
title('Longitudinal motion')
xlabel('Bunches')
grid on

saveas(f1, [data.filename, '_3D'], 'png')
saveas(f2, data.filename, 'png')
% close(f1)
% close(f2)