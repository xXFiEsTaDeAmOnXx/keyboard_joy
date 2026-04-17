FROM ros:jazzy-perception-noble

WORKDIR /root/ros2_ws

COPY src/keyboard_joy /root/ros2_ws/src/

RUN cd /root/ros2_ws && \
  colcon build --symlink-install --packages-select keyboard_joy

RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
  echo "source /root/ros2_ws/install/setup.bash" >> ~/.bashrc

WORKDIR /root/ros2_ws
