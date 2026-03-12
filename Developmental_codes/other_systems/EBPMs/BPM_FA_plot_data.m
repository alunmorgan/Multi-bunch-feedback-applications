function BPM_FA_plot_data(data)
% Plot the data returned from get_BPM_FA_data.

timescale = (data.t - data.t(1)) * 24 * 3600;
figure;
subplot(2,1,1);
plot(timescale,data.X);
title('BPM FA data')
xlabel('Time(s)')
ylabel('X Position (nm)')

subplot(2,1,2);
plot(timescale, data.Y)
xlabel('Time(s)')
ylabel('Y Position (nm)')

Xrel = data.X(:,:) - data.X(:,1);
Yrel = data.Y(:,:) - data.Y(:,1);
figure;
subplot(2,1,1);
plot(timescale, Xrel);
title('BPM FA data (relative movement)')
xlabel('Time(s)')
ylabel('X Position (nm)')

subplot(2,1,2);
plot(timescale, Yrel)
xlabel('Time(s)')
ylabel('Y Position (nm)')

fx = spectra(timescale,Xrel');
fy = spectra(timescale,Yrel');


figure;
subplot(2,1,1);
plot(fx.frequency * 1E-3, fx.dft_y);
title('BPM FA data (FFT)')
xlabel('Frequency (kHz)')
ylabel('X Position (nm)')

subplot(2,1,2);
plot(fy.frequency * 1E-3, fy.dft_y)
xlabel('Frequency (kHz)')
ylabel('Y Position (nm)')

