function [iq,f,phase]=mbf_pll_peakfind(name,range,step)
% function mbf_pll_peak(name,range)
%
% name          <EPICS device>:<axis>
% range         phase range id degree to search around current target phase
% step          step in degree, default is 5 degrees

% ugly check to see if step are specified
if nargin<3
    step=5;
end

start=lcaGet([name ':PLL:CTRL:TARGET_S']);
phase=[(start-range):step:(start+range) (start+range):-step:(start-range)];
for n=1:length(phase);
    lcaPut([name ':PLL:CTRL:TARGET_S'],mod(phase(n)+180,360)-180) %the funny mod is required to get into the right range of -180 to +179
    pause(.2) %This will depend on the dwell time and PLL config, but works with the default
    mag(n)=lcaGet([name ':PLL:FILT:MAG']); %get magnitude
    iq(n)=[1 i]*lcaGet({[name ':PLL:FILT:I'];[name ':PLL:FILT:Q']});
    f(n)=lcaGet([name ':PLL:NCO:FREQ']);
end
[m,mi]=max(abs(mag));
peak=phase(mi);
figure;
plot(phase,mag,[peak peak],[min(mag) max(mag) ])
xlabel('target phase')
ylabel('PLL detected magnitude')
figure
plot(iq)

status=lcaGet([name ':PLL:CTRL:STATUS']);
if strcmp(status,'Running')
    lcaPut([name ':PLL:CTRL:TARGET_S'],mod(peak+180,360)-180);
    display([name ':PLL:CTRL:TARGET_S set to ' num2str(mod(peak+180,360)-180)])
else
    error('PLL stoped during phase sweep, please restart using mbf_pll_start')
end
    

