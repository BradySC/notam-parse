import os, re
import pandas as pd

dir_path = os.path.dirname(os.path.abspath(__file__))

class NOTAM:
    def __init__(self, notam, circle = False):
        self.NotamDict = notam
        self.circle = True if re.search('([0-9]{1,3}NM RADIUS OF )', self.NotamDict['NOTAM Text']) is not None else False

    @property
    def Location(self):
        return self.NotamDict['Location']

    @property
    def Identifier(self):
        return self.NotamDict['ID']

    @property
    def Identification(self):
        return self.NotamDict['NOTAM #/LTA #']

    @property
    def IssueDate(self):
        return self.NotamDict['Issue Date (UTC)']

    @property
    def EffDate(self):
        return self.NotamDict['Effective Date (UTC)']

    @property
    def ExpirDate(self):
        return self.NotamDict['Expiration Date (UTC)']

    @property
    def NotamText(self):
        return self.NotamDict['NOTAM Text']

    @property
    def CoordsStrList(self):
        text_lines = self.NotamText.splitlines()
        coords_unparse = []
        for index, line in enumerate(text_lines):
            text_lines[index] = line.rstrip()
        for line in text_lines:
            if line[-3:] == ' TO' or line[-3:] == 'HEL':
                coords_unparse.append(line[:15])
        return coords_unparse

    @property
    def CircleCoords(self):
        text_lines = self.NotamText.splitlines()
        for index, line in enumerate(text_lines):
            if 'RADIUS OF ' in line:
                center_point = re.findall('([0-9]{6}(N|S)[0-9]{7}(E|W))', line)[0]
            else:
                center_point = None
        return center_point

    def __str__(self):
        return (
            (
                'Location: %s\n'
                'NOTAM #/LTA #: %s\n'
                'Issue Date (UTC): %s\n'
                'Effective Date (UTC): %s\n'
                'Expiration Date (UTC): %s\n'
                'NOTAM Text: \n%s'
            ) %
            (
                self.Location, 
                self.Identification, 
                self.IssueDate, 
                self.EffDate, 
                self.ExpirDate, 
                self.NotamText
                )
            )


def read_xlsx(filename):
    notams_df = pd.read_excel(os.path.join(dir_path, filename))
    notams_df.rename(columns={'NOTAM Condition/LTA subject/Construction graphic title': 'NOTAM Text'}, inplace=True)
    notams_df = notams_df.loc[notams_df['Class'] == 'Airspace'].copy()
    notams_dict = notams_df.to_dict('records')
    return notams_dict

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

def build_kml(kml_string, Notam):
    notam_name = '%s - %s' % (Notam.Location, Notam.Identification)
    kml_string = kml_string.replace('<Document><name>My document</name>',('<Document><name>%s</name>' % notam_name))
    kml_string = kml_string.replace('<Placemark><name>NAME</name>',('<Placemark><name>%s</name>' % notam_name))
    kml_string = kml_string.replace('<description>YES</description>',('<description>%s</description>' % Notam))
    for index, coord in enumerate(Notam.CoordsStrList):
        lat, lng = parse_coords(coord)
        kml_string += ('\n%f,%f,0.0' % (lng, lat))

    lat, lng = parse_coords(Notam.CoordsStrList[0])
    kml_string += ('\n%f,%f,0.0\n' % (lng, lat))
    return kml_string

def main(filename):
    notams_dict = read_xlsx(filename)
    kml_start = open(os.path.join(dir_path, 'kml_front_matter.kml'), 'r').read()
    kml_middle = open(os.path.join(dir_path, 'kml_int_matter.kml'), 'r').read()
    kml_end = open(os.path.join(dir_path, 'kml_end_matter.kml'), 'r').read()
    circle_check = 0
    for index, notam in enumerate(notams_dict):
        Notam = NOTAM(notam)
        if Notam.circle:
            if index == 0:
                circle_check = index+1
            continue
        if circle_check == index and index == 1:
            kml = build_kml(kml_start, Notam)
        else:
            kml += build_kml(kml_middle, Notam)
    
    kml += kml_end
    with open(os.path.join(dir_path, 'kml_output.kml'), 'w+') as f:
        f.write(kml)

if __name__ == '__main__':
    main(os.path.join(dir_path, '5g_notams.xlsx'))
    # notam_dict = read_xlsx('5g_notams.xlsx')[0]
    # Notam = NOTAM(notam_dict)
    # print(Notam)