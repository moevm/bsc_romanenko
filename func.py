import math
import numpy as np
import json

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

def get_points(actually_markers_list, sfm_data):

    # получаем список координат маркеров
    model_markers_list = {}

    for landmark in sfm_data["structure"]:
        if landmark["descType"] == "cctag3":
            # color[0] - id cctag3 маркера
            model_markers_list[landmark["color"][0]] = list(map(float, landmark["X"]))

    actually_markers_list = sorted(actually_markers_list.items(), key=lambda x: x[0])
    model_markers_list = sorted(model_markers_list.items(), key=lambda x: x[0])

    def all_the_same(elements):
        if len(elements) < 1:
            return True
        return len(elements) == elements.count(elements[0])

    # точки до и после преобразования отсортированные по порядку
    out_point = list(dict(actually_markers_list).values())
    in_point = list(dict(model_markers_list).values())

    # проверка на одинаковый параметр одной из координат у точек
    for i in range(len(in_point[0]) - 1):
        if(all_the_same([item[i] for item in out_point])):
            for point in in_point:
                point.pop(i)
            for point in out_point:
                point.pop(i)

    in_point = in_point[:len(in_point[0])+1]
    out_point = out_point[:len(in_point[0])+1]

    return in_point, out_point

def calculate_affine(in_point, out_point):
    # количество точек
    points_len = len(in_point)

    # матрица начальных точек
    input_matrix = np.vstack([np.transpose(in_point), np.ones(points_len)])  # добавляем единицы последней строкой

    # определитель в знаменателе формулы
    bottom_del = 1.0 / np.linalg.det(input_matrix)

    # функция для подсчета минорных определителей
    def minors(r, j):
        return np.linalg.det(np.delete(np.vstack([r, input_matrix]), (j + 1), axis=0))

    # перемножение матриц
    M = [[(-1) ** i * bottom_del * minors(R, i) for i in range(points_len)] for R in np.transpose(out_point)]

    # итоговые матрица и вектор
    affine_Matrix, affine_Vector = np.hsplit(np.array(M), [points_len - 1])
    affine_Vector = np.transpose(affine_Vector)[0]
    return affine_Matrix, affine_Vector


def affine_point(affine_Matrix,affine_Vector,point):
    if (len(point) != len(affine_Vector)):
        point2d = np.dot(affine_Matrix, [point[0],point[2]]) + affine_Vector
        return [point2d[0], point[1], point2d[1]]
    else:
        return (np.dot(affine_Matrix, point) + affine_Vector)


def calculate_error(act_param, params):
    param_len = len(params)
    for i in range(param_len):
        params[i] = (abs(act_param - params[i]))**2
    s = math.sqrt(sum(params)/(param_len*(param_len-1)))
    delta_x = 3.2 * s
    return (delta_x/act_param)*100


def affine_sfm_file(sfm_data, affine_Matrix, affine_Vector):
    new_landmark_list = []
    for landmark in sfm_data["structure"]:
       new_landmark = landmark;
       new_landmark["X"] = list(map(str, np.round(affine_point(affine_Matrix, affine_Vector, list(map(float, landmark["X"]))), 6)))
       new_landmark_list.append(new_landmark)
    sfm_data["structure"] = new_landmark_list
    with open('res.json', 'w') as outfile:
        json.dump(sfm_data, outfile)
    return
