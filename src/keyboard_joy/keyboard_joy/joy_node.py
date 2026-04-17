#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import sys
import termios
import tty
import threading
import os
import signal
import select
import yaml
from ament_index_python.packages import get_package_share_directory


class KeyboardJoy(Node):
    def __init__(self):
        super().__init__("keyboard_joy")

        self.declare_parameter("config", "")

        self.load_key_mappings()

        self.get_logger().info("KeyboardJoy Node Started")
        self.get_logger().info(f"Loaded axis mappings: {self.axis_mappings}")
        self.get_logger().info(f"Loaded button mappings: {self.button_mappings}")
        self.get_logger().info(
            f"Axis increment rate: {self.axis_increment_rate}, step: {self.axis_increment_step}"
        )

        self.joy_publisher = self.create_publisher(Joy, "joy", 10)

        max_axis_index = max([v[0] for v in self.axis_mappings.values()], default=-1)
        max_button_index = max(self.button_mappings.values(), default=-1)

        self.joy_msg = Joy()
        self.joy_msg.axes = [0.0] * (max_axis_index + 1) if max_axis_index >= 0 else []
        self.joy_msg.buttons = (
            [0] * (max_button_index + 1) if max_button_index >= 0 else []
        )

        self.active_axes = {}
        self.sticky_axes = {}
        self.last_buttons = (
            [0] * (max_button_index + 1) if max_button_index >= 0 else []
        )
        self.last_axes = [0.0] * (max_axis_index + 1) if max_axis_index >= 0 else []

        self.running = True
        self.lock = threading.Lock()

        self.listener_thread = threading.Thread(target=self.key_loop, daemon=True)
        self.listener_thread.start()

        self.timer = self.create_timer(0.1, self.publish_joy)

        if self.axis_increment_rate > 0:
            self.increment_timer = self.create_timer(
                self.axis_increment_rate, self.update_active_axes
            )

    def load_key_mappings(self):
        config_file_path = (
            self.get_parameter("config").get_parameter_value().string_value
        )

        if not config_file_path:
            config_file_path = os.path.join(
                get_package_share_directory("keyboard_joy"),
                "config",
                "key_mappings.yaml",
            )

        try:
            with open(config_file_path, "r") as file:
                key_mappings = yaml.safe_load(file)
        except FileNotFoundError:
            self.get_logger().error(f"Configuration file not found: {config_file_path}")
            key_mappings = {}

        self.axis_mappings = key_mappings.get("axes", {})
        self.button_mappings = key_mappings.get("buttons", {})

        parameters = key_mappings.get("parameters", {})
        self.axis_increment_rate = parameters.get("axis_increment_rate", 0.1)
        self.axis_increment_step = parameters.get("axis_increment_step", 0.05)

    def get_key(self, timeout=0.2):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                return sys.stdin.read(1)
            else:
                return ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def get_key_full(self, timeout=0.2):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    remaining = ""
                    try:
                        while True:
                            r, _, _ = select.select([sys.stdin], [], [], 0.01)
                            if r:
                                remaining += sys.stdin.read(1)
                            else:
                                break
                    except:
                        pass
                    return ch + remaining
                return ch
            else:
                return ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def _format_key(self, key):
        if key == " ":
            return "Space"
        elif len(key) == 1:
            return key.upper() if key.islower() else key
        else:
            return key

    def key_loop(self):
        def fmt(k):
            k = str(k)
            if k == " ":
                return "Space"
            if k in "0123456789":
                return f"Num{k}"
            return k.upper() if len(k) == 1 else k

        axis_info = ", ".join(
            [f"A{v[0]}={v[1]}:{fmt(k)}" for k, v in self.axis_mappings.items()]
        )
        button_info = ", ".join(
            [f"B{v}:{fmt(k)}" for k, v in self.button_mappings.items()]
        )
        self.get_logger().info(
            f"JOYSTICK MODE: Axes: {axis_info}, Buttons: {button_info}"
        )

        while self.running and rclpy.ok():
            key = self.get_key(timeout=0.2)

            if key == "\x03":
                os.kill(os.getpid(), signal.SIGINT)
                break

            buttons = [0] * len(self.joy_msg.buttons)
            axes = [0.0] * len(self.joy_msg.axes)

            pressed_keys = set()
            if key:
                pressed_keys.add(key)

            for _ in range(10):
                k = self.get_key(timeout=0.01)
                if k:
                    pressed_keys.add(k)

            for k, v in self.axis_mappings.items():
                if str(k) in pressed_keys:
                    axes[v[0]] = v[1]

            for k, v in self.button_mappings.items():
                if str(k) in pressed_keys:
                    buttons[v] = 1

            with self.lock:
                self.joy_msg.buttons = buttons
                self.joy_msg.axes = axes

                if buttons != self.last_buttons or axes != self.last_axes:
                    self.last_buttons = buttons
                    self.last_axes = axes

    def update_active_axes(self):
        with self.lock:
            for axis_idx, target_value in self.active_axes.items():
                if axis_idx < len(self.joy_msg.axes):
                    current = self.joy_msg.axes[axis_idx]
                    if target_value > 0:
                        self.joy_msg.axes[axis_idx] = min(
                            current + self.axis_increment_step, target_value
                        )
                    else:
                        self.joy_msg.axes[axis_idx] = max(
                            current - self.axis_increment_step, target_value
                        )

    def publish_joy(self):
        with self.lock:
            self.joy_msg.header.stamp = self.get_clock().now().to_msg()
            self.joy_publisher.publish(self.joy_msg)

    def destroy_node(self):
        self.running = False
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    keyboard_joy = KeyboardJoy()

    try:
        rclpy.spin(keyboard_joy)
    except KeyboardInterrupt:
        pass

    keyboard_joy.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
