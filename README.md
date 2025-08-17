This branch basically:
1. Creates a map using Turtlebot's 2D LiDAR Scan of one of ROS' many premade worlds (dqn_server3), and spits out a .pgm and .yaml file
2. Runs an EKF module on our Turtlebot, which fuses its wheel odom and IMU input.
3. Using the filtered odom, we then applied our ACML module on the generated map.
4. Link to video -> https://drive.google.com/file/d/1kkeTlemMrcpLVoDPtJlbi7yJ-nm2PKoM/view?usp=sharing
