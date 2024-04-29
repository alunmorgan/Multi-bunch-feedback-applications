function image = pinhole_get_data_after_trigger(channel)

% The camera image PV always returns the maximum size regardless of
% settings. So set the selection area to max so that all of the scale
% values match.
original_imagewidth = get_variable([channel ':IMAGEWIDTH']);
set_variable([channel ':IMAGEWIDTH'], 1024)
image_pv =[channel ':PROXY:DATA'];
lcaSetMonitor(image_pv)
lcaNewMonitorWait(image_pv) % initial data
lcaNewMonitorWait(image_pv) % experimental data

[image.image, image.timestamp] = get_variable(image_pv,0,'byte');
im_temp = get_variable({[channel ':WIDTH'];...
                  [channel ':HEIGHT'];...
                  [channel ':XSCALEMAX'];...
                  [channel ':XSCALEMIN'];...
                  [channel ':YSCALEMAX'];...
                  [channel ':YSCALEMIN']});
neg=find(image.image < 0);
image.image(neg)=256 + image.image(neg);
image.width = squeeze(im_temp(1, :));
image.height = squeeze(im_temp(2, :));
image.xmax = squeeze(im_temp(3, :));
image.xmin = squeeze(im_temp(4, :));
image.ymax = squeeze(im_temp(5, :));
image.ymin = squeeze(im_temp(6, :));

% Restore to original slection size.
set_variable([channel ':IMAGEWIDTH'], original_imagewidth)

image.image = reshape(image.image, image.width, image.height).';