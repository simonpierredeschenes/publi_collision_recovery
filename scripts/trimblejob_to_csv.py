#! /usr/bin/python3.6

import sys
import xml.etree.ElementTree as ET
import math

def spherical_to_cartesian(HA, VA, SD):
    x = SD * math.cos(-HA) * math.sin(VA)
    y = SD * math.sin(-HA) * math.sin(VA)
    z = SD * math.cos(VA)
    return (x, y, z)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise RuntimeError("Incorrect number of arguments. Argument 1 is the trimble job file to convert. Argument 2 is the output file name.")
   
    with open(sys.argv[2], "w") as csv:
        tree = ET.parse(sys.argv[1])
        field_book = tree.getroot()[0]

        for entry in field_book:
            if entry.tag == "PointRecord":
                measurement_name = entry[0].text
                if measurement_name != "station" and measurement_name != "ref":
                    HA = math.radians(float(entry[6][0].text))
                    VA = math.radians(float(entry[6][1].text))
                    SD = float(entry[6][2].text)
                    (x, y, z) = spherical_to_cartesian(HA, VA, SD)
                    csv.write(measurement_name + "," + str(x) + "," + str(y) + "," + str(z) + ",\n")

