from mbf_applications.Common.mbf_make_index import mbfMakeIndex

# update all indexes


mbfMakeIndex("LO_scan")
mbfMakeIndex("clock_phase_scan")
mbfMakeIndex("system_phase_scan")
mbfMakeIndex("Bunch_motion")
mbfMakeIndex("Spectrum", "x")
mbfMakeIndex("Spectrum", "y")
mbfMakeIndex("Spectrum", "s")
mbfMakeIndex("Growdamp", "x")
mbfMakeIndex("Growdamp", "y")
mbfMakeIndex("Growdamp", "s")

