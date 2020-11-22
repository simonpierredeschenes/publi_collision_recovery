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

def compute_transformation(first_point_start, second_point_start, third_point_start, first_point_end, second_point_end, third_point_end):
    pa = second_point_start - first_point_start
    qa = third_point_start - first_point_start
    ra = np.cross(pa, qa)
    ra /= np.linalg.norm(ra)
    pb = second_point_end - first_point_end
    qb = third_point_end - first_point_end
    rb = np.cross(pb, qb)
    rb /= np.linalg.norm(rb)

    A = np.zeros((9,9))
    A[0,0:3] = A[1,3:6] = A[2,6:9] = pa
    A[3,0:3] = A[4,3:6] = A[5,6:9] = qa
    A[6,0:3] = A[7,3:6] = A[8,6:9] = ra
    b = np.hstack([pb, qb, rb])
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

    t = first_point_end - first_point_start

    T = np.eye(4)
    T[:3,:3] = R
    T[:3,3] = t

    return T

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Incorrect number of arguments. Argument 1 must be the path to the csv file containing husky measurements for the different runs!")
    
    runs = read_file(sys.argv[1])
    for i in range(runs.shape[0]):
        T = compute_transformation(runs[i,0,0,:], runs[i,0,1,:], runs[i,0,2,:], runs[i,1,0,:], runs[i,1,1,:], runs[i,1,2,:])
        print("Computed transformation for run " + str(i + START_INDEX_RUNS) + ":\n" + str(T) + "\n")

