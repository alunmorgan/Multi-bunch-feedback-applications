function varargout = pll_PI_scan(mbf_axis, p_vals, i_vals, varargin)
% This sets up the PLL loop for different P and I settings, then records various
% statistics in order to assess which setting are most suitable.

default_pll_monitor_bunches=400;
default_guardbunches = 10;

binary_string = {'yes', 'no'};
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
validScalarNum = @(x) isnumeric(x) && isscalar(x);
validNum = @(x) isnumeric(x);

addRequired(p, 'mbf_axis');
addRequired(p, 'p_vals');
addRequired(p, 'i_vals');
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'guardbunches', default_guardbunches, validScalarNum);
addParameter(p, 'pll_monitor_bunches', default_pll_monitor_bunches, validNum);
parse(p, mbf_axis, p_vals, i_vals, varargin{:});

[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
pv_head = pv_names.hardware_names.(mbf_axis);
pll_tails = pv_names.tails.pll;

% getting general environment data.
pll_data = machine_environment('tunes');
% Add the axis label to the data structure.
pll_data.ax_label = mbf_axis;
pll_data.base_name = ['PLL_', pll_data.ax_label, '_PI_scan'];

n_p = length(p_vals);
n_i = length(i_vals);
n_repeats = 20;
pll_data.minwf = NaN(n_p, n_i, n_repeats);
pll_data.maxwf = NaN(n_p, n_i, n_repeats);
pll_data.meanwf = NaN(n_p, n_i, n_repeats);
pll_data.stdwf = NaN(n_p, n_i, n_repeats);
pll_data.tunewf = NaN(n_p, n_i, n_repeats);
pll_data.offsetwf = NaN(n_p, n_i, n_repeats);
pll_data.i_values = NaN(n_p, n_i, n_repeats);
pll_data.p_values = NaN(n_p, n_i, n_repeats);

pll_data.dwell = get_variable([pv_head, pll_tails.detector.dwell]);
for ser = 1:n_p
    for jfe = 1:n_i
        %initialise loop
        set_variable([pv_head, pll_tails.i], i_vals(jfe))
        set_variable([pv_head, pll_tails.p], p_vals(ser))
        mbf_pll_start(mbf_axis, 'pllbunches',p.Results.pll_monitor_bunches,...
            'guardbunches',p.Results.guardbunches)
        for ewn = 1:n_repeats
            pause(1)
            data = get_variable({[pv_head,pll_tails.nco.offset_waveform];...
                [pv_head,pll_tails.nco.mean_offset];...
                [pv_head,pll_tails.nco.std_offset];...
                [pv_head,pll_tails.nco.tune];...
                [pv_head,pll_tails.nco.offset]});
            wf = data(1,:);
            pll_data.minwf(ser, jfe, ewn) = min(wf);
            pll_data.maxwf(ser, jfe, ewn) = max(wf);
            pll_data.meanwf(ser, jfe, ewn) = data(2,1);
            pll_data.stdwf(ser, jfe, ewn) = data(3,1);
            pll_data.tunewf(ser, jfe, ewn) = data(4,1);
            pll_data.offsetwf(ser, jfe, ewn) = data(5,1);
            pll_data.i_values(ser, jfe, ewn) = i_vals(jfe);
            pll_data.p_values(ser, jfe, ewn) = p_vals(ser);

            clear data
        end %for
    end %for
end %for
%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, pll_data)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, "pll_data")
    end %if
end %if

if nargout == 1
    varargout{1} = pll_data;
end %if
