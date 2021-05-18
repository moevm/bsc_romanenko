import json
import numpy as np
import xml.etree.ElementTree as ET
import func


with open("data/settings.json", 'r') as settings:
    settings_param = settings.read()

settings_param = json.loads(settings_param)

sfm_file_name = settings_param["sfm_file_name"]
points_file_name = settings_param["points_file_name"]
actually_markers_list = settings_param["actually_markers_list"]


in_point, out_point = func.get_points(actually_markers_list, sfm_file_name)

affine_Matrix, affine_Vector = func.calculate_affine(in_point, out_point)

print("Affine transformation matrix:\n", affine_Matrix)
print("Affine transformation translation vector:\n", affine_Vector)

print("\nTESTING:")
for p, P in zip(np.array(in_point), np.array(out_point)):
    image_p = np.dot(affine_Matrix, p) + affine_Vector
    result = "[OK]" if np.allclose(image_p, P) else "[ERROR]"
    print(p, " mapped to: ", image_p, " ; expected: ", P, result)

print("\n")
# читаем файл с координатами
root_node = ET.parse(points_file_name).getroot()

points_old = {}

# формируем словарь координат объекта
for tag in root_node.findall('point'): # Get the value from the attribute 'name'
    coords = [tag.attrib['x'], tag.attrib['y'], tag.attrib['z']]
    points_old[tag.attrib['name']] = [float(item) for item in coords]


points_new = {}

for key, value in points_old.items():
    points_new[key] = func.affine_point(affine_Matrix, affine_Vector, value)
    print(key, " old = ", value, ";  new =", points_new[key])


# список параметров объекта


param = {"sides": [29.5, [["A", "B"], ["A", "D"], ["C", "D"], ["B", "C"]]],
         "front_diag": [41.7193, [["A", "C"], ["B", "D"], ["E", "F"], ["K", "G"]]],
         "interior_diag": [42.3024821079, [["A", "F"], ["E", "C"], ["G", "D"], ["B", "K"]]],
         "lateral_diag": [30.3191358716, [["A", "K"], ["C", "G"], ["K", "C"], ["A", "G"]]]}



for key, value in param.items():
    old_dist = [10 * func.dist(points_old[item[0]], points_old[item[1]]) for item in value[1]]
    new_dist = [10 * func.dist(points_new[item[0]], points_new[item[1]]) for item in value[1]]
    print("\nname - ", key, " реальный размер - ", value[0], "см")
    for i in range(len(old_dist)):
        print("line ",value[1][i][0] + value[1][i][1], " - old dist = ", old_dist[i], "см;  new dist = ", new_dist[i], "см")
    old_error = round(func.calculate_error(value[0], old_dist), 3)
    new_error = round(func.calculate_error(value[0], new_dist), 3)
    print("old error = ", old_error,"%", ";   new error = ", new_error,"%")


