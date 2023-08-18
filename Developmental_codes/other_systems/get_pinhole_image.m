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

image.imagewidth = lcaGet([channel ':IMAGEWIDTH']);
[image.image, image.timestamp] = lcaGet([channel ':PROXY:DATA'],0,'byte');
neg=find(image.image < 0);
image.image(neg)=256 + image.image(neg);
image.width = lcaGet([channel ':WIDTH']);
image.height = lcaGet([channel ':HEIGHT']);
image.xmax = lcaGet([channel ':XSCALEMAX']);
image.xmin = lcaGet([channel ':XSCALEMIN']);
image.ymax = lcaGet([channel ':YSCALEMAX']);
image.ymin = lcaGet([channel ':YSCALEMIN']);

% The PV returns the full image regardless of settings. 
% Remove zero padding
image.image = image.image(1:image.height*image.width);
image.image = reshape(image.image, image.width, image.height).';

% gamma correction 
image.image = image.image .* ...
    exp(p.Results.gamma_correction * (image.image / 255 - 1)); 
% this appears to give the best correction  



