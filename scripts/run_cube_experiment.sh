#! /bin/bash

if [ $# -ne 3 ]
then
  echo "Incorrect number of arguments! Argument 1 is the folder containing the bag files. Argument 2 is the folder in which to store the results. Argument 3 is the model number to use (-1 for no model)."
  exit
fi

data_folder=$1
results_folder=$2
model_nb=$3

if [ ! -d $results_folder ]
then
        mkdir -p $results_folder
fi
matrix_file="$results_folder"/mapper.txt
> $matrix_file

use_skew_weights="true"
if [ $model_nb -eq -1 ]
then
  use_skew_weights="false"
fi

for run_bag in `ls -v "$data_folder"/run*.bag`
do
  run_bag_file_name=${run_bag##*/}
  run_nb=`echo $run_bag_file_name | grep -o "[0-9]*"`
  map_bag="$data_folder"/map"$run_nb".bag
  map_file="$results_folder"/map"$run_nb".vtk
  map_pose_file="$results_folder"/map"$run_nb"_pose.txt
  map_inertia_file="$results_folder"/inertia_map"$run_nb".csv
  run_inertia_file="$results_folder"/inertia_run"$run_nb".csv

  roslaunch publi_collision_recovery cube.launch bagfile:=$map_bag final_map_file_name:=$map_file final_map_pose_file_name:=$map_pose_file use_skew_weights:=$use_skew_weights skew_model:=$model_nb inertia_file_name:=$map_inertia_file &
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

  roslaunch publi_collision_recovery cube.launch bagfile:=$run_bag initial_map_file_name:=$map_file initial_map_pose:=$map_pose final_transformation_file_name:=$matrix_file use_skew_weights:=$use_skew_weights skew_model:=$model_nb inertia_file_name:=$run_inertia_file &
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

