# -*- coding: utf-8 -*-
"""
measure_speed.py — Alias compatible para medidor de velocidad de internet.
"""
from actions.measure_internet_speed import measure_internet_speed

def measure_speed(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return measure_internet_speed(parameters, player, speak, **kwargs)