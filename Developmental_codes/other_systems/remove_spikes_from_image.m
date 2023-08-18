function cleaned_data = remove_spikes_from_image(data, threshold)
% remove the single point spikes in an image. replaces them with the average
% value of surrounding pixels.
% data is a 2D array
% threshold is the difference between the sample and the surounding values (in
% pixels)
%
% example:  cleaned_data = remove_spikes_from_image(data, threshold, it)

if nargin == 1
    error('Need to put in a threshold level')
end
cleaned_data = data;
% for each point calculate the difference between it and the adjacent points
for sje = 2:size(data,1)-2
    for hsew = 2:size(data,2)-2
        diff1 = data(sje, hsew) - data(sje-1, hsew);
        diff2 = data(sje, hsew) - data(sje+1, hsew);
        diff3 = data(sje, hsew) - data(sje, hsew-1);
        diff4 = data(sje, hsew) - data(sje, hsew+1);
        if diff1 > threshold && diff2 > threshold && diff3 > threshold && diff4 > threshold
            cleaned_data(sje, hsew) = (data(sje-1, hsew)+ data(sje+1, hsew) + data(sje, hsew-1) + data(sje, hsew+1)) ./ 4;
        end %if

    end %for
end %for