function plot_pinhole_image(image)

% setting up a new colormap
jet1=jet;
jet1(1:8,3)=linspace(0,1,8).';
jet1(64,1:3)=[1 1 1];

figure
imagesc(linspace(image.xmax,image.xmin,image.height),...
     linspace(image.ymin,image.ymax,image.width),...
     image.image);
axis image
set(gca,'YDir','normal')
colormap(jet1)
