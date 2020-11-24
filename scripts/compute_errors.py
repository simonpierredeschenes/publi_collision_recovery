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

# ZYX euler angle convention (roll pitch yaw)
def rotation_matrix_to_rpy(R) :
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < 1e-6
    if not singular :
        roll = math.atan2(R[2,1] , R[2,2])
        pitch = math.atan2(-R[2,0], sy)
        yaw = math.atan2(R[1,0], R[0,0])
    else :
        roll = math.atan2(-R[1,2], R[1,1])
        pitch = math.atan2(-R[2,0], sy)
        yaw = 0
    return (roll, pitch, yaw)

def rotation_matrix_to_axis_angle(R):
    angle = abs(math.acos((R.trace() - 1.0) / 2.0))
    singular = angle < 1e-6 or abs(angle - math.pi) < 1e-6
    if not singular:
        axis = np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]]) / (2 * math.sin(angle))
    else:
        (eigen_values,eigen_vectors) = np.linalg.eig(R)
        for i in range(len(eigen_values)):
            if abs(eigen_values[i].real - 1) < 1e-6 and abs(eigen_values[i].imag) < 1e-6:
                axis = eigen_vectors[i]
                break
    return (axis, angle)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise RuntimeError("Incorrect number of arguments! Argument 1 is the mapper matrix file. Argument 2 is the thedolite matrix file.")

    mapper_matrices = read_mapper_file(sys.argv[1])
    theodolite_matrices = read_theodolite_file(sys.argv[2])
    for i in range(mapper_matrices.shape[0]):
        translation_errors = theodolite_matrices[i,:3,3] - mapper_matrices[i,:3,3]
        (roll_theodolite, pitch_theodolite, yaw_theodolite) = rotation_matrix_to_rpy(theodolite_matrices[i,:3,:3])
        (roll_mapper, pitch_mapper, yaw_mapper) = rotation_matrix_to_rpy(mapper_matrices[i,:3,:3])
        (roll_error, pitch_error, yaw_error) = (roll_theodolite - roll_mapper, pitch_theodolite - pitch_mapper, yaw_theodolite - yaw_mapper)
        (_, angle_error) = rotation_matrix_to_axis_angle(theodolite_matrices[i,:3,:3].T @ mapper_matrices[i,:3,:3])
        print("Run " + str(i + 1) + ":")
        print("Translation error:\tx: " + str(translation_errors[0])[:NUMBER_OF_DIGITS] + "m,\t\ty: " + str(translation_errors[1])[:NUMBER_OF_DIGITS] + "m,\t\tz: " + str(translation_errors[2])[:NUMBER_OF_DIGITS] + "m,\t\ttotal: " + str(np.linalg.norm(translation_errors))[:NUMBER_OF_DIGITS] + "m")
        print("Rotation error:\t\troll: " + str(math.degrees(roll_error))[:NUMBER_OF_DIGITS] + "°,\tpitch: " + str(math.degrees(pitch_error))[:NUMBER_OF_DIGITS] + "°,\tyaw: " + str(math.degrees(yaw_error))[:NUMBER_OF_DIGITS] + "°,\t\ttotal: " + str(math.degrees(angle_error))[:NUMBER_OF_DIGITS] + "°")

