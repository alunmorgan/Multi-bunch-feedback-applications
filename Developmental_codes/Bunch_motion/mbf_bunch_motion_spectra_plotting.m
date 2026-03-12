function mbf_bunch_motion_spectra_plotting(data)

xt = reshape(data.x, data.num_buckets, []);
yt = reshape(data.y, data.num_buckets, []);
zt = reshape(data.z, data.num_buckets, []);

n_turns = size(xt, 2);
bucket_numbers = 0:data.num_buckets-1;
turn_numbers = 1:n_turns;

T = 1; %turns Sampling period
Fs = 1/T; %Sampling frequency
f_scale = Fs*(0:(n_turns/2))/n_turns;

% Normalise each bunch signal to the average of the first 100 turns
x_ref = repmat(mean(xt(:,1:100),2),1,length(turn_numbers));
y_ref = repmat(mean(yt(:,1:100),2),1,length(turn_numbers));
z_ref = repmat(mean(zt(:,1:100),2),1,length(turn_numbers));
xt = xt - x_ref;
yt = yt - y_ref;
zt = zt - z_ref;

x1 = fft(xt, [], 2);
x1 = abs(x1 ./ n_turns);
x = x1(:, 1:n_turns/2+1);
x(:, 2:end-1) = 2*x(:, 2:end-1);

y1 = fft(yt, [], 2);
y1 = abs(y1 ./ n_turns);
y = y1(:, 1:n_turns/2+1);
y(:, 2:end-1) = 2*y(:, 2:end-1);

z1 = fft(zt, [], 2);
z1 = abs(z1 ./ n_turns);
z = z1(:, 1:n_turns/2+1);
z(:, 2:end-1) = 2*z(:, 2:end-1);


% Find the location of the largest disturbance.
[maxx, maxindx] = max(x(:));
[peak_row_x, peak_col_x] = ind2sub(size(x), maxindx);
f_of_peak_x = f_scale(peak_col_x);
bucket_of_peak_x = peak_row_x -1;

[maxy, maxindy] = max(y(:));
[peak_row_y, peak_col_y] = ind2sub(size(y), maxindy);
f_of_peak_y = f_scale(peak_col_y);
bucket_of_peak_y = peak_row_y -1;

[maxz, maxindz] = max(z(:));
[peak_row_z, peak_col_z] = ind2sub(size(z), maxindz);
f_of_peak_z = f_scale(peak_col_z);
bucket_of_peak_z = peak_row_z -1;

[~,loc] = max([maxx, maxy, maxz]);
ax_labs = {'x', 'y', 'z'};

disp(['Axis with most disturbance is ' ax_labs{loc}])
disp(['Tune of main disturbance in x is ' num2str(f_of_peak_x)])
disp(['Bucket of main disturbance in x is ' num2str(bucket_of_peak_x)])
disp(['Tune of main disturbance in y is ' num2str(f_of_peak_y)])
disp(['Bucket of main disturbance in y is ' num2str(bucket_of_peak_y)])
disp(['Tune of main disturbance in z is ' num2str(f_of_peak_z)])
disp(['Bucket of main disturbance in z is ' num2str(bucket_of_peak_z)])

f1 = figure('OuterPosition',[20, 20, 1800 1000]);
t = tiledlayout(3,1);
title(t, data.filename, 'Interpreter', 'None')
ylabel(t, 'Bunches')
xlabel(t, 'Tune (1/Turns)')
ax2 = nexttile;
imagesc(f_scale, bucket_numbers, x)
title('Horizontal motion')
ax3 = nexttile;
imagesc(f_scale, bucket_numbers, y)
title('Vertical motion')
ax4 = nexttile;
imagesc(f_scale, bucket_numbers, z)
title('Longitudinal motion')
linkaxes([ax2, ax3, ax4],'xy')

f2 = figure('OuterPosition',[20, 20, 1800 1000]);
t = tiledlayout(3,1);
title(t, data.filename, 'Interpreter', 'None')
ylabel(t, 'Bunches')
xlabel(t, 'Tune (1/Turns)')
ax2 = nexttile;
plot(f_scale, abs(x(bucket_of_peak_x +1,:)))
title(['Horizontal motion (bucket ', num2str(bucket_of_peak_x), ')'])
ax3 = nexttile;
plot(f_scale, abs(y(bucket_of_peak_y +1,:)))
title(['Vertical motion (bucket ', num2str(bucket_of_peak_y), ')'])
ax4 = nexttile;
plot(f_scale, abs(z(bucket_of_peak_z +1,:)))
title(['Longitudinal motion (bucket ', num2str(bucket_of_peak_z), ')'])
linkaxes([ax2, ax3, ax4],'xy')
% 
% figure(f2) % Sometimes matlab has a delay plotting the previous plot and this breaks everything.
% ax4 = nexttile(4);
% imagesc(turn_numbers, bucket_numbers, y)
% title('Vertical motion')
% colorbar
% ylabel('Bunches')
% 
% figure(f2)
% ax7 = nexttile(7);
% imagesc(turn_numbers, bucket_numbers, z)
% title('Longitudinal motion')
% colorbar
% ylabel('Bunches')
% linkaxes([ax1 ax4 ax7], 'xy')
% 
% figure(f2)
% nexttile(2)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(x(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% legend('Location','northoutside', 'NumColumns', 2)
% title('Horizontal motion')
% grid on
% 
% figure(f2)
% nexttile(5)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(y(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% title('Vertical motion')
% grid on
% 
% figure(f2)
% nexttile(8)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(z(selected_bunches(sje) +1, :), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% title('Longitudinal motion')
% grid on
% 
% figure(f2)
% nexttile(3)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(selected_turns, x(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% legend('Location','northoutside', 'NumColumns', 2)
% title('Horizontal motion')
% grid on
% 
% figure(f2)
% nexttile(6)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(selected_turns, y(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% title('Vertical motion')
% grid on
% 
% figure(f2)
% nexttile(9)
% hold on
% for sje = 1:length(selected_bunches)
%     plot(selected_turns, z(selected_bunches(sje) +1, selected_turns), 'DisplayName', ['Bunch ', num2str(selected_bunches(sje))])
% end %for
% title('Longitudinal motion')
% grid on
% 
% saveas(f1, [data.filename, '_bunches'], 'png')
% saveas(f2, [data.filename, '_turns'], 'png')
% close(f1)
% close(f2)