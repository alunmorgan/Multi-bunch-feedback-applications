function output = mbf_IQ_measurement(ax)
% Triggers a measument using the TMBF DDR buffer. Waits for the buffer to
% be ready, and then reads out the result.
% IQ data in this case.
%
% Example: output = mbf_IQ_measurement

mbf_get_then_put([ax2dev(ax) ':TRG:DDR:ARM_S.PROC'],1);
% could wait for busy then ready
% while ~strcmp(lcaGet([ax2dev(ax) ':DDR:STATUS']),'Busy')
%     pause(.2)
%     fprintf('.')
%     lcaGet([ax2dev(ax) ':DDR:STATUS'])
% end
pause(3)
disp('after pause')
%% Wait for DDR buffer ready, then read out.
while ~strcmp(lcaGet([ax2dev(ax) ':TRG:DDR:STATUS']),'Ready')
    pause(.2)
    fprintf('.')   
end
fprintf('\n')

pause(1)
% while ~strcmp(lcaGet([ax2dev(ax) ':DDR:STATUS']),'Ready')
%     pause(.2)
%     fprintf('.')   
% end
% fprintf('\n')
output = tmbf_read_iq(ax2dev(ax));