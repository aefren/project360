from pdb import Pdb

area = []
tile = 0
for r in range(0,3,1):
    area.append([tile])
    tile += 1
    for x in range(0,3,1):
        area[r].append(tile)
        tile += 1


lst = [[0]*4]*6
Pdb().set_trace()