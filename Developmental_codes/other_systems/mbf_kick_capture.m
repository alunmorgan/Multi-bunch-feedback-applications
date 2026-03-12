function mbf_kick_capture
tic
[data.bpm_names, ~,~] = fa_id2name(1:173);
[temp_names, ~,~] = fa_id2name(181:183);
data.bpm_names = cat(2, data.bpm_names, temp_names);
data.capture_length = 2000;
data.n_turns = 2000;
data.start_time = now;
data.sweep_settings = {'-18','-12', '-6', '-3','-1','0'};
data.sweep_type = 'log';
data.sweep_settings_lab = regexprep(data.sweep_settings, '-', 'm');
data.sweep_settings_val = str2double(data.sweep_settings);
% Setup the EBPMs for capture
BPM_TbT_capture_setup(data.bpm_names, data.capture_length)

for nd = 1:length(data.sweep_settings)
    disp(['Starting capture with NCO gain ',data.sweep_settings{nd}])
    if strcmp(data.sweep_type, 'log')
        lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', data.sweep_settings{nd})
    elseif strcmp(data.sweep_type, 'lin')
        lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_SCALAR_S', data.sweep_settings{nd})
    else
        error('Sweep type needs to be log or lin.')
    end %if
    pause(2)
    temp = lcaGet({'SR-DI-DCCT-01:SIGNAL';'SR-DI-PICO-02:BUCKETS_180'; ...
        'SR23C-DI-TMBF-01:Y:ADC:MMS:MAX';...
        'SR23C-DI-TMBF-01:Y:ADC:MMS:MIN'; 'SR23C-DI-TMBF-01:Y:ADC:MMS:DELTA';...
        'SR23C-DI-TMBF-01:Y:ADC:MMS:MEAN'; 'SR23C-DI-TMBF-01:Y:ADC:MMS:STD'; ...
        'SR23C-DI-TMBF-01:X:ADC:MMS:MAX';...
        'SR23C-DI-TMBF-01:X:ADC:MMS:MIN'; 'SR23C-DI-TMBF-01:X:ADC:MMS:DELTA';...
        'SR23C-DI-TMBF-01:X:ADC:MMS:MEAN'; 'SR23C-DI-TMBF-01:X:ADC:MMS:STD'});
    data.current(nd,:) = temp(1,:);
    data.fill_pattern(nd,:) = temp(2,:);
    data.MBF.ADC.maxy(nd,:) = temp(3,:);
    data.MBF.ADC.miny(nd,:) = temp(4,:);
    data.MBF.ADC.diffy(nd,:) = temp(5,:);
    data.MBF.ADC.meany(nd,:) = temp(6,:);
    data.MBF.ADC.stdy(nd,:) = temp(7,:);
    data.MBF.ADC.maxx(nd,:) = temp(8,:);
    data.MBF.ADC.minx(nd,:) = temp(9,:);
    data.MBF.ADC.diffx(nd,:) = temp(10,:);
    data.MBF.ADC.meanx(nd,:) = temp(11,:);
    data.MBF.ADC.stdx(nd,:) = temp(12,:);
    clear temp
    BPM_TbT_capture_arm(data.bpm_names)
    pause(0.2)
    data.BPM.TBT{nd} = BPM_TbT_get_data(data.bpm_names, data.n_turns,...
        'capture_stats', 'yes', 'all_waveforms', 'no');
%     for hwa = 1:30
%         data.emittance(nd, hwa) = lcaGet('SR-DI-EMIT-01:VEMIT');
%         data.emittance_status{nd, hwa} = lcaGet('SR-DI-EMIT-01:STATUS');
%         pause(0.3)
%     end %for
end %for
data.end_time = now;
save(['/scratch/afdm76/MBF_EBPM_cal_nco_sweep'...
    ,datestr(data.start_time, 'yyyymmddTHHMMSS'),'.mat'],...
    'data', '-v7.3')

disp('')
ebpms_to_plot = {'SR24C_DI_EBPM_01', 'SR24C_DI_EBPM_07', 'SR24C_DI_EBPM_04'};
ebpm{1} = gather_ebpm_data(data.BPM.TBT, ebpms_to_plot{1});
ebpm{2} = gather_ebpm_data(data.BPM.TBT, ebpms_to_plot{2});
ebpm{3} = gather_ebpm_data(data.BPM.TBT, ebpms_to_plot{3});
figure(394853)
tiledlayout('flow')
nexttile
plot(str2double(data.sweep_settings), max(data.MBF.ADC.maxx, [],2), 'DisplayName', 'MBF signal max')
hold on
plot(str2double(data.sweep_settings), max(data.MBF.ADC.minx, [],2), 'DisplayName', 'MBF signal min')
plot(str2double(data.sweep_settings), max(data.MBF.ADC.meanx, [],2), 'DisplayName', 'MBF signal mean')
title('MBF X signal')
legend
nexttile
plot(str2double(data.sweep_settings), max(data.MBF.ADC.stdx, [],2), 'DisplayName', 'MBF signal std')
title('MBF X signal std')
legend
nexttile
plot(str2double(data.sweep_settings), max(data.MBF.ADC.maxy, [],2), 'DisplayName', 'MBF signal max')
hold on
plot(str2double(data.sweep_settings), max(data.MBF.ADC.miny, [],2), 'DisplayName', 'MBF signal min')
plot(str2double(data.sweep_settings), max(data.MBF.ADC.meany, [],2), 'DisplayName', 'MBF signal mean')
title('MBF Y signal')
legend
nexttile
plot(str2double(data.sweep_settings), max(data.MBF.ADC.stdy, [],2), 'DisplayName', 'MBF signal std')
title('MBF Y signal std')
legend
for kw = 1:length(ebpm)
    nexttile
    plot(str2double(data.sweep_settings), ebpm{kw}.maxx, 'DisplayName', 'EBPM signal max')
    hold on
    plot(str2double(data.sweep_settings), ebpm{kw}.minx, 'DisplayName', 'EBPM signal min')
    plot(str2double(data.sweep_settings), ebpm{kw}.meanx, 'DisplayName', 'EBPM signal meanx')
    hold off
    title(['EBPM X signal (', ebpms_to_plot{kw},')'], 'Interpreter','none')
    legend
    nexttile
    plot(str2double(data.sweep_settings), ebpm{kw}.stdx, 'DisplayName', 'EBPM signal std')
    title(['EBPM X std (', ebpms_to_plot{kw},')'], 'Interpreter','none')
    nexttile
    plot(str2double(data.sweep_settings), ebpm{kw}.maxy, 'DisplayName', 'EBPM signal max')
    hold on
    plot(str2double(data.sweep_settings), ebpm{kw}.miny, 'DisplayName', 'EBPM signal min')
    plot(str2double(data.sweep_settings), ebpm{kw}.meany, 'DisplayName', 'EBPM signal meanx')
    hold off
    title(['EBPM Y signal (', ebpms_to_plot{kw},')'], 'Interpreter','none')
    legend
    nexttile
    plot(str2double(data.sweep_settings), ebpm{kw}.stdy, 'DisplayName', 'EBPM signal std')
    title(['EBPM Y std (', ebpms_to_plot{kw},')'], 'Interpreter','none')
end %for
toc
%
% disp('')
% % Grab data from the fast archiver
% pause(10) % Give the archiver time to process the live data.
% time_range = {datestr(data.start_time, 'yyyymmddTHHMMSS'),...
%     datestr(data.end_time, 'yyyymmddTHHMMSS')};
% pv_data = fa_archive_EBPM_grab(time_range);
% save(['/scratch/afdm76/MBF_EBPM_cal_EBPM_fast_data', datestr(data.start_time, 'yyyymmddTHHMMSS')],...
%     "pv_data", '-v7.3')
% figure(394853)
% tiledlayout('flow')
% nexttile
% plot(pv_data.timestamp, squeeze(pv_data.data(1,167,:)))
% title('EBPM X data')
% xlabel('time')
% nexttile
% plot(pv_data.timestamp, squeeze(pv_data.data(2,167,:)))
% title('EBPM Y data')
% xlabel('time')
end %fuction

function out = gather_ebpm_data(ebpm_data, ebpm_name)
% input is a cell array of identical structures.
for ks = 1:length(ebpm_data)
    out.maxy(ks) = ebpm_data{ks}.(ebpm_name).maxy;
    out.maxx(ks) = ebpm_data{ks}.(ebpm_name).maxx;
    out.miny(ks) = ebpm_data{ks}.(ebpm_name).miny;
    out.minx(ks) = ebpm_data{ks}.(ebpm_name).minx;
    out.meany(ks) = ebpm_data{ks}.(ebpm_name).meany;
    out.meanx(ks) = ebpm_data{ks}.(ebpm_name).meanx;
    out.stdy(ks) = ebpm_data{ks}.(ebpm_name).stdy;
    out.stdx(ks) = ebpm_data{ks}.(ebpm_name).stdx;
end %for
end %function


