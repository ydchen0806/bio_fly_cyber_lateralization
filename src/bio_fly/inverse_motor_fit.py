from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


READOUT_FEATURES = [
    "descending_abs_mass",
    "descending_signed_mass",
    "memory_axis_abs_mass",
    "memory_axis_signed_mass",
    "visual_projection_abs_mass",
    "visual_projection_signed_mass",
    "gustatory_abs_mass",
    "gustatory_signed_mass",
    "mechanosensory_abs_mass",
    "mechanosensory_signed_mass",
]

MOTOR_TARGETS = [
    "forward_drive",
    "turning_drive",
    "feeding_drive",
    "grooming_drive",
    "visual_steering_drive",
]


@dataclass(frozen=True)
class InverseMotorFitPaths:
    training_table: Path
    coefficients: Path
    predictions: Path
    cross_validation: Path
    figure: Path
    report: Path
    metadata: Path


def _default_target_table() -> pd.DataFrame:
    """Behavioural motif labels used only when no external calibration table is available.

    These are deliberately low-dimensional, interpretable targets. They are not Eon's
    private motor weights and should be treated as a transparent surrogate interface.
    """

    return pd.DataFrame.from_records(
        [
            {
                "condition": "olfactory_food_memory",
                "forward_drive": 0.85,
                "turning_drive": 0.45,
                "feeding_drive": 0.70,
                "grooming_drive": 0.05,
                "visual_steering_drive": 0.10,
                "label_source": "CS+ food-odour approach motif",
            },
            {
                "condition": "visual_object_tracking",
                "forward_drive": 0.55,
                "turning_drive": 0.85,
                "feeding_drive": 0.05,
                "grooming_drive": 0.05,
                "visual_steering_drive": 0.95,
                "label_source": "moving-object visual taxis motif",
            },
            {
                "condition": "gustatory_feeding",
                "forward_drive": 0.15,
                "turning_drive": 0.10,
                "feeding_drive": 0.95,
                "grooming_drive": 0.15,
                "visual_steering_drive": 0.05,
                "label_source": "sugar/taste contact feeding motif",
            },
            {
                "condition": "mechanosensory_grooming",
                "forward_drive": 0.10,
                "turning_drive": 0.25,
                "feeding_drive": 0.05,
                "grooming_drive": 0.95,
                "visual_steering_drive": 0.05,
                "label_source": "head/antenna contact grooming motif",
            },
        ]
    )


def _zscore(frame: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, pd.Series, pd.Series]:
    values = frame[columns].astype(float)
    mean = values.mean(axis=0)
    std = values.std(axis=0, ddof=0).replace(0, 1.0)
    return ((values - mean) / std).to_numpy(dtype=float), mean, std


def _ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    x_aug = np.column_stack([np.ones(x.shape[0]), x])
    penalty = np.eye(x_aug.shape[1], dtype=float) * alpha
    penalty[0, 0] = 0.0
    return np.linalg.solve(x_aug.T @ x_aug + penalty, x_aug.T @ y)


def _predict(x: np.ndarray, beta: np.ndarray) -> np.ndarray:
    x_aug = np.column_stack([np.ones(x.shape[0]), x])
    return np.clip(x_aug @ beta, 0.0, 1.0)


def _leave_one_out_cv(x: np.ndarray, y: np.ndarray, conditions: list[str], alpha: float) -> pd.DataFrame:
    records = []
    for held_out in range(x.shape[0]):
        mask = np.ones(x.shape[0], dtype=bool)
        mask[held_out] = False
        beta = _ridge_fit(x[mask], y[mask], alpha)
        pred = _predict(x[held_out : held_out + 1], beta)[0]
        for target, actual, predicted in zip(MOTOR_TARGETS, y[held_out], pred):
            records.append(
                {
                    "held_out_condition": conditions[held_out],
                    "target": target,
                    "actual": float(actual),
                    "predicted": float(predicted),
                    "absolute_error": float(abs(predicted - actual)),
                }
            )
    return pd.DataFrame.from_records(records)


def build_training_table(
    connectome_summary_path: Path,
    target_table_path: Path | None = None,
) -> pd.DataFrame:
    readout = pd.read_csv(connectome_summary_path)
    missing_features = [column for column in READOUT_FEATURES if column not in readout.columns]
    if missing_features:
        raise ValueError(f"Connectome summary is missing columns: {missing_features}")

    if target_table_path is not None and target_table_path.exists():
        targets = pd.read_csv(target_table_path)
    else:
        targets = _default_target_table()

    table = readout.merge(targets, on="condition", how="inner")
    if table.empty:
        raise ValueError("No overlapping conditions between connectome readout and motor target table.")
    missing_targets = [column for column in MOTOR_TARGETS if column not in table.columns]
    if missing_targets:
        raise ValueError(f"Motor target table is missing columns: {missing_targets}")
    return table


def fit_inverse_motor_interface(
    connectome_summary_path: Path,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "inverse_motor_fit",
    target_table_path: Path | None = None,
    alpha: float = 0.2,
) -> InverseMotorFitPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    table = build_training_table(connectome_summary_path, target_table_path=target_table_path)
    table_path = output_dir / "inverse_motor_training_table.csv"
    table.to_csv(table_path, index=False)

    x, feature_mean, feature_std = _zscore(table, READOUT_FEATURES)
    y = table[MOTOR_TARGETS].astype(float).to_numpy()
    beta = _ridge_fit(x, y, alpha=alpha)
    predictions = _predict(x, beta)

    coefficient_records = []
    for target_idx, target in enumerate(MOTOR_TARGETS):
        coefficient_records.append(
            {
                "target": target,
                "feature": "intercept",
                "coefficient": float(beta[0, target_idx]),
                "feature_mean": np.nan,
                "feature_std": np.nan,
            }
        )
        for feature_idx, feature in enumerate(READOUT_FEATURES):
            coefficient_records.append(
                {
                    "target": target,
                    "feature": feature,
                    "coefficient": float(beta[feature_idx + 1, target_idx]),
                    "feature_mean": float(feature_mean[feature]),
                    "feature_std": float(feature_std[feature]),
                }
            )
    coefficients = pd.DataFrame.from_records(coefficient_records)
    coef_path = output_dir / "inverse_motor_interface_coefficients.csv"
    coefficients.to_csv(coef_path, index=False)

    prediction_records = []
    for row_idx, condition in enumerate(table["condition"].astype(str)):
        for target_idx, target in enumerate(MOTOR_TARGETS):
            prediction_records.append(
                {
                    "condition": condition,
                    "target": target,
                    "actual": float(y[row_idx, target_idx]),
                    "predicted": float(predictions[row_idx, target_idx]),
                    "residual": float(y[row_idx, target_idx] - predictions[row_idx, target_idx]),
                    "label_source": table.iloc[row_idx].get("label_source", ""),
                }
            )
    prediction_frame = pd.DataFrame.from_records(prediction_records)
    prediction_path = output_dir / "inverse_motor_interface_predictions.csv"
    prediction_frame.to_csv(prediction_path, index=False)

    cv_frame = _leave_one_out_cv(x, y, table["condition"].astype(str).tolist(), alpha=alpha)
    cv_path = output_dir / "inverse_motor_interface_leave_one_out_cv.csv"
    cv_frame.to_csv(cv_path, index=False)

    figure_path = make_inverse_motor_figure(prediction_path, coef_path, output_dir / "figures")
    report_path = write_inverse_motor_report(
        output_dir=output_dir,
        table=table,
        predictions=prediction_frame,
        cv=cv_frame,
        paths={
            "training_table": table_path,
            "coefficients": coef_path,
            "predictions": prediction_path,
            "cross_validation": cv_path,
            "figure": figure_path,
        },
        alpha=alpha,
    )
    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "connectome_summary_path": str(connectome_summary_path),
                "target_table_path": str(target_table_path) if target_table_path else "",
                "alpha": alpha,
                "n_conditions": int(table.shape[0]),
                "features": READOUT_FEATURES,
                "targets": MOTOR_TARGETS,
                "training_table": str(table_path),
                "coefficients": str(coef_path),
                "predictions": str(prediction_path),
                "cross_validation": str(cv_path),
                "figure": str(figure_path),
                "report": str(report_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return InverseMotorFitPaths(
        training_table=table_path,
        coefficients=coef_path,
        predictions=prediction_path,
        cross_validation=cv_path,
        figure=figure_path,
        report=report_path,
        metadata=metadata_path,
    )


def make_inverse_motor_figure(prediction_path: Path, coefficient_path: Path, figure_dir: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_dir.mkdir(parents=True, exist_ok=True)
    predictions = pd.read_csv(prediction_path)
    coefficients = pd.read_csv(coefficient_path)
    coef = coefficients[coefficients["feature"] != "intercept"].copy()
    coef["abs_coefficient"] = coef["coefficient"].abs()
    top_coef = coef.sort_values("abs_coefficient", ascending=False).groupby("target").head(4)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))
    sns.scatterplot(data=predictions, x="actual", y="predicted", hue="target", style="condition", s=85, ax=axes[0])
    axes[0].plot([0, 1], [0, 1], color="black", lw=1, ls="--")
    axes[0].set_xlim(-0.03, 1.03)
    axes[0].set_ylim(-0.03, 1.03)
    axes[0].set_title("Inverse motor interface fit")
    axes[0].set_xlabel("Target motor motif score")
    axes[0].set_ylabel("Predicted score from connectome readout")
    axes[0].legend(fontsize=7, loc="lower right")

    sns.barplot(data=top_coef, x="coefficient", y="target", hue="feature", ax=axes[1])
    axes[1].axvline(0, color="black", lw=1)
    axes[1].set_title("Largest readout-to-motor coefficients")
    axes[1].set_xlabel("Standardized ridge coefficient")
    axes[1].set_ylabel("Motor motif")
    axes[1].legend(fontsize=7, loc="best")
    fig.tight_layout()
    figure_path = figure_dir / "Fig_inverse_motor_interface.png"
    fig.savefig(figure_path, dpi=260)
    plt.close(fig)
    return figure_path


def write_inverse_motor_report(
    output_dir: Path,
    table: pd.DataFrame,
    predictions: pd.DataFrame,
    cv: pd.DataFrame,
    paths: dict[str, Path],
    alpha: float,
) -> Path:
    report_path = output_dir / "INVERSE_MOTOR_INTERFACE_CN.md"
    mae = predictions.groupby("target")["residual"].apply(lambda values: float(np.mean(np.abs(values)))).reset_index(name="training_mae")
    cv_mae = cv.groupby("target")["absolute_error"].mean().reset_index(name="leave_one_out_mae")
    merged_error = mae.merge(cv_mae, on="target", how="outer")

    report_path.write_text(
        f"""# 逆向拟合 DN-to-motor 接口层可行性报告

保存路径：`{report_path}`

## 结论摘要

本轮已经实现一个可运行的“逆向拟合接口层”原型。它用公开连接组传播得到的多模态 readout 特征，拟合到低维行为控制目标：前进、转向、进食、梳理和视觉转向。该层可以作为接近 Eon 闭环系统的替代方案，但必须在论文中称为 `surrogate motor interface`，不能声称是 Eon 私有 DN-to-motor 权重。

当前训练样本数为 `{len(table)}` 个感觉/行为条件，岭回归正则强度 `alpha = {alpha}`。样本量很小，因此它适合做工程闭环和图表演示，不足以单独支撑 Nature 级统计结论。Nature 级证据需要后续加入真实行为轨迹、公开神经元级 DN 标签、更多条件和湿实验验证。

## 输入变量

- `descending_abs_mass`：感觉扰动经连接组传播到 descending neuron 类神经元的总绝对响应量，近似表示脑到身体接口的招募强度。
- `descending_signed_mass`：descending neuron 响应的带符号总和，近似表示净兴奋/抑制方向。
- `memory_axis_abs_mass`：KC、MBON、DAN、APL、DPM 等记忆相关轴的总响应量。
- `memory_axis_signed_mass`：记忆轴带符号响应。
- `visual_projection_abs_mass` / `visual_projection_signed_mass`：视觉投射相关通路响应。
- `gustatory_abs_mass` / `gustatory_signed_mass`：味觉/糖接触相关通路响应。
- `mechanosensory_abs_mass` / `mechanosensory_signed_mass`：机械感觉/接触相关通路响应。

## 输出变量

- `forward_drive`：前进/趋近驱动，数值越高表示越倾向持续行走。
- `turning_drive`：左右转向或轨迹修正驱动，数值越高表示越需要方向控制。
- `feeding_drive`：进食或 proboscis extension proxy 驱动。
- `grooming_drive`：梳理动作驱动。
- `visual_steering_drive`：视觉目标跟踪或视觉诱导转向驱动。

## 误差摘要

{merged_error.to_string(index=False)}

## 训练条件

{table[['condition', 'biological_input', 'expected_behavior', 'label_source']].to_string(index=False)}

## 输出文件

- 训练表：`{paths['training_table']}`
- 接口系数：`{paths['coefficients']}`
- 训练集预测：`{paths['predictions']}`
- 留一法交叉验证：`{paths['cross_validation']}`
- 图：`{paths['figure']}`

## 严谨边界

1. 这里拟合的是公开可审计的替代接口，不是 Eon 内部接口。
2. 默认标签来自行为 motif 约束，而不是真实果蝇逐帧标注，因此只用于工程原型和假说生成。
3. 该接口已经能把 olfactory、visual、gustatory、mechanosensory 四类 readout 映射到不同 motor motif，但样本数只有四个，留一法误差只能作为 sanity check。
4. 下一步应把真实行为数据或更大规模 FlyGym/NeuroMechFly rollout 结果加入 `target_table_path`，再重新拟合并报告独立测试集误差。

## 对论文的用法

可以写：我们实现了一个 connectome-readout-constrained surrogate motor interface，用于把公开连接组传播结果接入 embodied 行为仿真，并通过留一法和消融实验评估接口稳定性。

不能写：我们通过逆向拟合恢复了 Eon 的真实 DN-to-motor 权重。
""",
        encoding="utf-8",
    )
    return report_path

