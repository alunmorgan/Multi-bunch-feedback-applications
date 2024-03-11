function pll_phase_scan = mbf_pll_phase_scan(mbf_axis, varargin)
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
    default_range = 270;
elseif strcmp(mbf_axis, 'y')
    default_range = 270;
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
pll_phase_scan = machine_environment;
pll_phase_scan.ax_label = mbf_axis;
pll_phase_scan.base_name = ['pll_phase_scan_' pll_phase_scan.ax_label '_axis'];
name = pv_names.hardware_names.(mbf_axis);
pll_tails = pv_names.tails.pll;

pll_phase_scan.scan_step = step;
pll_phase_scan.scan_range = range;

pll_phase_scan.mbf_fll.target_bunches = get_variable([name, pll_tails.detector.target_bunches]);
pll_phase_scan.mbf_fll.gain = get_variable([name, pll_tails.nco.gain]);
pll_phase_scan.mbf_fll.target_phase = get_variable([name, pll_tails.target_phase]);
pll_phase_scan.mbf_fll.KI = get_variable([name, pll_tails.i]);
pll_phase_scan.mbf_fll.KP = get_variable([name, pll_tails.p]);

start=get_variable([name pll_tails.target_phase]);
pll_phase_scan.phase=[start:step:(start + range) (start + range):-step:(start - range) (start - range):step:(start+ range) (start+ range):-step:start ];
pll_phase_scan.mag = NaN(length(pll_phase_scan.phase),1);
pll_phase_scan.iq = NaN(length(pll_phase_scan.phase),1);
pll_phase_scan.f = NaN(length(pll_phase_scan.phase),1);
for n=1:length(pll_phase_scan.phase)
    status=get_variable([name pll_tails.status]);
    if strcmp(status,'Running')
        %the funny mod is required to get into the right range of -180 to +179
        set_variable([name pll_tails.target_phase],mod(pll_phase_scan.phase(n)+180,360)-180)
        pause(.2) %This will depend on the dwell time and PLL config, but works with the default
        pll_phase_scan.mag(n)=get_variable([name pll_tails.readback.magnitude]); %get magnitude
        pll_phase_scan.phase(n)=get_variable([name pll_tails.readback.phase]); %get phase readback
        pll_phase_scan.iq(n)=[1 1i]*get_variable({[name pll_tails.readback.i];[name pll_tails.readback.q]});
        pll_phase_scan.f(n)=get_variable([name pll_tails.nco.frequency]);
    else
        set_variable([name pll_tails.target_phase],start);
        break
    end %if
end %for

save_to_archive(root_path{1}, pll_phase_scan)
disp(['Data saved to ', fullfile(root_path{1}, pll_phase_scan.base_name)])

fll_phase_scan_plotting(pll_phase_scan);

if ~strcmp(status,'Running')
    error('PLL:stoppedUnexpectedly', 'PLL stopped during phase sweep, please restart using fll_start')
end


