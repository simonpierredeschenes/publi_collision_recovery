#! /bin/bash

if [ $# -ne 2 ]
then
  echo "Incorrect number of arguments! Argument 1 is the map bag file. Argument 2 is the file in which to store the resulting map."
  exit
fi

bag_file=$1
map_file=$2

roslaunch publi_collision_recovery cube.launch bagfile:="$bag_file" use_skew_weights:=false final_map_file_name:="$map_file" &
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

