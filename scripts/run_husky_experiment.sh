#! /bin/bash

if [ $# -ne 2 ]
then
      echo "Incorrect number of arguments! Argument 1 is the transformation matrix output file. Argument 2 is the folder containing the bag files."
      exit
fi

matrix_file=$1
bagfile_folder=$2

> $matrix_file
for bagfile in "$bagfile_folder"/*.bag
do
  roslaunch publi_collision_recovery husky.launch bagfile:=$bagfile final_transformation_file_name:=$matrix_file &
  sleep 3
  while [[ ! -z `pgrep mapper_node` ]]
  do
      sleep 1
  done
  killall rviz
  killall imu_odom_node
  killall pointcloud2_deskew_node
  killall cloud_node_stamped
  killall static_transform_publisher
  killall rosmaster
done

