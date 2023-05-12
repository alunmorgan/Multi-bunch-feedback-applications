function image = get_pinhole_image(channel, varargin)
% Returns the current image from the camera along with size, timestamp and
% scaling values.
default_gamma_correction = 0.097;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);

addRequired(p, 'channel');
addParameter(p, 'gamma_correction', default_gamma_correction, valid_number);
parse(p, channel, varargin{:});

original_imagewidth = lcaGet([channel ':IMAGEWIDTH']);
% The camera image PV always returns the maximum size regardless of
% settings. So set the selection area to max so that all of the scale
% values match.
lcaPut([channel ':IMAGEWIDTH'], 1024)
[image.image, image.timestamp] = lcaGet([channel ':PROXY:DATA'],0,'byte');
neg=find(image.image < 0);
image.image(neg)=256 + image.image(neg);
%image.width = lcaGet([channel ':WIDTH']);
%image.height = lcaGet([channel ':HEIGHT']);
% FIX ME
image.width = 1024;
image.height = 768;
image.xmax = lcaGet([channel ':XSCALEMAX']);
image.xmin = lcaGet([channel ':XSCALEMIN']);
image.ymax = lcaGet([channel ':YSCALEMAX']);
image.ymin = lcaGet([channel ':YSCALEMIN']);

% Restore to original slection size.
lcaPut([channel ':IMAGEWIDTH'], original_imagewidth)

image.image = reshape(image.image, image.width, image.height).';

% gamma correction 
image.image = image.image .* ...
    exp(p.Results.gamma_correction * (image.image / 255 - 1)); 
% this appears to give the best correction  


