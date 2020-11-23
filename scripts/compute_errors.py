#! /usr/bin/python3.6

import numpy as np
import sys
import math

NUMBER_OF_DIGITS = 8

def read_mapper_file(filename):
    with open(filename) as file:
        lines = file.readlines()
        matrices = np.ndarray((len(lines) // 4, 4, 4))
        for i, line in enumerate(lines):
            matrix_index = i // 4
            row_index = i % 4
            tokens = line[:-1].split(" ")
            col_index = 0
            for token in tokens:
                if token != "":
                    matrices[matrix_index,row_index,col_index] = float(token)
                    col_index += 1
        return matrices

def read_theodolite_file(filename):
    with open(filename) as file:
        lines = file.readlines()
        matrices = np.ndarray((len(lines) // 4, 4, 4))
        for i, line in enumerate(lines):
            matrix_index = i // 4
            row_index = i % 4
            tokens = line[:-1].replace("[", "").replace("]", "").split(" ")
            col_index = 0
            for token in tokens:
                if token != "":
                    matrices[matrix_index,row_index,col_index] = float(token)
                    col_index += 1
        return matrices

def rotation_matrix_to_euler_angles(R) :
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < 1e-6
    if not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
    return np.array([x, y, z])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise RuntimeError("Incorrect number of arguments! Argument 1 is the mapper matrix file. Argument 2 is the thedolite matrix file.")

    mapper_matrices = read_mapper_file(sys.argv[1])
    theodolite_matrices = read_theodolite_file(sys.argv[2])
    for i in range(mapper_matrices.shape[0]):
        translation_errors = theodolite_matrices[i,:3,3] - mapper_matrices[i,:3,3]
        rotation_errors = np.degrees(rotation_matrix_to_euler_angles(theodolite_matrices[i]) - rotation_matrix_to_euler_angles(mapper_matrices[i]))
        print("Run " + str(i + 1) + ":")
        print("Translation error:\tx: " + str(translation_errors[0])[:NUMBER_OF_DIGITS] + "m,\ty: " + str(translation_errors[1])[:NUMBER_OF_DIGITS] + "m,\tz: " + str(translation_errors[2])[:NUMBER_OF_DIGITS] + "m,\ttotal: " + str(np.linalg.norm(translation_errors))[:NUMBER_OF_DIGITS] + "m")
        print("Rotation error:\t\tx: " + str(rotation_errors[0])[:NUMBER_OF_DIGITS] + "°,\ty: " + str(rotation_errors[1])[:NUMBER_OF_DIGITS] + "°,\tz: " + str(rotation_errors[2])[:NUMBER_OF_DIGITS] + "°,\ttotal: " + str(np.linalg.norm(rotation_errors))[:NUMBER_OF_DIGITS] + "°")

