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
    if len(sys.argv) != 4:
        raise RuntimeError("Incorrect number of arguments! Argument 1 is the mapper matrix file. Argument 2 is the thedolite matrix file. Argument 3 is the csv output file.")

    mapper_matrices = read_mapper_file(sys.argv[1])
    theodolite_matrices = read_theodolite_file(sys.argv[2])
    with open(sys.argv[3], "w") as output_file:
        output_file.write("run_nb,x_travelled,x_error,y_travelled,y_error,z_travelled,z_error,translation,translation_error,roll_travelled,roll_error,pitch_travelled,pitch_error,yaw_travelled,yaw_error,rotation,rotation_error\n")
        for i in range(mapper_matrices.shape[0]):
            (x_travelled, y_travelled, z_travelled) = (abs(theodolite_matrices[i,0,3]), abs(theodolite_matrices[i,1,3]), abs(theodolite_matrices[i,2,3]))
            translation_errors = theodolite_matrices[i,:3,3] - mapper_matrices[i,:3,3]
            (x_error, y_error, z_error) = (abs(translation_errors[0]), abs(translation_errors[1]), abs(translation_errors[2]))
            translation = np.linalg.norm(theodolite_matrices[i,:3,3])
            translation_error = np.linalg.norm(translation_errors)
            (roll_theodolite, pitch_theodolite, yaw_theodolite) = rotation_matrix_to_rpy(theodolite_matrices[i,:3,:3])
            (roll_travelled, pitch_travelled, yaw_travelled) = (math.degrees(abs(roll_theodolite)), math.degrees(abs(pitch_theodolite)), math.degrees(abs(yaw_theodolite)))
            (roll_mapper, pitch_mapper, yaw_mapper) = rotation_matrix_to_rpy(mapper_matrices[i,:3,:3])
            (roll_error, pitch_error, yaw_error) = (math.degrees(abs(roll_theodolite - roll_mapper)), math.degrees(abs(pitch_theodolite - pitch_mapper)), math.degrees(abs(yaw_theodolite - yaw_mapper)))
            (_, rotation) = rotation_matrix_to_axis_angle(theodolite_matrices[i,:3,:3])
            rotation = math.degrees(abs(rotation))
            (_, rotation_error) = rotation_matrix_to_axis_angle(theodolite_matrices[i,:3,:3].T @ mapper_matrices[i,:3,:3])
            rotation_error = math.degrees(abs(rotation_error))
            print("Run " + str(i + 1) + ":")
            print("Translation error:\tx: " + str(x_error)[:NUMBER_OF_DIGITS] + "m,\t\ty: " + str(y_error)[:NUMBER_OF_DIGITS] + "m,\t\tz: " + str(z_error)[:NUMBER_OF_DIGITS] + "m,\t\ttotal: " + str(translation_error)[:NUMBER_OF_DIGITS] + "m")
            print("Rotation error:\t\troll: " + str(roll_error)[:NUMBER_OF_DIGITS] + "°,\tpitch: " + str(pitch_error)[:NUMBER_OF_DIGITS] + "°,\tyaw: " + str(yaw_error)[:NUMBER_OF_DIGITS] + "°,\t\ttotal: " + str(rotation_error)[:NUMBER_OF_DIGITS] + "°")
            output_file.write(str(i + 1) + "," + str(x_travelled) + "," + str(x_error) + "," + str(y_travelled) + "," + str(y_error) + "," + str(z_travelled) + "," + str(z_error) + "," + str(translation) + "," + str(translation_error) + "," + str(roll_travelled) + "," + str(roll_error) + "," + str(pitch_travelled) + "," + str(pitch_error) + "," + str(yaw_travelled) + "," + str(yaw_error) + "," + str(rotation) + "," + str(rotation_error) + "\n")
