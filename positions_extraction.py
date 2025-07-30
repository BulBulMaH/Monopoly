def positions_extraction(resolution_folder):
    positions_file = open(f'resources/{resolution_folder}/text values/positions.txt')
    positions_temporary = positions_file.readlines()
    positions_file.close()
    positions = []
    for i in range(len(positions_temporary)):
        positions.append(positions_temporary[i].split(','))
        positions[i][1] = positions[i][1][:-1]
    positions_temporary.clear()
    for i in range(len(positions)):
        for ii in range(len(positions[i])):
            positions[i][ii] = int(positions[i][ii])
    return positions