function mbf_bunch_motion_plotting(data)

xlimits = [min(data.x) max(data.x)];
ylimits = [min(data.y) max(data.y)];
zlimits = [min(data.z) max(data.z)];

x = reshape(data.x, data.num_buckets, []);
y = reshape(data.y, data.num_buckets, []);
z = reshape(data.z, data.num_buckets, []);

figure(1)
ax1 = axes('OuterPosition',[0 0.5 0.5 0.5]);
ax2 = axes('OuterPosition',[0.5 0.5 0.5 0.5]);
ax3 = axes('OuterPosition',[0 0 0.5 0.5]);
ax4 = axes('OuterPosition',[0.5 0 0.5 0.5]);

xlabel(ax1, 'Beam direction')
ylabel(ax1, 'Horizontal')
xlabel(ax2, 'Beam direction')
ylabel(ax2, 'Vertical')
ylabel(ax3, 'Horizontal')
zlabel(ax3, 'Vertical')
xlabel(ax3, 'Beam direction')
xlabel(ax4, 'Horizontal')
ylabel(ax4, 'Vertical')

axes(ax1);
hold on
axes(ax2);
hold on
axes(ax4);
hold on
axes(ax3);
hold on
for js = 1:data.num_buckets
    warning('off','all')
    shp1 = alphaShape(cat(2,squeeze(z(js,:))', squeeze(x(js,:))'));
    shp2 = alphaShape(cat(2,squeeze(z(js,:))', squeeze(y(js,:))'));
    shp4 = alphaShape(cat(2,squeeze(x(js,:))', squeeze(y(js,:))'));
    shp3 = alphaShape(cat(2,squeeze(z(js,:))', squeeze(x(js,:))', ...
        squeeze(y(js,:))'));
    warning('on','all')
    
    
    plot(shp1, 'FaceAlpha', 0.5, 'EdgeAlpha', 0 ,...
        'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
        'Parent', ax1)
    
    plot(shp2, 'FaceAlpha', 0.5, 'EdgeAlpha', 0  ,...
        'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
        'Parent', ax2)
    
    plot(shp4, 'FaceAlpha', 0.5, 'EdgeAlpha', 0  ,...
        'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
        'Parent', ax4)
    
    plot(shp3, 'FaceAlpha', 0.5, 'EdgeAlpha', 0  ,...
        'FaceColor', [(data.num_buckets - js)/ data.num_buckets, 0, js/data.num_buckets],...
        'Parent', ax3)
end %for


axis(ax1, [zlimits(1) zlimits(2) xlimits(1) xlimits(2)])
axis(ax2, [zlimits(1) zlimits(2) ylimits(1) ylimits(2)])
axis(ax4, [xlimits(1) xlimits(2) ylimits(1) ylimits(2)])
axis(ax3, [zlimits(1) zlimits(2) xlimits(1) xlimits(2) ylimits(1) ylimits(2)])

view(ax3, 30, 30)
