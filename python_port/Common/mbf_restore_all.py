from Common import mbfSystemConfig, mbfRestorePv, findSubstringInList
from cothread.catools import caPut
import os


def mbfRestoreAll():
    """
    Finds all the stored values in the captured config folder. Restores all
    the found PVs to the stored state, and deletes the value from the store.
    For PROC files it determines if it is was a reset and if so triggers the
    corresponding arm PV. Does not do anything with other types of PROC
    files.

    Example: mbf_restore_all
    """

    root_string, _1, _2, _3 = mbfSystemConfig
    # Only interested in the currently used storage location.
    root_string = root_string[0]

    pv_files, file_dir = dir_list_gen(os.path.join(root_string, 'captured_config'),
                                      'mat')
    pv_files1, _4 = dir_list_gen(os.path.join(root_string, 'captured_config'), 'PROC')
    pv_files.extend(pv_files1)
    for hsaw in range(len(pv_files)):
        if findSubstringInList(pv_files[hsaw], '.PROC') == []:
            mbfRestorePv(pv_files[hsaw])
            os.remove(os.path.join(file_dir, pv_files[hsaw]))
        else:
            if not findSubstringInList(pv_files[hsaw], ':RESET_S.PROC') == []:
                #                 Arm the previously disabled trigger
                print(regexprep(pv_files[hsaw], ':RESET_S.PROC', ':ARM_S.PROC'))
                caPut(regexprep(pv_files[hsaw], ':RESET_S.PROC', ':ARM_S.PROC'), 1)
                os.remove(os.path.join(file_dir, pv_files[hsaw]))
            else:
                individual_pv = os.path.basename(pv_files[hsaw])
                print(''.join(('Not touching ', individual_pv[0:-4])))
