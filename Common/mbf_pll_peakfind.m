function fll_phase_scan = mbf_pll_peakfind(mbf_axis, varargin)
%
%       Args:
%           mbf_axis(str): 'x' or 'y'
%           range(int): phase range in degree to search around the
%                       current target phase default is 80 degrees
%           step(int): step in degree, default is 5 degrees
%       Returns:
%          fll_phase_scan(struct): structure containing captured data from
%                                  the MBF plus general operating
%                                  conditions of the machine
%
% Example: fll_phase_scan = mbf_pll_peakfind('x')

default_step = 1;
if strcmp(mbf_axis, 'x')
    default_range = 80;
elseif strcmp(mbf_axis, 'y')
    default_range = 60;
end %if

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
p = inputParser;
addRequired(p, 'name', @ischar);
addParameter(p, 'range', default_range, validScalarPosNum);
addParameter(p, 'step', default_step, validScalarPosNum);

parse(p,mbf_axis,varargin{:});
range = p.Results.range;
step = p.Results.step;

[root_path, ~, pv_names, ~] = mbf_system_config;
fll_phase_scan = machine_environment;
fll_phase_scan.ax_label = mbf_axis;
fll_phase_scan.base_name = ['fll_phase_scan_' fll_phase_scan.ax_label '_axis'];
name = pv_names.hardware_names.(mbf_axis);

fll_phase_scan.scan_step = step;
fll_phase_scan.scan_range = range;

fll_phase_scan.mbf_fll.target_bunches = lcaGet([name, ':PLL:DET:BUNCHES_S']);
fll_phase_scan.mbf_fll.gain = lcaGet([name, ':PLL:NCO:GAIN_DB_S']);
fll_phase_scan.mbf_fll.target_phase = lcaGet([name, ':PLL:CTRL:TARGET_S']);
fll_phase_scan.mbf_fll.KI = lcaGet([name, ':X:PLL:CTRL:KI_S']);
fll_phase_scan.mbf_fll.KP = lcaGet([name, ':PLL:CTRL:KP_S']);

start=lcaGet([name ':PLL:CTRL:TARGET_S']);
fll_phase_scan.phase=[start:step:(start + range) (start + range):-step:(start - range) (start - range):step:(start+ range) (start+ range):-step:start ];
fll_phase_scan.mag = NaN(length(fll_phase_scan.phase),1);
fll_phase_scan.iq = NaN(length(fll_phase_scan.phase),1);
fll_phase_scan.f = NaN(length(fll_phase_scan.phase),1);
for n=1:length(fll_phase_scan.phase)
    %the funny mod is required to get into the right range of -180 to +179
    lcaPut([name ':PLL:CTRL:TARGET_S'],mod(fll_phase_scan.phase(n)+180,360)-180)
    pause(.2) %This will depend on the dwell time and PLL config, but works with the default
    fll_phase_scan.mag(n)=lcaGet([name ':PLL:FILT:MAG']); %get magnitude
    fll_phase_scan.iq(n)=[1 1i]*lcaGet({[name ':PLL:FILT:I'];[name ':PLL:FILT:Q']});
    fll_phase_scan.f(n)=lcaGet([name ':PLL:NCO:FREQ']);
end

save_to_archive(root_path{1}, fll_phase_scan)
disp(['Data saved to ', fullfile(root_path{1}, fll_phase_scan.base_name)])

f1 = fll_phase_scan_plotting(fll_phase_scan);

status=lcaGet([name ':PLL:CTRL:STATUS']);
if strcmp(status,'Running')
    lcaPut([name ':PLL:CTRL:TARGET_S'],start);
else
    error('PLL stopped during phase sweep, please restart using mbf_fll_start')
end


