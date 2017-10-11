function varargout = mbf_growdamp_capture(mbf_axis, tune)
% wrapper function to call growdamp, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Usually the fractional tune of the machine. 
%
% example growdamp = mbf_growdamp_capture('x', 0.17)

if ~strcmpi(mbf_axis,'x') && ~strcmpi(mbf_axis,'y') && ~strcmpi(mbf_axis,'s')
 error('mbf_growdamp_capture: Incorrect value axis given (should be x, y or s)');
end

[root_string, ~] = mbf_system_config;
settings = mbf_growdamp_config(mbf_axis);
% Generate the base PV name.
pv_head = ax2dev(settings.axis_number);
% getting general environment data.
growdamp = machine_environment;
% Add the axis label to the data structure.
growdamp.ax_label = settings.axis_label;
% construct name and add it to the structure
growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis'];

% set tune, should only be required on excitation (state 4), but do it on
% all just in case someone makes a big jump!
for n=2:4
    mbf_get_then_put([pv_head ':SEQ:',num2str(n),':START_FREQ_S'], tune);
end

% Getting the number of turns of growth, natural damping, and active
% damping.
growdamp.growth_turns = lcaGet([pv_head ':SEQ:4:COUNT_S']);
growdamp.nat_turns = lcaGet([pv_head ':SEQ:3:COUNT_S']);
growdamp.act_turns = lcaGet([pv_head ':SEQ:2:COUNT_S']);

% Getting the number of turns each point dwells at, for growth,
%natural damping, and active damping.
growdamp.growth_dwell = lcaGet([pv_head ':SEQ:4:DWELL_S']);
growdamp.nat_dwell = lcaGet([pv_head ':SEQ:3:DWELL_S']);
growdamp.act_dwell = lcaGet([pv_head ':SEQ:2:DWELL_S']);

% Getting the number of turns each point dwells at, for growth,
%natural damping, and active damping.
growdamp.growth_gain = lcaGet([pv_head ':SEQ:4:GAIN_S']);
growdamp.nat_gain = lcaGet([pv_head ':SEQ:3:GAIN_S']);
growdamp.act_gain = lcaGet([pv_head ':SEQ:2:GAIN_S']);

% Trigger the measurement

while 1==1
    output = mbf_IQ_measurement(settings.axis_number);
    % check we don't have an overflow or too little IQ data, adjust fixed IQ
    % gain accordingly.
    datamax=max(abs(output));
    gain_pv = [pv_head ':DET:GAIN_S'];
    gain = lcaGet(gain_pv, 1, 'double');
    overflow_pv = [pv_head ':DDR:OVF:IQ'];
    overflow_state = lcaGet(overflow_pv, 1 , 'double');
    if overflow_state == 1
        if gain < 7
            mbf_get_then_put(gain_pv, gain+1);
            warning('IQ overflow, detector gain has been adjusted, capturing again!')
        else
            error('too much signal at maximum attenuation!')
        end
    elseif datamax<4000
        if gain > 0
            mbf_get_then_put(gain_pv, gain-1);
            warning('IQ weak, detector gain has been adjusted, capturing again!')
        else
            warning('very small signal at minimum attenuation!')
            growdamp.data = output;
            break
        end
    else
        growdamp.data = output;
        break
    end
end

%% saving the data to a file
save_to_archive(root_string, growdamp)

if nargout == 1
    varargout{1} = growdamp;
end %if

