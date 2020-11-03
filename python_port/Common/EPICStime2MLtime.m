%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% EPICStime2MLtime
%
% Christopher Bloomer
% v1.0 01/10/2013
%
% A short program to convert the complex timestamps that an lcaGet recieves 
% from EPICS (seconds from epoch: 01 Jan 1970, with an imaginary components 
% corresponding to ns) into MatLab time (days from epoch: 01 Jan 0000).
%
% T = EPICStime2MLtime(t)
%
% Inputs:
%   t = A single value or vector of times in EPICS complex number format.
%
% Output:
%   T = The time(s) in MatLab time.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%
function T = EPICStime2MLtime(t)

T = datenum(1970, 1, 1, 0, 0, real(t)+imag(t).*1e-9);