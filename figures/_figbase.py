# -*- coding: utf-8 -*-
"""数据图公共引导：路径注入 + JSON 载入 + 配色/口径工具。数据全部来自真实产物。"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from _utils.plot_utils import (setup_style, save_fig, PALETTE, PALETTE_LIGHT, COLORS,
                               _lighten, set_paper_placement, declutter_axes,
                               dynamic_limits, smart_labels, auto_legend)
setup_style()


def load(name):
    for base in (HERE, os.path.join(ROOT, 'output')):
        p = os.path.join(base, name)
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                return json.load(f)
    raise FileNotFoundError(name)


P1 = load('problem_1_results.json')
P2 = load('problem_2_results.json')
P3 = load('problem_3_results.json')
SUPP = load('supp_eda.json')


def panel(ax, tag):
    ax.set_title(tag, fontsize=11, fontweight='bold', loc='left', pad=3)


# 感官维中文短名映射（50 维：香=A_、味=F_ 前缀 + 基词；另有口感/缺陷维）
_BASE_ZH = {
    'malt_all': '麦芽', 'malt_grain': '谷物', 'malt_bread': '面包', 'malt_cara': '焦糖',
    'malt_burn': '烟熏', 'hops_all': '酒花', 'hops_citrus': '柑橘', 'hops_tropical': '热带',
    'hops_noble': '贵族花', 'hops_woody': '木质', 'esters_all': '酯', 'esters_ethac': '指甲油',
    'esters_isoaa': '香蕉酯', 'esters_flower': '花香酯', 'esters_fruity': '果香酯',
}
_STD_ZH = {
    'acidity': '酸度', 'bitternes': '苦味', 'sweetness': '甜味', 'X4vg': '4VG',
    'diacetyl': '双乙酰', 'dms': 'DMS', 'metallic': '金属味', 'stale_hops': '陈酒花',
    't2n': '反2壬烯醛', 'orange': '橙香', 'coriander': '芫荽', 'clove': '丁香',
    'lactic': '乳酸', 'acetic': '乙酸', 'barnyard': '畜棚味', 'alcohol': '酒精',
    'aftertaste': '余味', 'body': '酒体', 'co2': '碳酸', 'overall': '总体',
}


def dim_zh(k):
    if k in _STD_ZH:
        return _STD_ZH[k]
    if k[:2] in ('A_', 'F_'):
        pre = '香·' if k[0] == 'A' else '味·'
        base = _BASE_ZH.get(k[2:], k[2:].replace('_', ''))
        return pre + base
    return k.replace('_', ' ')


# 兼容旧引用
DIM_ZH = {k: dim_zh(k) for k in list(_BASE_ZH) + list(_STD_ZH)}
