import os


def dirListGen(directory_name, file_type, quiet_flag=1):
    """takes in a directory name and outputs the list of files
    as a list filtered by file type.
     if a file type of 'dirs' is input it will output a list of directories.
          quiet_flag makes it quiet or verbose (1 = quiet) if not given assume quiet.
     outputs absolute paths.
     Example:  names = dir_list_gen('U:\', 'mat')
    """
    names = []
    # removes leading . of file_type if present
    if file_type[0] == '.':
        file_type = file_type[1:-1]

    if not os.path.isdir(directory_name):
        print('Directory does not exist')

        return names
    else:
        folder_contents = os.scandir(directory_name)

    for entry in folder_contents:
        if file_type == 'dirs':
            if entry.is_dir():
                names.append(os.path.join(directory_name, entry))
        else:
            if entry.is_file():
                entry_name, entry_ext = os.path.splitext(entry)
                if entry_ext == file_type:
                    names.append(os.path.join(directory_name, entry))

    if quiet_flag == 0:
        if file_type == 'dirs':
            if names == []:
                print('No directories found')
            else:
                print(''.join((len(names), ' directories found')))
        else:
            if names == []:
                print(''.join(('No files with extension ', file_type, ' found')))
            else:
                print(''.join((len(names), ' files with extension ',
                               file_type, ' found')))
