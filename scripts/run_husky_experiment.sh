#! /bin/bash

if [ $# -ne 2 ]
then
      echo "Incorrect number of arguments! Argument 1 is the transformation matrix output file. Argument 2 is the folder containing the bag files."
      exit
fi

matrix_file=$1
bagfile_folder=$2

> $matrix_file
run_prefix="$bagfile_folder"/run
map_prefix="$bagfile_folder"/map
for run_bag in "$run_prefix"*.bag
do
  run_nb=${run_bag:`expr length "$run_prefix"`:1}
  map_bag="$map_prefix""$run_nb".bag
  map_file="$map_prefix""$run_nb".vtk
  map_pose_file="$map_prefix""$run_nb"_pose.txt

  roslaunch publi_collision_recovery husky.launch bagfile:=$map_bag final_map_file_name:=$map_file final_map_pose_file_name:=$map_pose_file &
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

  map_pose=`rosrun publi_collision_recovery read_matrix_file.py "$map_pose_file"`

  roslaunch publi_collision_recovery husky.launch bagfile:=$run_bag initial_map_file_name:=$map_file initial_map_pose:=$map_pose final_transformation_file_name:=$matrix_file &
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

