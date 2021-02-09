def cat_multi_dim(cat_dim, original_data, new_data):
    """ concatinates multi-dimensional data in the cat_dim dimension,
    pads the other dimensions as necessary.
    If given 1 output will give the combined matrix,.
    If given 2 outputs will output the padded components
    example
    varargout = cat_multi_dim(cat_dim,original_data, new_data)
    """
    pad_dims = range(1,5)
    pad_dims[pad_dims == cat_dim] = []

    ## Padding the arrays to make them the same size in all dimensions
    for n in range(3):
        if size(new_data,pad_dims[n]) > size(original_data,pad_dims[n]):
            if pad_dims[n] == 1:
                size1 = size(new_data,1) - size(original_data,1)
                if size1 == 0:
                    size1 = 1

            else:
                size1 = size(original_data,1)

            if pad_dims[n] == 2:
                size2 = size(new_data,2) - size(original_data,2)
                if size2 == 0:
                    size2 = 1

            else:
                size2 = size(original_data,2)

            if pad_dims[n] == 3:
                size3 = size(new_data,3) - size(original_data,3)
                if size3 == 0:
                    size3 = 1

            else:
                size3 = size(original_data,3)

            if pad_dims[n] == 4:
                size4 = size(new_data,4) - size(original_data,4)
                if size4 == 0:
                    size4 = 1

            else:
                size4 = size(original_data,4)

            od_padding = NaN(size1,size2,size3,size4)
            # If the data is a character array, converting the
            #NaN padding matrix into an array of spaces to stop
            #the warning messages.
            if ischar(original_data) == 1:
                od_padding[isnan(od_padding) == 1] = ' '
                od_padding = char(od_padding)

            original_data = cat(pad_dims[n],original_data,od_padding)

        if size(new_data,pad_dims[n]) < size(original_data,pad_dims[n]):
            if pad_dims[n] == 1:
                size1 = size(original_data,1) - size(new_data,1)
                if size1 == 0:
                    size1 = 1

            else:
                size1 = size(new_data,1)

            if pad_dims[n] == 2:
                size2 = size(original_data,2) - size(new_data,2)
                if size2 == 0:
                    size2 = 1

            else:
                size2 = size(new_data,2)

            if pad_dims[n] == 3:
                size3 = size(original_data,3) - size(new_data,3)
                if size3 == 0:
                    size3 = 1

            else:
                size3 = size(new_data,3)

            if pad_dims[n] == 4:
                size4 = size(original_data,4) - size(new_data,4)
                if size4 == 0:
                    size4 = 1
                end
            else:
                size4 = size(new_data,4)

            nd_padding = NaN(size1,size2,size3,size4)
            # If the data is a character array, converting the 
            #NaN padding matrix into an array of spaces to stop
            #the warning messages.
            if ischar(new_data) == 1:
                nd_padding[isnan(nd_padding) == 1] = ' '
                nd_padding = char(nd_padding)

            new_data = cat(pad_dims[n],new_data,nd_padding)

    return new_data