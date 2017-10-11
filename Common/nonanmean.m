% Function identical to MEAN, except NaNs are discounted.
%
% Similar replacements exist for NONANMEAN, NONANMEDIAN, NONANSTD, 
% NONANSUM and NONANCUMSUM which are all part of the NaN-suite.
function y=nonanmean(y0,dim)

if nargin==1
    dim = find(size(y0)~=1,1,'first');
end
if isempty(dim)
    % this covers the case when there is only one value
    dim = 1;
end
nan_list = isnan(y0);
y0(isnan(y0)) = 0; 

y = sum(y0,dim)./(size(y0,dim) - sum(nan_list,dim));
