function sel = find_position_in_cell_lst(tmp)
% returns the indicies of a cell array where the cell is not empty.
% will also work for a vector (yes/no).

if iscell(tmp) == 0
    if isempty(tmp) == 0
        sel = 1;
    else
        sel  = [];
    end %if
else
    hsd = 1;
    sel = NaN(length(tmp));
    for he = 1:length(tmp)
        if isempty(tmp{he}) == 0
            sel(hsd) = he;
            hsd = hsd +1;
        end %if
    end %for
    sel(hsd:end) = [];
    if hsd == 1
        sel = [];
    end %if
end %if
