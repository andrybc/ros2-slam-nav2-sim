#!/usr/bin/env python3
"""
Odometry yaw vs. Gazebo ground-truth yaw.

Commands a pure in-place rotation at a fixed angular velocity for a fixed
duration in SIMULATION time, accumulating yaw from two independent sources:

  odom yaw   from /odom (what the DiffDrive plugin believes)
  true yaw   from `gz model -m <model> -p` (what the physics engine did)

Prints, per trial and in aggregate, the ratio odom_yaw / true_yaw.

Run this with SLAM NOT running. slam.launch.py must be stopped; use
sim.launch.py only. If SLAM is publishing map->odom, this measurement is
still valid (it only reads /odom), but stopping SLAM removes any doubt.

Usage:
  ros2 run my_robot_bringup odom_yaw_test.py --w 0.5 --duration 4.0 --trials 3
"""

import argparse
import math
import re
import subprocess
import sys
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def wrap_to_pi(a):
    return math.atan2(math.sin(a), math.cos(a))


def yaw_from_quat(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


_POSE_TRIPLE = re.compile(r"\[\s*(-?[\d.eE+-]+)\s*\|\s*(-?[\d.eE+-]+)\s*\|\s*(-?[\d.eE+-]+)\s*\]")


def gz_truth_yaw(model):
    """Shell out to `gz model -p` and pull yaw (rad) out of the RPY triple.

    Output format differs slightly between Gazebo releases, so this takes the
    second bracketed [a | b | c] triple that follows the word 'Pose', which is
    the R P Y row in Harmonic.
    """
    try:
        out = subprocess.run(
            ["gz", "model", "-m", model, "-p"],
            capture_output=True, text=True, timeout=5.0,
        ).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        raise RuntimeError(f"could not query gz for model '{model}': {e}")

    idx = out.find("Pose")
    if idx == -1:
        raise RuntimeError(
            "no 'Pose' block in `gz model` output. Is the model name right?\n"
            "Check with: gz model --list\n--- got ---\n" + out
        )
    triples = _POSE_TRIPLE.findall(out[idx:])
    if len(triples) < 2:
        raise RuntimeError("could not parse an RPY triple from:\n" + out[idx:])
    return float(triples[1][2])


class YawTest(Node):
    def __init__(self, model, w, duration, settle):
        super().__init__("odom_yaw_test")
        # Sim time matters: if Gazebo runs at a real-time factor below 1.0,
        # a wall-clock duration commands a different amount of rotation than
        # you think it does. Everything below is timed off the /clock.
        self.set_parameters([rclpy.parameter.Parameter("use_sim_time", value=True)])

        self.model = model
        self.w = w
        self.duration = duration
        self.settle = settle

        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.sub = self.create_subscription(Odometry, "/odom", self._on_odom, 50)
        self._odom_yaw = None
        self._lock = threading.Lock()

    def _on_odom(self, msg):
        q = msg.pose.pose.orientation
        with self._lock:
            self._odom_yaw = yaw_from_quat(q.x, q.y, q.z, q.w)

    def odom_yaw(self):
        with self._lock:
            return self._odom_yaw

    def _spin_for(self, secs):
        """Spin, blocking, for `secs` of SIM time."""
        t0 = self.get_clock().now()
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.02)
            if (self.get_clock().now() - t0).nanoseconds / 1e9 >= secs:
                return

    def _command(self, wz):
        m = Twist()
        m.angular.z = wz
        self.pub.publish(m)

    def wait_for_odom(self, timeout=15.0):
        t0 = self.get_clock().now()
        while rclpy.ok() and self.odom_yaw() is None:
            rclpy.spin_once(self, timeout_sec=0.1)
            if (self.get_clock().now() - t0).nanoseconds / 1e9 > timeout:
                raise RuntimeError(
                    "no /odom messages. Is sim.launch.py running and the "
                    "ros_gz_bridge up? Check: ros2 topic hz /odom"
                )

    def run_trial(self):
        # Let everything settle so we start from rest, not mid-coast.
        self._command(0.0)
        self._spin_for(self.settle)

        odom_acc = 0.0
        true_acc = 0.0
        odom_prev = self.odom_yaw()
        true_prev = gz_truth_yaw(self.model)

        t0 = self.get_clock().now()
        while rclpy.ok():
            self._command(self.w)
            rclpy.spin_once(self, timeout_sec=0.05)

            o = self.odom_yaw()
            if o is not None:
                odom_acc += wrap_to_pi(o - odom_prev)
                odom_prev = o

            t = gz_truth_yaw(self.model)
            true_acc += wrap_to_pi(t - true_prev)
            true_prev = t

            if (self.get_clock().now() - t0).nanoseconds / 1e9 >= self.duration:
                break

        # Stop, then keep integrating through the coast-down so that any
        # rotation after cmd_vel goes to zero is counted on both sides.
        self._command(0.0)
        t1 = self.get_clock().now()
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            o = self.odom_yaw()
            if o is not None:
                odom_acc += wrap_to_pi(o - odom_prev)
                odom_prev = o
            t = gz_truth_yaw(self.model)
            true_acc += wrap_to_pi(t - true_prev)
            true_prev = t
            if (self.get_clock().now() - t1).nanoseconds / 1e9 >= self.settle:
                break

        return odom_acc, true_acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=float, default=0.5, help="commanded yaw rate, rad/s")
    ap.add_argument("--duration", type=float, default=4.0, help="turn duration, SIM seconds")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--settle", type=float, default=1.0, help="rest/coast-down time, sim s")
    ap.add_argument("--model", type=str, default="my_robot")
    args = ap.parse_args()

    rclpy.init()
    node = YawTest(args.model, args.w, args.duration, args.settle)
    try:
        node.wait_for_odom()
        print(f"\ncommanded {args.w} rad/s for {args.duration} s  "
              f"(nominal {math.degrees(args.w * args.duration):.1f} deg)\n")
        print(f"{'trial':>5}  {'odom (deg)':>11}  {'true (deg)':>11}  {'ratio':>7}")
        print("-" * 40)

        ratios = []
        for i in range(args.trials):
            o, t = node.run_trial()
            if abs(t) < 1e-6:
                print(f"{i+1:>5}  {math.degrees(o):>11.2f}  {math.degrees(t):>11.2f}  "
                      f"{'n/a':>7}   <- robot did not rotate; is it against a wall?")
                continue
            r = o / t
            ratios.append(r)
            print(f"{i+1:>5}  {math.degrees(o):>11.2f}  {math.degrees(t):>11.2f}  {r:>7.4f}")

        if ratios:
            mean = sum(ratios) / len(ratios)
            spread = max(ratios) - min(ratios)
            print("-" * 40)
            print(f"mean ratio odom/true = {mean:.4f}   (spread {spread:.4f}, n={len(ratios)})")
            print(f"odometry over-reports yaw by {(mean - 1.0) * 100:+.1f}%")
    except (RuntimeError, KeyboardInterrupt) as e:
        print(f"\n{e}", file=sys.stderr)
    finally:
        try:
            node._command(0.0)
            rclpy.spin_once(node, timeout_sec=0.2)
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
