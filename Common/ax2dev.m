function dev=ax2dev(axis)
% converts axis number into IOC name for PV
% this functions is called from all others which allow specification of
% axis
% change to suit your needs
% axis 1|2|3 for X|Y|Z
% example dev=ax2dev(axis)
if axis == 1
    dev = 'SR23C-DI-TMBF-04:X';
elseif axis == 2
    dev = 'SR23C-DI-TMBF-04:Y';
elseif axis == 3
    dev = 'SR23C-DI-LMBF-01:IQ';
else
    dev='TS-DI-TMBF-01';
end