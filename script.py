import json
import numpy as np
import xml.etree.ElementTree as ET
import func

# чтение файла настроек
with open("data/settings_1_3D.json", 'r') as settings:
    settings_param = settings.read()

# преобразуем json строку в объект
settings_param = json.loads(settings_param)

# присваиваем переменным данные из настроек
sfm_file_name = settings_param["sfm_file_name"]
points_file_name = settings_param["points_file_name"]
actually_markers_list = settings_param["actually_markers_list"]
actually_param_list = settings_param["actually_param_list"]

with open(sfm_file_name, 'r') as sfm:
    data = sfm.read()

sfm_data = json.loads(data)

# формируем массивы точек до и после преобразования
in_point, out_point = func.get_points(actually_markers_list, sfm_data)

# расчитываем аффиное преобразование
affine_Matrix, affine_Vector = func.calculate_affine(in_point, out_point)

print("Affine transformation matrix:\n", affine_Matrix)
print("Affine transformation translation vector:\n", affine_Vector)

print("\nTESTING:")
for p, P in zip(np.array(in_point), np.array(out_point)):
    tranform_p = np.dot(affine_Matrix, p) + affine_Vector
    res = "[OK]" if np.allclose(tranform_p, P) else "[ERROR]"
    print(p, " mapped to: ", tranform_p, " ; expected: ", P, res)

print("\n")

func.affine_sfm_file(sfm_data, affine_Matrix, affine_Vector)

# читаем файл с координатами
root_node = ET.parse(points_file_name).getroot()

points_old = {}
# формируем словарь координат объекта
for tag in root_node.findall('point'):
    coords = [tag.attrib['x'], tag.attrib['y'], tag.attrib['z']]
    points_old[tag.attrib['name']] = [float(item) for item in coords]

points_new = {}
for key, value in points_old.items():
    points_new[key] = func.affine_point(affine_Matrix, affine_Vector, value)
    print(key, " old = ", np.round(value,4), ";  new =", np.round(points_new[key], 4))


for key, value in actually_param_list.items():
    old_dist = [10 * func.dist(points_old[item[0]], points_old[item[1]]) for item in value[1]]
    new_dist = [10 * func.dist(points_new[item[0]], points_new[item[1]]) for item in value[1]]
    print("\nname - ", key, " реальный размер - ", round(value[0],4), "см")
    for i in range(len(old_dist)):
        print("line ",value[1][i][0] + value[1][i][1], " - old dist = ", round(old_dist[i], 4), "см;  new dist = ", round(new_dist[i],4), "см")
    old_error = round(func.calculate_error(value[0], old_dist), 3)
    new_error = round(func.calculate_error(value[0], new_dist), 3)
    print("old error = ", old_error,"%", ";   new error = ", new_error,"%")

