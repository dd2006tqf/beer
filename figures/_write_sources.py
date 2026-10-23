# -*- coding: utf-8 -*-
"""写 FIGURE_SOURCES.json（机器可读的图-数据绑定）。只列脚本真实读取的文件与字段。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
sources = {
    "fig_eda_style_pca": ["supp_eda.json::style_counts", "supp_eda.json::pca_chem"],
    "fig_q1_missing_pattern": ["supp_eda.json::missing"],
    "fig_q1_pred_perf": ["problem_1_results.json::fig_data.qwk_ranked",
                         "problem_1_results.json::summary.mean_qwk_main"],
    "fig_q1_calibration": ["problem_1_results.json::calibration"],
    "fig_q2_coexpr_network": ["problem_2_results.json::fig_data.network_nodes",
                              "problem_2_results.json::fig_data.network_edges",
                              "problem_2_results.json::graph"],
    "fig_q2_top3_heatmap": ["problem_2_results.json::per_dim",
                            "problem_1_results.json::fig_data.qwk_ranked"],
    "fig_q2_stability": ["problem_2_results.json::fig_data.top1_freq_ranked",
                         "problem_2_results.json::summary.n_bootstrap"],
    "fig_q2_chem_sensory_corr": ["supp_eda.json::chem_sensory_corr"],
    "fig_q3_style_radar": ["problem_3_results.json::fig_data.radar"],
    "fig_q3_realvsgen": ["problem_3_results.json::fig_data.pca",
                         "problem_3_results.json::summary.ks_distance_by_style"],
    "fig_q3_transfer_defect": ["problem_3_results.json::fig_data.defect_dumbbell",
                               "problem_3_results.json::transfer_info"],
}
with open(os.path.join(HERE, 'FIGURE_SOURCES.json'), 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=1)
print('FIGURE_SOURCES.json written;', len(sources), 'figures')
