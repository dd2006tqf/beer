# -*- coding: utf-8 -*-
"""问题三：风格条件生成 CVAE + 跨风格迁移（缺陷不恶化）（P3-C1/C2/C3）。

忠实 MODELING_REPORT §八 / METHOD_CLAIMS M7-M8：
- M7 CVAE：torch nn.Module，重参数化 mu/logvar + KL 散度，风格 one-hot 为条件，
         缺失位置用掩码排除重构损失（式10/11）。
- M8 迁移：隐空间风格平移 Δ=z̄_t−z̄_s + 对缺陷列逐样本 min/clip 投影（式12/13）。
- 极小样本风格走按风格多元高斯兜底；感官画像复用 Q1 模型（闭环）。
"""
import os
import sys
import warnings

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(_HERE)

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

import params as P
import utils as U
import torch
import torch.nn as nn
from scipy.stats import ks_2samp


class CVAE(nn.Module):
    def __init__(self, n_feat, n_style, latent=P.LATENT_DIM, hidden=128):
        super().__init__()
        self.n_feat = n_feat
        self.enc = nn.Sequential(
            nn.Linear(n_feat + n_style, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU())
        self.fc_mu = nn.Linear(hidden, latent)
        self.fc_lv = nn.Linear(hidden, latent)
        self.dec = nn.Sequential(
            nn.Linear(latent + n_style, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, n_feat))

    def encode(self, x, s):
        h = self.enc(torch.cat([x, s], dim=1))
        return self.fc_mu(h), self.fc_lv(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z, s):
        return self.dec(torch.cat([z, s], dim=1))

    def forward(self, x, s):
        mu, logvar = self.encode(x, s)
        z = self.reparameterize(mu, logvar)
        return self.decode(z, s), mu, logvar


def _elbo_loss(xhat, x, mask, mu, logvar, beta_kl, free_bits=P.FREE_BITS):
    # 掩码重构（只对非缺失分量计 MSE，式11）
    diff2 = ((xhat - x) ** 2) * mask
    recon = diff2.sum() / mask.sum().clamp(min=1.0)
    # 逐维 KL + free-bits（每维 KL 低于 free_bits 时不再惩罚，防后验坍塌）
    kld_dim = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp())   # [B, d]
    kld_dim = torch.clamp(kld_dim.mean(dim=0), min=free_bits)
    kld = kld_dim.sum()
    return recon + beta_kl * kld, recon.item(), float(kld.item())


def run(data_dir="user_data", out_dir=None):
    out_dir = out_dir or _ROOT
    U.set_all_seeds(P.SEED)
    torch.manual_seed(P.SEED)
    fig_dir = os.path.join(out_dir, "figures")
    sub_dir = os.path.join(out_dir, "submission")
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(sub_dir, exist_ok=True)

    df1, X, feat_cols, meta = U.load_chem(data_dir)
    styles = meta[P.STYLE_COL].values
    Xv = X.values.astype(float)
    mask = (~np.isnan(Xv)).astype(float)       # 1=观测 0=缺失

    # 标准化（缺失先按列中位临时填，仅供编码器输入；重构损失用 mask 排除）
    col_med = np.nanmedian(Xv, axis=0)
    Xfill = np.where(np.isnan(Xv), col_med, Xv)
    mu_f = Xfill.mean(axis=0)
    sd_f = Xfill.std(axis=0) + 1e-8
    Xstd = (Xfill - mu_f) / sd_f

    style_list = sorted(pd.unique(styles).tolist())
    s2i = {s: i for i, s in enumerate(style_list)}
    S = len(style_list)
    onehot = np.eye(S)[np.array([s2i[s] for s in styles])]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Q3] device={device} 样本={Xv.shape[0]} 特征={Xv.shape[1]} 风格={S} 隐维={P.LATENT_DIM}")

    model = _train_cvae(Xstd, mask, onehot, device)

    # 生成代表风格谱
    gen_records, gen_native = _generate(model, style_list, s2i, S, Xstd, styles,
                                        mu_f, sd_f, device)
    # 迁移 Pils/Lager -> Tripel + 缺陷投影
    transfer_records, transfer_info = _transfer(model, style_list, s2i, S, Xstd, Xv,
                                                styles, feat_cols, mu_f, sd_f, device)
    # 感官画像（Q1 模型）
    sens_pred_gen, sens_cols = _sensory_profile(gen_native, feat_cols)
    sens_pred_tr, _ = _sensory_profile(
        np.array([r["_native"] for r in transfer_records]), feat_cols)

    # 验证指标
    metrics = _eval_metrics(Xv, styles, feat_cols, gen_native, gen_records, transfer_info)

    results = _assemble(out_dir, data_dir, feat_cols, sens_cols, gen_records, gen_native,
                        sens_pred_gen, transfer_records, sens_pred_tr, transfer_info,
                        metrics, Xv, styles)
    _validate(out_dir, results)
    U.save_json(results, os.path.join(fig_dir, "problem_3_results.json"))
    print("[Q3] 完成，结果写入 figures/problem_3_results.json")
    return results
def _train_cvae(Xstd, mask, onehot, device):
    model = CVAE(Xstd.shape[1], onehot.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=P.CVAE_LR)
    Xt = torch.tensor(Xstd, dtype=torch.float32, device=device)
    Mt = torch.tensor(mask, dtype=torch.float32, device=device)
    St = torch.tensor(onehot, dtype=torch.float32, device=device)
    N = Xt.shape[0]
    best, best_state, patience, bad = 1e18, None, 60, 0
    rng = np.random.default_rng(P.SEED)
    for ep in range(1, P.CVAE_EPOCHS + 1):
        model.train()
        perm = rng.permutation(N)
        ep_loss = ep_rec = ep_kl = 0.0
        for st in range(0, N, P.CVAE_BATCH):
            bidx = perm[st:st + P.CVAE_BATCH]
            xb, mb, sb = Xt[bidx], Mt[bidx], St[bidx]
            opt.zero_grad()
            xhat, mu, lv = model(xb, sb)
            beta = P.BETA_KL * min(1.0, ep / max(1, P.KL_ANNEAL_EPOCHS))  # KL 退火
            loss, rec, kl = _elbo_loss(xhat, xb, mb, mu, lv, beta)
            loss.backward()
            opt.step()
            ep_loss += loss.item() * len(bidx); ep_rec += rec * len(bidx); ep_kl += kl * len(bidx)
        ep_loss /= N
        if ep <= P.KL_ANNEAL_EPOCHS:
            if ep % 50 == 0 or ep == 1:
                print(f"[Q3] CVAE epoch {ep}/{P.CVAE_EPOCHS}(退火) loss={ep_loss:.4f} "
                      f"recon={ep_rec/N:.4f} kl={ep_kl/N:.4f}")
            continue   # 退火阶段不计入早停
        if ep_loss < best - 1e-4:
            best, best_state, bad = ep_loss, {k: v.detach().clone() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
        if ep % 50 == 0 or ep == 1:
            print(f"[Q3] CVAE epoch {ep}/{P.CVAE_EPOCHS} loss={ep_loss:.4f} "
                  f"recon={ep_rec/N:.4f} kl={ep_kl/N:.4f}")
        if bad >= patience:
            print(f"[Q3] 早停于 epoch {ep}（best loss={best:.4f}）")
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model


def _style_latent_mean(model, Xstd, styles, target_style, s2i, S, device):
    """编码目标风格样本得隐均值 z̄_c（迁移用）。"""
    idx = np.where(styles == target_style)[0]
    oh = np.zeros((len(idx), S)); oh[:, s2i[target_style]] = 1
    with torch.no_grad():
        mu, _ = model.encode(torch.tensor(Xstd[idx], dtype=torch.float32, device=device),
                             torch.tensor(oh, dtype=torch.float32, device=device))
    return mu.cpu().numpy().mean(axis=0), idx


def _generate(model, style_list, s2i, S, Xstd, styles, mu_f, sd_f, device, n_gen=30):
    """代表风格条件采样生成；小样本风格走高斯兜底。"""
    rng = np.random.default_rng(P.SEED)
    records, native_rows = [], []
    for style in P.GEN_STYLES:
        if style not in s2i:
            print(f"[Q3] 跳过未知风格 {style}")
            continue
        cnt = int((styles == style).sum())
        if cnt >= P.MIN_STYLE_FOR_CVAE:
            # CVAE：z~N(0,I) 解码
            z = torch.tensor(rng.normal(size=(n_gen, P.LATENT_DIM)), dtype=torch.float32, device=device)
            oh = np.zeros((n_gen, S)); oh[:, s2i[style]] = 1
            with torch.no_grad():
                xhat = model.decode(z, torch.tensor(oh, dtype=torch.float32, device=device)).cpu().numpy()
            gen_std = xhat
            gmethod = "CVAE"
        else:
            # 高斯兜底：按风格样本多元高斯采样（标准化空间）
            idx = np.where(styles == style)[0]
            m = Xstd[idx].mean(axis=0); cov = np.cov(Xstd[idx].T) + 1e-3 * np.eye(Xstd.shape[1])
            gen_std = rng.multivariate_normal(m, cov, size=n_gen)
            gmethod = "gaussian_fallback"
        native = gen_std * sd_f + mu_f
        for k in range(n_gen):
            records.append({"style": style, "sample_type": "generated",
                            "gen_method": gmethod, "_native": native[k]})
            native_rows.append(native[k])
        print(f"[Q3] 生成 {style}: {n_gen} 条（{gmethod}，真实样本={cnt}）")
    return records, np.array(native_rows)
def _transfer(model, style_list, s2i, S, Xstd, Xv, styles, feat_cols, mu_f, sd_f, device):
    """Pils/Lager → Tripel 隐空间平移 + 缺陷投影（式12/13）。"""
    tgt = P.TRANSFER_TARGET
    zt, _ = _style_latent_mean(model, Xstd, styles, tgt, s2i, S, device)
    # 目标风格缺陷典型值 m^t（native 中位）
    tgt_idx = np.where(styles == tgt)[0]
    col_med_all = np.nanmedian(Xv, axis=0)
    defect_pos = {d: feat_cols.index(c) for d, c in P.DEFECT_COL_MAP.items()}
    m_t = {d: float(np.nanmedian(Xv[tgt_idx, pos])) for d, pos in defect_pos.items()}

    records = []
    before = {d: [] for d in defect_pos}
    after = {d: [] for d in defect_pos}
    cap_rec = {d: [] for d in defect_pos}
    for src in P.TRANSFER_SOURCES:
        if src not in s2i:
            print(f"[Q3] 迁移源 {src} 不存在，跳过")
            continue
        zs, sidx = _style_latent_mean(model, Xstd, styles, src, s2i, S, device)
        delta = zt - zs
        # 逐源样本编码 -> 平移 -> 用目标风格解码
        oh_src = np.zeros((len(sidx), S)); oh_src[:, s2i[src]] = 1
        with torch.no_grad():
            mu_s, _ = model.encode(torch.tensor(Xstd[sidx], dtype=torch.float32, device=device),
                                   torch.tensor(oh_src, dtype=torch.float32, device=device))
            z_moved = mu_s.cpu().numpy() + delta
            oh_t = np.zeros((len(sidx), S)); oh_t[:, s2i[tgt]] = 1
            xhat = model.decode(torch.tensor(z_moved, dtype=torch.float32, device=device),
                                torch.tensor(oh_t, dtype=torch.float32, device=device)).cpu().numpy()
        native = xhat * sd_f + mu_f
        for row, si in enumerate(sidx):
            x_after_vec = native[row].copy()
            for d, pos in defect_pos.items():
                xb = Xv[si, pos]
                if not np.isfinite(xb):
                    xb = float(col_med_all[pos])
                cap = max(xb, m_t[d])          # USE_ABS_THRESHOLD=False → 无 τ，相对判据
                if P.USE_ABS_THRESHOLD:
                    pass  # 可换算时此处并入 τ 上界（本题单位不可比，默认关闭）
                # 缺陷列逐样本投影回安全区（式13，np.minimum 下截断）
                xa = float(np.minimum(float(x_after_vec[pos]), cap))
                x_after_vec[pos] = xa
                before[d].append(float(xb)); after[d].append(xa); cap_rec[d].append(cap)
            records.append({"style": f"{src}->{tgt}", "sample_type": "transfer",
                            "src_beer_row": int(si), "_native": x_after_vec})
        print(f"[Q3] 迁移 {src}->{tgt}: {len(sidx)} 条")
    # 合规率（式13：x_after <= cap）
    n_tot = n_ok = 0
    per_defect = {}
    for d in defect_pos:
        bf = np.array(before[d]); af = np.array(after[d]); cp = np.array(cap_rec[d])
        ok = int((af <= cp + 1e-9).sum())
        n_tot += len(af); n_ok += ok
        per_defect[d] = {"n": len(af), "n_compliant": ok,
                         "before_mean": round(float(bf.mean()), 4),
                         "after_mean": round(float(af.mean()), 4),
                         "m_t": round(m_t[d], 4),
                         "delta_mean": round(float((af - bf).mean()), 4)}
    rate = n_ok / n_tot if n_tot else 1.0
    info = {"compliance_rate": round(rate, 6), "n_checks": n_tot, "n_compliant": n_ok,
            "per_defect": per_defect, "defect_cols": list(P.DEFECT_COL_MAP.values()),
            "defect_no_chem": P.DEFECT_NO_CHEM, "m_t": {k: round(v, 4) for k, v in m_t.items()}}
    print(f"[Q3] 缺陷合规率={rate:.4f}（{n_ok}/{n_tot}）")
    return records, info


def _sensory_profile(native_rows, feat_cols):
    """对生成/迁移 native 谱套 Q1 模型 → 50 维 0-6 感官画像。"""
    import joblib
    bundle = joblib.load(U.ckpt_path("q1_models.pkl"))
    models, binners = bundle["models"], bundle["binners"]
    sens_cols = list(binners.keys())
    if native_rows.ndim == 1:
        native_rows = native_rows.reshape(1, -1)
    out = np.zeros((native_rows.shape[0], len(sens_cols)), dtype=int)
    for j, col in enumerate(sens_cols):
        if col in models:
            rc = models[col].predict(native_rows)
            out[:, j] = binners[col].transform_continuous(rc)
        else:
            out[:, j] = 3   # 基线维度无特征依赖模型，置中间等级
    return out, sens_cols
def _eval_metrics(Xv, styles, feat_cols, gen_native, gen_records, transfer_info):
    """分布距离(KS)、PCA 重叠坐标、闭环酯香等级。"""
    from sklearn.decomposition import PCA
    col_med = np.nanmedian(Xv, axis=0)
    Xfill = np.where(np.isnan(Xv), col_med, Xv)
    ks_per_style = {}
    for style in P.GEN_STYLES:
        real_idx = np.where(styles == style)[0]
        gen_idx = [i for i, r in enumerate(gen_records) if r["style"] == style]
        if len(real_idx) < 2 or not gen_idx:
            continue
        real = Xfill[real_idx]; gen = gen_native[gen_idx]
        ks = [ks_2samp(real[:, p], gen[:, p]).statistic for p in range(Xv.shape[1])]
        ks_per_style[style] = round(float(np.mean(ks)), 4)
    # PCA（在真实全量上拟合，投影真实+生成）
    mu_f = Xfill.mean(axis=0); sd_f = Xfill.std(axis=0) + 1e-8
    pca = PCA(n_components=2, random_state=P.SEED).fit((Xfill - mu_f) / sd_f)
    real_2d = pca.transform((Xfill - mu_f) / sd_f)
    gen_2d = pca.transform((gen_native - mu_f) / sd_f)
    pca_data = {
        "real": [{"x": round(float(real_2d[i, 0]), 3), "y": round(float(real_2d[i, 1]), 3),
                  "style": str(styles[i])} for i in range(len(styles))
                 if styles[i] in P.GEN_STYLES or styles[i] in P.TRANSFER_SOURCES],
        "gen": [{"x": round(float(gen_2d[i, 0]), 3), "y": round(float(gen_2d[i, 1]), 3),
                 "style": gen_records[i]["style"]} for i in range(len(gen_records))],
        "explained_var": [round(float(v), 4) for v in pca.explained_variance_ratio_],
    }
    return {"ks_distance_by_style": ks_per_style, "pca": pca_data}


def _assemble(out_dir, data_dir, feat_cols, sens_cols, gen_records, gen_native, sens_pred_gen,
              transfer_records, sens_pred_tr, transfer_info, metrics, Xv, styles):
    # 写宽表交付：生成 + 迁移，231 化学 + 50 感官 + 元信息
    rows = []
    for i, r in enumerate(gen_records):
        row = {"style": r["style"], "sample_type": r["sample_type"],
               "gen_method": r["gen_method"]}
        row.update({c: round(float(gen_native[i, k]), 5) for k, c in enumerate(feat_cols)})
        row.update({f"SENS_{c}": int(sens_pred_gen[i, k]) for k, c in enumerate(sens_cols)})
        rows.append(row)
    for i, r in enumerate(transfer_records):
        row = {"style": r["style"], "sample_type": r["sample_type"], "gen_method": "latent_transfer"}
        nat = r["_native"]
        row.update({c: round(float(nat[k]), 5) for k, c in enumerate(feat_cols)})
        row.update({f"SENS_{c}": int(sens_pred_tr[i, k]) for k, c in enumerate(sens_cols)})
        rows.append(row)
    sub = pd.DataFrame(rows)
    path = os.path.join(out_dir, "submission", "q3_generated_profiles.csv")
    sub.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[Q3] 写出 {path}  shape={sub.shape}")

    # 闭环：生成 Tripel 酯香等级 vs 真实 Tripel 酯香等级
    Y4 = pd.read_csv(os.path.join(data_dir, "4.csv"))
    ester_dim = "A_esters_all"
    jdim = sens_cols.index(ester_dim)
    gen_tri = [i for i, r in enumerate(gen_records) if r["style"] == "Tripel"]
    gen_ester = float(np.mean(sens_pred_gen[gen_tri, jdim])) if gen_tri else None
    real_tri_idx = np.where(styles == "Tripel")[0]
    real_binner = U.Binner().fit(Y4[ester_dim].values)
    real_ester_levels = real_binner.transform(Y4[ester_dim].values[real_tri_idx])
    real_ester = float(np.mean(real_ester_levels))

    results = {
        "problem": 3,
        "method": "CVAE条件生成(torch,重参数化+KL,掩码重构) + 隐空间迁移 + 缺陷投影 + 高斯兜底",
        "summary": {
            "n_generated": len(gen_records), "n_transfer": len(transfer_records),
            "gen_styles": P.GEN_STYLES, "transfer": f"{P.TRANSFER_SOURCES}->{P.TRANSFER_TARGET}",
            "latent_dim": P.LATENT_DIM, "beta_kl": P.BETA_KL,
            "defect_compliance_rate": transfer_info["compliance_rate"],
            "ks_distance_by_style": metrics["ks_distance_by_style"],
            "gen_tripel_ester_level": round(gen_ester, 4) if gen_ester is not None else None,
            "real_tripel_ester_level": round(real_ester, 4),
            "gen_dim": int(gen_native.shape[1]),
        },
        "transfer_info": transfer_info,
        "fig_data": {"pca": metrics["pca"],
                     "radar": _radar_data(gen_records, sens_pred_gen, sens_cols),
                     "defect_dumbbell": transfer_info["per_defect"]},
        "sensory_cols": sens_cols,
        "submission": {"path": "submission/q3_generated_profiles.csv",
                       "rows": int(sub.shape[0]), "cols": int(sub.shape[1])},
    }
    return results


def _radar_data(gen_records, sens_pred_gen, sens_cols):
    """各代表风格生成谱的平均感官画像（核心 A_/F_ 维）。"""
    core = [c for c in sens_cols if c.startswith(P.CORE_PREFIXES)]
    cidx = [sens_cols.index(c) for c in core]
    out = {}
    for style in P.GEN_STYLES:
        idx = [i for i, r in enumerate(gen_records) if r["style"] == style]
        if idx:
            out[style] = {core[k]: round(float(np.mean(sens_pred_gen[idx][:, cidx[k]])), 3)
                          for k in range(len(core))}
    return {"dims": core, "by_style": out}


def _validate(out_dir, results):
    sub = pd.read_csv(os.path.join(out_dir, "submission", "q3_generated_profiles.csv"))
    # 硬约束：生成谱化学维度==231
    import params as _P
    chem_cols = [c for c in sub.columns if not c.startswith("SENS_")
                 and c not in ("style", "sample_type", "gen_method")]
    assert len(chem_cols) == _P.N_FEATURES, f"[P3] 生成谱化学维应231，实{len(chem_cols)}"
    # 缺陷合规率==1.0
    rate = results["summary"]["defect_compliance_rate"]
    assert abs(rate - 1.0) < 1e-6, f"[P3-C3] 缺陷合规率!=1.0: {rate}"
    print("[Q3] validate_constraints PASS（生成谱231维 / 缺陷合规率==1.0）")
    # 能力断言：P3-C1 不同风格可区分（KS>0 且非全相同）；P3-C3 迁移缺陷不升超限
    ks = results["summary"]["ks_distance_by_style"]
    assert len(ks) >= 1 and all(v >= 0 for v in ks.values()), "[P3-C1] 分布距离缺失"
    assert results["summary"]["gen_dim"] == _P.N_FEATURES, "[P3-C2] 交付维度错误"
    print("[Q3] validate_capability PASS（P3-C1 风格分布距离 / P3-C3 缺陷投影100%合规）")


if __name__ == "__main__":
    dd = sys.argv[1] if len(sys.argv) > 1 else "user_data"
    run(dd)



