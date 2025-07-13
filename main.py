import merger as mg

print ("-----------------------------------")
print("Merging location specific shp files")
print ("-----------------------------------")
mg.mergeInner()
print ("-----------------------------------")
print("Creating map out of all merged shp files")
print ("-----------------------------------")
mg.mergeOuter()