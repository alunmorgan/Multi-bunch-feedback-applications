function summary = BPM_TbT_analyse_data(data_path)

load(data_path)
disp('')

bpms = fields(output);
summary.bpms = bpms;
buttons = {'A', 'B', 'C', 'D'};
for ewhs = 1:length(bpms)
    summary.meanx(ewhs) = output.(bpms{ewhs}).meanx;
    summary.meany(ewhs) = output.(bpms{ewhs}).meany;
    summary.stdx(ewhs) = output.(bpms{ewhs}).stdx;
    summary.stdy(ewhs) = output.(bpms{ewhs}).stdy;
    summary.minx(ewhs) = output.(bpms{ewhs}).minx;
    summary.miny(ewhs) = output.(bpms{ewhs}).miny;
    summary.maxx(ewhs) = output.(bpms{ewhs}).maxx;
    summary.maxy(ewhs) = output.(bpms{ewhs}).maxy;
    for dsw = 1:length(buttons)
        summary.(['mean', buttons{dsw}])(ewhs) = mean(output.(bpms{ewhs}).(buttons{dsw}));
        summary.(['std', buttons{dsw}])(ewhs) = std(output.(bpms{ewhs}).(buttons{dsw}));
        summary.(['min', buttons{dsw}])(ewhs) = min(output.(bpms{ewhs}).(buttons{dsw}));
        summary.(['max', buttons{dsw}])(ewhs) = max(output.(bpms{ewhs}).(buttons{dsw}));
     
    end %for
end %for
