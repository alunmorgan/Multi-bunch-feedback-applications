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

image.imagewidth = get_variable([channel ':IMAGEWIDTH']);
[image.image, image.timestamp] = get_variable([channel ':PROXY:DATA'],0,'byte');
neg=find(image.image < 0);
image.image(neg)=256 + image.image(neg);
image.width = get_variable([channel ':WIDTH']);
image.height = get_variable([channel ':HEIGHT']);
image.xmax = get_variable([channel ':XSCALEMAX']);
image.xmin = get_variable([channel ':XSCALEMIN']);
image.ymax = get_variable([channel ':YSCALEMAX']);
image.ymin = get_variable([channel ':YSCALEMIN']);

% The PV returns the full image regardless of settings. 
% Remove zero padding
image.image = image.image(1:image.height*image.width);
image.image = reshape(image.image, image.width, image.height).';

% gamma correction 
image.image = image.image .* ...
    exp(p.Results.gamma_correction * (image.image / 255 - 1)); 
% this appears to give the best correction  



