function growdamp_all(mbf_axis, varargin)
% Top level function to run the growdamp measurements on the
% selected plane
%   Args:
%       mbf_axis(str): 'x','y', or 's'
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       additional_save_location(str): fully defined filename to save the
%                                      captured data to in addition to the 
%                                      main archive.
%       excitation(str): sets whether the measurement uses an excitation to
%                        drive a resonance or if the measurement just uses the natural beam coupling.
%                        Defaults to 'yes'
%       excitation_location(str): The location of the excitation in tune space.
%                                 The default value is 'tune'.
%       excitation_manual(float): if excitation_location is set to 'manual' then
%                                 this defines the location of the excitation 
%                                 in tune space.
%       pll_tracking (str): Sets if the excitation frequency follows the tune
%                           jitter. Default is no
%       pll_bunches (float): bunches the pll is active on.
%       pll_guard_bunches (float): the number of bunches surrounding the pll
%                                  bunches for which feedback is switched off.
%       bunch_monitor(list(int)): This determines which bunches are monitored
%                                 during the measurement. Defaults to and array
%                                 of ones which means all bunches.
%       capture_full_bunch_motion(str): Captures the centroid motion for the 
%                                       duration of the measuremnt. 
%                                       Defaults to no as this is a lot of data. 
% Example: growdamp_all('x')

[root_string, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;

% for archival investigations this allows filtering by machine state.
% but for capture this is not needed so it set to empty.
filter_conditions = {};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
valid_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);
excitation_locations = {'tune', 'lower_sideband', 'upper_sideband', 'manual'};

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'excitation', 'yes',  @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'excitation_location', 'tune', @(x) any(validatestring(x,excitation_locations)));
addParameter(p, 'excitation_manual', 0, valid_number);
addParameter(p, 'pll_tracking', 'no', @(x) any(validatestring(x,boolean_string)));
addParameter(p, 'pll_bunches', 400, valid_number);
addParameter(p, 'pll_guard_bunches', 10, valid_number);
addParameter(p, 'bunch_monitor', ones(harmonic_number,1));
addParameter(p, 'capture_full_bunch_motion', 'no', @(x) any(validatestring(x,boolean_string)));

parse(p, mbf_axis, varargin{:});

%% Constructing the different states for the squencer. These will be arranged 
% in various configurations depending on the experiment requested.
%
% bank = 1 is Feedback off
% bank = 2 is Feedback on
%       tune_offset (float): Tune fraction to offset from the peak.
%       dwell (int): number of turns at each point.
%       durations (struct): number of points for each stage.
if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y')
    % Passive Growth
    growth.duration = 2500;
    growth.dwell = 1;
    growth.capture = 'Capture';
    growth.excitation = 'Off';
    growth.excitation_level = '-48dB';
    growth.bank = 1;

    % Excitation
    excitation.duration = 750;
    excitation.dwell = 1;
    excitation.capture = 'Capture';
    excitation.excitation = 'On';
    excitation.excitation_level = '-18dB';
    excitation.bank = 1;

    % Passive decay (assuming no instability)
    passive.duration = 1500;
    passive.dwell = 1;
    passive.capture = 'Capture';
    passive.excitation = 'Off';
    passive.excitation_level = '-48dB';
    passive.bank = 1;

    % Feedback active
    active.duration = 1500;
    active.dwell = 1;
    active.capture = 'Capture';
    active.excitation = 'Off';
    active.excitation_level = '-48dB';
    active.bank = 2;

    % Feedback active but no capture
    spacer.duration = 4000;
    spacer.dwell = 1;
    spacer.capture = 'Discard';
    spacer.excitation = 'Off';
    spacer.excitation_level = '-48dB';
    spacer.bank = 2;

    tune_offset = 0;
elseif strcmpi(mbf_axis, 's')
    growth.duration = 10;
    growth.dwell = 480;
    growth.capture = 'Capture';
    growth.excitation = 'Off';
    growth.excitation_level = '-48dB';
    growth.bank = 1;

    % Excitation
    excitation.duration = 10;
    excitation.dwell = 480;
    excitation.capture = 'Capture';
    excitation.excitation = 'On';
    excitation.excitation_level = '-18dB';
    excitation.bank = 1;

    % Passive decay (assuming no instability)
    passive.duration = 10;
    passive.dwell = 480;
    passive.capture = 'Capture';
    passive.excitation = 'Off';
    passive.excitation_level = '-48dB';
    passive.bank = 1;

    % Feedback active
    active.duration = 50;
    active.dwell = 480;
    active.capture = 'Capture';
    active.excitation = 'Off';
    active.excitation_level = '-48dB';
    active.bank = 2;

    % Feedback active but no capture
    spacer.duration = 100;
    spacer.dwell = 480;
    spacer.capture = 'Discard';
    spacer.excitation = 'Off';
    spacer.excitation_level = '-48dB';
    spacer.bank = 2;

    tune_offset = 0;
end %if

% getting general environment data.
growdamp = machine_environment;

%% Setting up the growdamp experiments.
if strcmp(p.Results.excitation, 'no')
    states{2} = growth;
    states{1} = active;
else
    states{6} = excitation;
    states{5} = passive;
    states{4} = spacer;
    states{3} = excitation;
    states{2} = active;
    states{1} = spacer;
    if strcmp(p.Results.excitation_location,'lower_sideband')
        excitation_tune = growdamp.tunes.([mbf_axis, '_tune']).lower_sideband...
            + tune_offset;
    elseif strcmp(p.Results.excitation_location,'upper_sideband')
        excitation_tune = growdamp.tunes.([mbf_axis, '_tune']).upper_sideband...
            + tune_offset;
    elseif strcmp(p.Results.excitation_location,'manual')
        excitation_tune = p.Results.excitation_manual;
    else
        excitation_tune = growdamp.tunes.([mbf_axis, '_tune']).tune...
            + tune_offset;
    end %if
end %if

% Add the extra data to the data structure.
growdamp.ax_label = mbf_axis;
growdamp.base_name = ['Growdamp_' mbf_axis '_axis'];
growdamp.harmonic_number = harmonic_number;
growdamp.excitation_location = p.Results.excitation_location;
growdamp.excitation_tune = excitation_tune;
growdamp.excitation_setting = p.Results.excitation;
growdamp.states = states;
growdamp.bunches_monitored = p.Results.bunch_monitor;

if strcmp(p.Results.auto_setup, 'yes')
    % Get the current FIR gain
    orig_fir_gain = get_variable([pv_head, Bunch_bank.FIR_gains]);
    % putting the system into a known state.
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)
end %if

growdamp.mbf_state = get_operational_mode(mbf_axis);

% Setup the MBF ready for the measurement.
mbf_growdamp_setup(mbf_axis, pv_names, trigger_inputs, harmonic_number...
    , states, excitation_tune, pll_setup,...
    p.Results.bunch_monitor);

% Capturing data.
captured_data = mbf_growdamp_capture(mbf_axis, pv_names,...
    p.Results.capture_full_bunch_motion);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    growdamp.(data_fields{je}) = captured_data.(data_fields{je});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)
end %if

%% saving the data to a file
save_to_archive(root_string, growdamp)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, growdamp)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_growdamp_archival_retrieval(mbf_axis, [growdamp.time growdamp.time],...
        filter_conditions)
end %if
