#! /usr/bin/python3.6
import sys
import numpy as np
import scipy.linalg

START_INDEX_RUNS = 1
NB_POINTS_PER_POSE = 3
NB_POSES_PER_RUN = 2

def read_file(file_name):
    with open(file_name) as file:
        lines = file.readlines()
        runs = np.ndarray((int(len(lines) / (NB_POINTS_PER_POSE * NB_POSES_PER_RUN)), NB_POSES_PER_RUN, NB_POINTS_PER_POSE, 3))
        for line in lines:
            tokens = line.split(",")
            nb_digit = 0
            while ord(tokens[0][nb_digit]) >= 48 and ord(tokens[0][nb_digit]) <= 58:
                nb_digit += 1
            run_nb = int(tokens[0][:nb_digit]) - START_INDEX_RUNS
            pose_nb = 0 if tokens[0][nb_digit] <= "c" else 1
            point_nb = ord(tokens[0][nb_digit]) - (97 + (pose_nb * 3))
            runs[run_nb,pose_nb,point_nb,0] = tokens[1]
            runs[run_nb,pose_nb,point_nb,1] = tokens[2]
            runs[run_nb,pose_nb,point_nb,2] = tokens[3]
    return runs

def convert_points_to_transformation_matrix(first_point, second_point, third_point):
    origin = first_point
    x = second_point - origin
    x /= np.linalg.norm(x)
    y = np.cross(x, third_point - origin)
    y /= np.linalg.norm(y)
    z = np.cross(x, y)
    T = np.eye(4)
    T[:3,0] = x
    T[:3,1] = y
    T[:3,2] = z
    T[:3,3] = origin
    return T

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Incorrect number of arguments. Argument 1 must be the path to the csv file containing husky measurements for the different runs!")
    
    runs = read_file(sys.argv[1])
    for i in range(runs.shape[0]):
        T1 = convert_points_to_transformation_matrix(runs[i,0,0,:], runs[i,0,1,:], runs[i,0,2,:])
        T2 = convert_points_to_transformation_matrix(runs[i,1,0,:], runs[i,1,1,:], runs[i,1,2,:])
        T = np.linalg.inv(T1) @ T2
        print("Computed transformation for run " + str(i + START_INDEX_RUNS) + ":\n" + str(T) + "\n")

