function output = mbf_bunch_motion_analysis(data)

x = reshape(data.x, data.num_buckets, []);
y = reshape(data.y, data.num_buckets, []);
z = reshape(data.z, data.num_buckets, []);

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

output.turn_of_peak = peak_col;
output.bucket_of_peak = peak_row -1;

output.mean_bunches_x = mean(x, 2);
output.mean_bunches_y = mean(y, 2);
output.mean_bunches_z = mean(z, 2);

output.std_bunches_x = std(x, 1, 2);
output.std_bunches_y = std(y, 1, 2);
output.std_bunches_z = std(z, 1, 2);

output.mean_turns_x = mean(x, 1)';
output.mean_turns_y = mean(y, 1)';
output.mean_turns_z = mean(z, 1)';

output.std_turns_x = std(x, 1, 1)';
output.std_turns_y = std(y, 1, 1)';
output.std_turns_z = std(z, 1, 1)';

output.x_norm = x;
output.y_norm = y;
output.z_norm = z;
