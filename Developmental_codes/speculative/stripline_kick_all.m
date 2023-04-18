function stripline_kick_all

% sets up a static kick on one axis of the MBF system
% triggers the kick and the TbT capture

%%%% ALL TOO SLOW
% % trig_time = now;
% % time_range = {datestr(trig_time - 0.5 / (24*3600), 'yyyymmddTHHMMSS'),...
% %               datestr(trig_time + 2 / (24*3600), 'yyyymmddTHHMMSS')};
% % % then grabs the FA_archive BPM data from just before the kick to just after the kick
% % pv_data = fa_archive_EBPM_grab(time_range,  '/scratch/afdm76/temp');
% % % plots the data
% % normalised_data = pv_data.data;
% % correction_data = repmat(mean(normalised_data(:,:,1:10),3),1,1,size(normalised_data,3));
% % normalised_data = normalised_data - correction_data;
% % figure;
% % hold on
% % for he = 1:size(normalised_data,2)
% %     
% %     plot(pv_data.t, squeeze(normalised_data(1,he,:)));
% % end
% % hold off
% % title('EBPM normalised horizontal signals')
% % figure;
% %     hold on
% % for he = 1:size(normalised_data,2)
% %     plot(pv_data.t, squeeze(normalised_data(2,he,:)));
% % end
% % hold off
% % title('EBPM normalised vertical signals')