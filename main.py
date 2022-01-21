import os

dir_path = os.path.dirname(os.path.abspath(__file__))

def parse_coords(coord_string):
    signs = {'N': 1, 'E': 1, 'S': -1, 'W': -1}
    lat,lng = None,None
    lat_dir = coord_string[6]
    lng_dir = coord_string[-1]
    coord_string = coord_string.split(lat_dir)
    lat_unparse = coord_string[0]
    lng_unparse = coord_string[1][:-1]

    lat = (int(lat_unparse[:2]) + (int(lat_unparse[2:4])/60) + (int(lat_unparse[4:])/3600)) * signs[lat_dir]
    lng = (int(lng_unparse[:3]) + (int(lng_unparse[3:5])/60) + (int(lng_unparse[5:])/3600)) * signs[lng_dir]
    return lat,lng

def parse_plain_txt_notam(text):
    text_lines = text.splitlines()
    coords_unparse = []
    for index, line in enumerate(text_lines):
        text_lines[index] = line.rstrip()
    for line in text_lines:
        if line[-3:] == ' TO' or line[-3:] == 'HEL':
            coords_unparse.append(line[:15])

    return coords_unparse

def main():
    with open(os.path.join(dir_path, 'notam.txt')) as f:
        test_notam = f.read()
    notam_name = '01/122 (KZAB-A0011/22)'
    coords_unparse = parse_plain_txt_notam(test_notam)
    # coords_unparse = ['350910N0833730W','355543N0805628W','351602N0795242W','343300N0801615W','343522N0810041W','334830N0830608W']
    with open(os.path.join(dir_path, 'xml_front_matter.txt'), 'r') as f:
        xml = f.read()
    xml = xml.replace('<Placemark><name>NAME</name>',('<Placemark><name>%s</name>' % notam_name))
    xml = xml.replace('<Document><name>My document</name>',('<Document><name>%s</name>' % notam_name))
    for index, coord in enumerate(coords_unparse):
        lat, lng = parse_coords(coord)
        xml += ('\n%f,%f,0.0' % (lng, lat))
    lat, lng = parse_coords(coords_unparse[0])
    xml += ('\n%f,%f,0.0\n' % (lng, lat))
    with open(os.path.join(dir_path, 'xml_end_matter.txt'), 'r') as f:
        xml += f.read()

    with open(os.path.join(dir_path, 'kml_output.kml'), 'w+') as f:
        f.write(xml)

if __name__ == '__main__':
    main()