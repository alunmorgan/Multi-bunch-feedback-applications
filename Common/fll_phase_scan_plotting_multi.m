function fll_phase_scan_plotting_multi(requested_data, varargin)
% Plots the results of a FLL phase scan on the
%multi bunch feedback system
%
%   Args:
%       fll_phase_scan(struct): data captured during the phase scan.
%       scan_type(str): states what the scan variable was
%                       'samples', 'charge', 'gain', 'rf'
%
% Example: fll_phase_scan_plotting_multi(requested_data, varargin)

default_scan_type = 'samples';
p = inputParser;
addRequired(p, 'requested_data');
addParameter(p, 'scan_type', default_scan_type);

parse(p, requested_data, varargin{:});
scan_type = p.Results.scan_type;
% target_bunch = 920;
% gains = [-30,-24,-18,-12,-6];
f1 = figure('Position', [50, 100, 1440, 768]);
for ehs = 1:length(requested_data)
    % IF more than one bunch is selected then only the first one is used here.
    target_bunch = find(requested_data{ehs}.mbf_fll.target_bunches >0, 1, 'first');
    data_length = length(requested_data{ehs}.phase);
    subplot(2,3,1)
    hold all
    plot(requested_data{ehs}.phase, requested_data{ehs}.mag)
    xlabel('target phase')
    ylabel('FLL detected magnitude')
    grid on
    subplot(2,3,2)
    hold all
    plot(requested_data{ehs}.phase, requested_data{ehs}.f)
    xlabel('target phase')
    ylabel('FLL detected frequency')
    title(['Phase scan of frequency locked loop in ',requested_data{1}.ax_label,' with ', scan_type])
    grid on
    subplot(2,3,3)
    hold all
    plot(requested_data{ehs}.iq, '*')
    xlabel('i')
    ylabel('q')
    axis equal
    grid on
    
    if strcmp(scan_type, 'samples')
        xval = ehs;
    elseif strcmp(scan_type, 'charge')
        if ehs >length(requested_data) -3
            target_bunch = 926;
        end %if
        xval = requested_data{ehs}.fill_pattern(target_bunch);
    elseif strcmp(scan_type, 'gain')
        xval = requested_data{ehs}.mbf_fll.gain;
    elseif strcmp(scan_type, 'rf')
        xval = requested_data{ehs}.RF;
    end %if
    plot_X = ones(data_length,1) * xval;
    plot_Y = requested_data{ehs}.phase;
    mag_Z = requested_data{ehs}.mag;
    f_Z = requested_data{ehs}.f;
    
    subplot(2,3,4)
    hold all
    plot3(plot_X, plot_Y, mag_Z)
    ylabel('target phase')
    xlabel(scan_type)
    zlabel('FLL detected magnitude')
    grid on
    view(3)
    axis ij
    
    subplot(2,3,5)
    hold all
    plot3(plot_X, plot_Y, f_Z, 'DisplayName', num2str(xval))
    ylabel('target phase')
    xlabel(scan_type)
    zlabel('FLL detected frequency')
    grid on
    view(3)
    axis ij

    
end %for
filename = ['~/Phase scan of frequency locked loop in ',requested_data{1}.ax_label, ' with ', scan_type '_', datestr(requested_data{1}.time)];
filename = regexprep(filename, ' ', '_');
filename = regexprep(filename, ':', '-');
saveas(f1, filename, 'fig')
saveas(f1, filename, 'png')