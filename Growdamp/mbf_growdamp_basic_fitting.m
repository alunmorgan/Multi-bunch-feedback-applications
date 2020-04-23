function [s, delta, p] = mbf_growdamp_basic_fitting(data)

 x_ax = 1:length(data);
        s = polyfit(x_ax,log(abs(data)),1);
        c = polyval(s,x_ax);
        delta = mean(abs(c - log(abs(data)))./c);
        temp = unwrap(angle(data)) / (2*pi);
        p = polyfit(x_ax,temp,1);