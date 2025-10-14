"""
Package constants and defaults.
"""

DEFAULT_TOPICS = [
    "/log/ego_state",
    "/log/encounters",
    "/log/experiment_state",
    "/log/other_state",
    "/log/param/acceptance_radius",
    "/log/param/d_dot_max",
    "/log/param/dt",
    "/log/param/min_turning_angle",
    "/log/param/pred_horizon",
    "/log/param/r_ego",
    "/log/param/s_ddot_max",
    "/log/param/s_dot_max",
    "/log/param/t_h",
    "/log/param/time_parallel",
    "/log/param/time_turning",
    "/log/robustness/crossing/high",
    "/log/robustness/crossing/low",
    "/log/robustness/crossing/t_high",
    "/log/robustness/crossing/t_low",
    "/log/robustness/head_on/high",
    "/log/robustness/head_on/low",
    "/log/robustness/head_on/t_high",
    "/log/robustness/head_on/t_low",
    "/log/waypoints",
]

__all__ = ["DEFAULT_TOPICS"]
