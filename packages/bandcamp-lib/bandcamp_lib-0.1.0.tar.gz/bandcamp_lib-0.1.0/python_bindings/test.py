import bandcamp_lib
a = bandcamp_lib.fetch_album(3752216131, 83593492)
print(a.item_type)
