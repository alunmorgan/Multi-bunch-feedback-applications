function plot_single_kick_scan(data_x, data_y, label_x, graph_title)
figure
hold on
for wse = 1:size(data_y,2)
    temp = squeeze(data_y(:,wse)).*1e-3;
    temp = temp - min(temp);
    plot(data_x, temp,'.-')
end %for
xlabel(label_x)
ylabel('Ver. RMS oscillation (baseline removed) [\mum]')
title(graph_title)