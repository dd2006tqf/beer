# -*- coding: utf-8 -*-
"""已合并进 q1_extra_metrics.py，保留此文件仅为避免旧命令失效。

原先此脚本单独产出"与 4.csv 连续值的 Pearson"，现在 q1_extra_metrics.py
同时给出 pearson_vs_cont 与 pearson_vs_level 两种口径，表 5 采用前者。
运行它等价于运行 q1_extra_metrics.py。
"""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(HERE, "q1_extra_metrics.py"), run_name="__main__")
