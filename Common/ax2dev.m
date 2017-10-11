function dev=ax2dev(axis)
% converts axis number into IOC name for PV
% this functions is called from all others which allow specification of
% axis
% change to suit your needs
% axis 1|2 for X|Y
% example dev=ax2dev(axis)
if axis <4
    dev = ['SR23C-DI-TMBF-0' num2str(axis)];
else
    dev='TS-DI-TMBF-01';
end