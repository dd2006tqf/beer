# 能力清单验收总账（逐项）

- ✅ **P1-C1** [machine] PASS — 产物 submission/q1_sensory_scores.csv 已产出（29129 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P1-C2** [semantic] PASS — 结论 PASS —— code/problem1.py run()：Xv 保留 NaN 直接喂 LightGBM(_fit_lgb, LGBMRegressor 原生缺失)，assert Xv.shape[0]==250；_validate 断言 n_na_rows>0（实际 63 行含缺失全部参与训练）
- ✅ **P1-C3** [machine] PASS — 结论 PASS —— code/utils.py:131-136 Binner.transform= searchsorted+np.clip(0,6)+round+astype(int)；constraint_audit.py q1_level PASS n_violations=0，submission/q1_sensory_scores.csv 全 0-6 整数
- ✅ **P1-C4** [semantic] PASS — 结论 PASS —— code/problem1.py 折循环：Binner().fit(ytr_c) 仅训练折；SimpleImputer/KNNImputer.fit(Xv[tr]) 仅训练折；_summarize 逐维 QWK/MAE/R² 来自 out-of-fold 验证折
- ✅ **P2-C1** [semantic] PASS — 结论 PASS —— code/problem2.py:build_coexpr_graph 以 231 化合物为节点、2.csv R 为边权 |w|>=0.5 建 nx.Graph，greedy_modularity_communities 社区；结果 231节点/645边/62社区/模块度Q=0.638
- ✅ **P2-C2** [machine] PASS — 产物 submission/q2_top3_compounds.csv 已产出（21736 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P2-C3** [semantic] PASS — 结论 PASS —— code/problem2.py:_fuse_and_stability bootstrap B=500 np.random.choice(replace=True) 重算 Top-3 入选频率；跨方法 Jaccard=三法(SHAP/6.csv相关/RF) 两两 _jaccard
- ✅ **P2-C4** [semantic] PASS — 结论 PASS —— submission/q2_top3_compounds.csv 每行有 mechanism(机理)+cross_corr_abs(6.csv证据)+feature_type；A_esters_isoaa Top-1=isopentyl_acetate(香蕉酯,机理正确)
- ✅ **P3-C1** [semantic] PASS — 结论 PASS —— code/problem3.py CVAE decode(z, onehot(style)) 以 tasting_category_fine 为条件；KS 距离 Tripel0.357/Kriek0.398/Lambic0.408，三风格生成谱两两欧氏距离大(Kriek 显著不同)
- ✅ **P3-C2** [machine] PASS — 产物 submission/q3_generated_profiles.csv 已产出（205787 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P3-C3** [semantic] PASS — 结论 PASS —— code/problem3.py:_transfer 隐空间平移 Δ=z̄_t−z̄_s + 式13 np.minimum 投影 4 缺陷列；缺陷合规率 44/44=1.0
- ⏳ **P3-C4** [semantic][可选] PENDING — 缺考官结论：CAPABILITY_VERDICT.json 里没有 P3-C4 的 verdict（可选项，不阻断）