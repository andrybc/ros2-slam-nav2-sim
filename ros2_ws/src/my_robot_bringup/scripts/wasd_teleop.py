#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class WasdTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Max commanded speeds
        self.max_linear_speed = 0.5
        self.max_angular_speed = 1.5

        # How quickly speed changes
        self.linear_accel = 1.2      # m/s^2
        self.angular_accel = 3.0     # rad/s^2

        # Current published velocity
        self.current_linear = 0.0
        self.current_angular = 0.0

        # Target velocity from keyboard input
        self.target_linear = 0.0
        self.target_angular = 0.0

        # How long to keep a command alive after last key press
        self.key_timeout = 0.15
        self.last_key_time = self.get_clock().now()

        # Publish/update rate
        self.dt = 0.05  # 20 Hz
        self.timer = self.create_timer(self.dt, self.update)

        self.get_logger().info('Smooth WASD teleop started')
        self.get_logger().info('Hold: w/s forward-back, a/d left-right')
        self.get_logger().info('Space = hard stop, q = quit')

    def clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(value, high))

    def approach(self, current: float, target: float, step: float) -> float:
        if current < target:
            return min(current + step, target)
        if current > target:
            return max(current - step, target)
        return current

    def publish_cmd(self) -> None:
        msg = Twist()
        msg.linear.x = self.current_linear
        msg.angular.z = self.current_angular
        self.pub.publish(msg)

    def hard_stop(self) -> None:
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.publish_cmd()

    def get_key_nonblocking(self):
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    def update(self) -> None:
        now = self.get_clock().now()

        key = self.get_key_nonblocking()

        if key is not None:
            self.last_key_time = now

            if key == 'w':
                self.target_linear = self.max_linear_speed
                self.target_angular = 0.0

            elif key == 's':
                self.target_linear = -self.max_linear_speed
                self.target_angular = 0.0

            elif key == 'a':
                self.target_linear = 0.0
                self.target_angular = self.max_angular_speed

            elif key == 'd':
                self.target_linear = 0.0
                self.target_angular = -self.max_angular_speed

            elif key == ' ':
                self.get_logger().info('hard stop')
                self.hard_stop()
                return

            elif key == 'q':
                self.get_logger().info('quit')
                self.hard_stop()
                raise KeyboardInterrupt

        # If no recent key press, slowly return target to zero
        elapsed = (now - self.last_key_time).nanoseconds / 1e9
        if elapsed > self.key_timeout:
            self.target_linear = 0.0
            self.target_angular = 0.0

        # Smoothly move current velocities toward target velocities
        linear_step = self.linear_accel * self.dt
        angular_step = self.angular_accel * self.dt

        self.current_linear = self.approach(
            self.current_linear, self.target_linear, linear_step
        )
        self.current_angular = self.approach(
            self.current_angular, self.target_angular, angular_step
        )

        self.current_linear = self.clamp(
            self.current_linear, -self.max_linear_speed, self.max_linear_speed
        )
        self.current_angular = self.clamp(
            self.current_angular, -self.max_angular_speed, self.max_angular_speed
        )

        self.publish_cmd()

    def run(self) -> None:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            rclpy.spin(self)
        except KeyboardInterrupt:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.hard_stop()


def main():
    rclpy.init()
    node = WasdTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()