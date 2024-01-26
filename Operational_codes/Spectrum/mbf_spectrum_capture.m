function varargout = mbf_spectrum_capture(mbf_axis, varargin)
% captures a set of data from the mbf system runs the analysis and then
% saves the results.
%
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
%                       requesting.
%       tunes (structure): Tunes of the machine.
%       n_turns (str): Number of turns to capture at once. Improves
%                      frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
% Returns:
%       data (struct): Multiple sets of time data. Plus metatdata of
%                      settings used.
% 
% Example: data = mbf_spectrum_capture('x')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);

addRequired(p, 'mbf_axis');
addParameter(p, 'tunes', NaN);
addParameter(p, 'n_turns', 1000, valid_number);
addParameter(p, 'repeat',2, valid_number);

parse(p, mbf_axis, varargin{:});

[root_string, harmonic_number, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
spectrum = machine_environment('tunes', p.Results.tunes);

if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')
    chan = 0;
elseif strcmp(mbf_axis, 'y')
    chan = 1;
end %if

for k=p.Results.repeat:-1:1
    if strcmpi(mbf_axis, 's')
             set_variable([pv_names.hardware_names.L pv_names.tails.triggers.MEM.arm],1);
        set_variable([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
        spectrum.raw_data{k} = mbf_read_mem(pv_names.hardware_names.L, p.Results.n_turns,'channel', chan, 'lock', 60);
    else
              set_variable([pv_names.hardware_names.T pv_names.tails.triggers.MEM.arm],1);
        set_variable([pv_names.hardware_names.T, pv_names.tails.triggers.soft], 1)
        spectrum.raw_data{k} = mbf_read_mem(pv_names.hardware_names.T, p.Results.n_turns,'channel', chan, 'lock', 60);
    end %if
end%for
spectrum.axis = mbf_axis;
spectrum.n_turns = p.Results.n_turns;
spectrum.time = datevec(datetime("now"));
spectrum.repeat = p.Results.repeat;
spectrum.harmonic_number = harmonic_number;
spectrum.base_name = ['Spectrum_', mbf_axis, '_axis'];

%% saving the data to a file
save_to_archive(root_string, spectrum)

if nargout == 1
    varargout{1} = spectrum;
end %if