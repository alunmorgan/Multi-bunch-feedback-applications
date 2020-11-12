def findSubstringInList(tmp_list, target):
    # returns the indicies of a target string in a list.

    matched_indexes = []
    for he in range(len(tmp_list)):
        if target in tmp_list[he]:
            matched_indexes.append(he)

    return matched_indexes
