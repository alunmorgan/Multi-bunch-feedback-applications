import os


def treeGen(tree_root, c):
    """Generates a directory structure using the time vector from clock
    tree_root is where you want the subdirectoires to be placed
    cl is the clock vector
    """
    yr = c[0]
    mth = c[1]
    dy = c[2]

    if mth < 10:
        mth = "".join(("0", mth))

    if dy < 10:
        dy = "".join(("0", dy))

#    if not os.path.isdir(os.path.join(tree_root, yr)):
#        os.mkdir(os.path.join(tree_root, yr))

#    if not os.path.isdir(os.path.join(tree_root, yr, mth)):
#        os.mkdir(os.path.join(tree_root, yr, mth))

    if not os.path.isdir(os.path.join(tree_root, yr, mth, dy)):
        os.mkdirs(os.path.join((tree_root, yr, mth, dy)))
