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
            run_nb = int(tokens[0][0]) - START_INDEX_RUNS
            pose_nb = 0 if tokens[0][1] <= "c" else 1
            point_nb = ord(tokens[0][1]) - (97 + (pose_nb * 3))
            runs[run_nb,pose_nb,point_nb,0] = tokens[1]
            runs[run_nb,pose_nb,point_nb,1] = tokens[2]
            runs[run_nb,pose_nb,point_nb,2] = tokens[3]
    return runs

def convert_points_to_coordinate_frame(first_point, second_point, third_point):
    origin = first_point
    x = second_point - origin
    x /= np.linalg.norm(x)
    y = np.cross(x, third_point - origin)
    y /= np.linalg.norm(y)
    z = np.cross(x, y)
    return (origin, x, y, z)

def compute_transformation(origin1, x1, y1, z1, origin2, x2, y2, z2):
    A = np.zeros((9,9))
    A[0,0:3] = A[1,3:6] = A[2,6:9] = x1
    A[3,0:3] = A[4,3:6] = A[5,6:9] = y1
    A[6,0:3] = A[7,3:6] = A[8,6:9] = z1
    b = np.hstack([x2, y2, z2])
    x = np.linalg.solve(A, b)
    
    R = np.ndarray((3,3))
    R[0] = x[0:3]
    R[1] = x[3:6]
    R[2] = x[6:9]
    col2 = np.cross(R[:,0], R[:,1])
    col2 /= np.linalg.norm(col2)
    col0 = np.cross(R[:,1], R[:,2])
    col0 /= np.linalg.norm(col0)
    col1 = np.cross(col2, col0)
    R = np.vstack([col0, col1, col2]).T

    t = np.vstack([x1, y1, z1]) @ (origin2 - origin1)

    T = np.eye(4)
    T[:3,:3] = R
    T[:3,3] = t

    return T

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Incorrect number of arguments. Argument 1 must be the path to the csv file containing husky measurements for the different runs!")
    
    runs = read_file(sys.argv[1])
    for i in range(runs.shape[0]):
        (origin1, x1, y1, z1) = convert_points_to_coordinate_frame(runs[i,0,0,:], runs[i,0,1,:], runs[i,0,2,:])
        (origin2, x2, y2, z2) = convert_points_to_coordinate_frame(runs[i,1,0,:], runs[i,1,1,:], runs[i,1,2,:])
        T = compute_transformation(origin1, x1, y1, z1, origin2, x2, y2, z2)
        print("Computed transformation for run " + str(i + START_INDEX_RUNS) + ":\n" + str(T) + "\n")

