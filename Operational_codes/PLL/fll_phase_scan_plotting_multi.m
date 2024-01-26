function fll_phase_scan_plotting_multi(requested_data, varargin)
% Plots the results of a FLL phase scan on the
%multi bunch feedback system
%
%   Args:
%       fll_phase_scan(struct): data captured during the phase scan.
%       scan_type(str): states what the scan variable was
%                       'samples', 'charge', 'gain', 'rf'
%       target_bunch_override(int): force the target bunch location to be this
%                                   value
%
% Example: fll_phase_scan_plotting_multi(requested_data, varargin)

default_scan_type = 'samples';
p = inputParser;
addRequired(p, 'requested_data');
addParameter(p, 'scan_type', default_scan_type);
addParameter(p, 'target_bunch_override', NaN);

parse(p, requested_data, varargin{:});
scan_type = p.Results.scan_type;

xval = NaN(1, length(requested_data));
for ehs = 1:length(requested_data)
    if strcmp(scan_type, 'samples')
        xval(ehs) = ehs;
    elseif strcmp(scan_type, 'charge')
        if isnan(p.Results.target_bunch_override)
        % IF more than one bunch is selected then only the first one is used here.
            target_bunch = find(requested_data{ehs}.mbf.(selected_axis).fll.target_bunches >0, 1, 'first');
        else
            target_bunch = p.Results.target_bunch_override;
        end %if
        xval(ehs) = requested_data{ehs}.fill_pattern(target_bunch) * 1E3;
    elseif strcmp(scan_type, 'gain')
        selected_axis = requested_data{ehs}.ax_label;
        xval(ehs) = requested_data{ehs}.mbf.(selected_axis).fll.nco.gain;
    elseif strcmp(scan_type, 'rf')
        xval(ehs) = requested_data{ehs}.RF;
    end %if
end %for
[xval, sorting] = sort(xval);

% gains = [-30,-24,-18,-12,-6];
low_mag_limit = 2E-5;
f1 = figure('Position', [50, 100, 1900, 768]);
for ehs = 1:length(requested_data)
temp_data = requested_data{sorting(ehs)};
    data_length = length(temp_data.phase);
    subplot(2,4,1)
    hold all
    plot(temp_data.phase, temp_data.mag, '*')
    xlabel('target phase')
    ylabel('Loop detected magnitude')
    grid on
    subplot(2,4,2)
    hold all
        %set the phase values where the magnitude is very low to NaN in order to
    %clean up the graphs
    temp_phase = temp_data.phase;
    temp_phase(temp_data.mag < low_mag_limit) = NaN;
    plot(rem(temp_data.f,1), temp_phase, '*')
    xlabel('Loop detected fractional tune')
    ylabel('target phase')
    title(['Phase scan of frequency locked loop in ',requested_data{1}.ax_label,' with ', scan_type])
    grid on
    xlim([0, 1])
    subplot(2,4,3)
    hold all
    plot(rem(temp_data.f,1), temp_data.mag, '*')
    xlabel('Loop detected fractional tune')
    ylabel('Loop detected magnitude')
    grid on
    xlim([0, 1])
    subplot(2,4,4)
    hold all
    plot(requested_data{ehs}.iq, '*')
    xlabel('i')
    ylabel('q')
    axis equal
    grid on
    
    plot_X = ones(data_length,1) * xval(ehs);
    plot_Y = requested_data{ehs}.phase;
    mag_Z = requested_data{ehs}.mag;
    f_Z = requested_data{ehs}.f;
    
    %set the phase values where the magnitude is very low to NaN in order to
    %clean up the graphs
    plot_Y(mag_Z < low_mag_limit) = NaN;

    subplot(2,4,5)
    hold all
    plot3(plot_X, plot_Y, mag_Z, '*')
    ylabel('target phase')
    xlabel(scan_type)
    zlabel('Loop detected magnitude')
    grid on
    view(3)
    axis ij
    
    subplot(2,4,6:7)
    hold all
    plot3(plot_X, rem(f_Z,1), plot_Y, '*','DisplayName', num2str(xval(ehs)))
    ylabel('Loop detected fractional tune')
    xlabel(scan_type)
    zlabel('target phase')
    grid on
    ylim([0, 1])
    view(3)
    axis ij
    legend

    
end %for
filename = ['~/Phase scan of frequency locked loop in ',requested_data{1}.ax_label, ' with ', scan_type '_', datestr(requested_data{1}.time)];
filename = regexprep(filename, ' ', '_');
filename = regexprep(filename, ':', '-');
saveas(f1, filename, 'fig')
saveas(f1, filename, 'png')