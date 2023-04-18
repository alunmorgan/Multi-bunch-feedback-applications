function chromaticity_plotting_overlay(sb_chro_loc, mc_chro_loc)
% Compares and plots the data from the measchro routine and the new
% chromaticity measurements from sidebands.
%
% Example: chromaticity_plotting_overlay('/chromaticity_from_sidebands', fullfile('ops-physics', 'chrodata'))

sb_chro_files = dir_list_gen(sb_chro_loc, 'mat', 1);

sb_chro =load(sb_chro_files{1});
for se = 2:length(sb_chro_files)
    temp = load(sb_chro_files{se});
    sb_chro.chro_time = cat(2, sb_chro.chro_time, temp.chro_time);
    sb_chro.chro_x_mean = cat(2, sb_chro.chro_x_mean, temp.chro_x_mean);
    sb_chro.chro_y_mean = cat(2, sb_chro.chro_y_mean, temp.chro_y_mean);
    sb_chro.chro_x_std = cat(2, sb_chro.chro_x_std, temp.chro_x_std);
    sb_chro.chro_y_std = cat(2, sb_chro.chro_y_std, temp.chro_y_std);
end %for

% Ensuring that the data is acending time order.
[~,I] = sort(sb_chro.chro_time);
sb_chro.chro_x_time = sb_chro.chro_time(I);
sb_chro.chro_y_time = sb_chro.chro_time(I);
sb_chro.chro_x_mean = sb_chro.chro_x_mean(I);
sb_chro.chro_y_mean = sb_chro.chro_y_mean(I);
sb_chro.chro_x_std = sb_chro.chro_x_std(I);
sb_chro.chro_y_std = sb_chro.chro_y_std(I);

cmx = find(abs(sb_chro.chro_x_mean) <100);
sb_chro.chro_x_mean = sb_chro.chro_x_mean(cmx);
sb_chro.chro_x_std = sb_chro.chro_x_std(cmx);
sb_chro.chro_x_time = sb_chro.chro_x_time(cmx);

cmy = find(abs(sb_chro.chro_y_mean) <100);
sb_chro.chro_y_mean = sb_chro.chro_y_mean(cmy);
sb_chro.chro_y_std = sb_chro.chro_y_std(cmy);
sb_chro.chro_y_time = sb_chro.chro_y_time(cmy);

cmx = find(abs(sb_chro.chro_x_std) <1);
sb_chro.chro_x_mean = sb_chro.chro_x_mean(cmx);
sb_chro.chro_x_std = sb_chro.chro_x_std(cmx);
sb_chro.chro_x_time = sb_chro.chro_x_time(cmx);

cmy = find(abs(sb_chro.chro_y_std) <1);
sb_chro.chro_y_mean = sb_chro.chro_y_mean(cmy);
sb_chro.chro_y_std = sb_chro.chro_y_std(cmy);
sb_chro.chro_y_time = sb_chro.chro_y_time(cmy);

mc_chro_files = dir_list_gen_tree(mc_chro_loc, 'mat', 1);
chro_ind = find_position_in_cell_lst(strfind(mc_chro_files, fullfile('Chromaticity','Chro_')));
mc_chro_files = mc_chro_files(chro_ind);

% generate a list of times generated from the filenames
for wh = 1:length(mc_chro_files)
    [~, temp_name, ~] = fileparts(mc_chro_files{wh});
    file_dates(wh) = datenum(temp_name(6:end), 'yyyy-mm-dd_HH-MM-SS');
end %for
inds1 = find(file_dates >  sb_chro.chro_time(1));
inds2 = find(file_dates <  sb_chro.chro_time(end));
inds3 = intersect(inds1, inds2);
mc_chro_files = mc_chro_files(inds3);
for kje = 1:length(mc_chro_files)
    mc_temp = load(mc_chro_files{kje});
    mc_chro_x(kje) = abs(mc_temp.Chromaticity.Data(1));
    mc_chro_y(kje) = abs(mc_temp.Chromaticity.Data(2));
    mc_chro_time(kje) = datenum(mc_temp.Chromaticity.TimeStamp);
    clear mc_temp
end %for


figure;
sb1 = subplot(2,1,1);
errorbar(sb_chro.chro_x_time, sb_chro.chro_x_mean, sb_chro.chro_x_std, 'ko')
if inds3 ~= 0
    hold on
    plot(mc_chro_time, mc_chro_x, 'r*')
    hold off
end %if
ylim([0 10])
grid on
title('Chromaticity X')
datetick('x', 'keeplimits')
sb2 = subplot(2,1,2);
errorbar(sb_chro.chro_y_time, sb_chro.chro_y_mean, sb_chro.chro_y_std, 'ko')
if inds3 ~= 0
    hold on
    plot(mc_chro_time, mc_chro_y, 'r*')
    hold off
end %if
ylim([0 10])
grid on
title('Chromaticity Y')
datetick('x', 'keeplimits')
linkaxes([sb1, sb2], 'x')
disp('')