from mbf_applications.Common.dir_list_gen import dirListGen


def dirListGen_tree(root_dir, file_type, quiet=1):
    """ finds files of the requested file_type in current folder and all subfolders
    ignores hidden folders
    if one ouptput is given then the absolute paths are returned.
    if two output are given then the flien names and directory paths are
    returned separately.

    Example: a dir_paths =dirListGen_tree(root_dir, 'png')
        """

    # returns a list of files in the current directory
    full_name = dirListGen(root_dir, file_type, quiet)
    sub_dir = dirListGen(root_dir, 'dirs', quiet)
    if full_name == [] and sub_dir == []:
        return []

    if not sub_dir == []:
        for sejh in sub_dir:
            full_name_sub = dirListGen_tree(sejh, file_type, quiet)

            if not full_name_sub == []:  # CHECK LOGIC AGAINST MATLAB CODE TODO
                if not full_name == []:
                    full_name.append(full_name_sub)
                else:
                    full_name = full_name_sub

    return full_name
