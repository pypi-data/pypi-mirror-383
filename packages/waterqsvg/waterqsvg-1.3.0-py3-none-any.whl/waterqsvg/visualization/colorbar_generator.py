#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立Colorbar图片生成模块

功能：
1. 生成定量模式colorbar（显示具体数值刻度）
2. 生成定性模式colorbar（显示"低"和"高"标签）
3. 支持透明背景PNG格式输出
4. 不包含指标名称/单位等额外文字

移植自AutoReportV3的maps.py，专门用于WaterQSVG独立colorbar生成
"""

import logging
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase

logger = logging.getLogger(__name__)


def create_colorbar_image(
    colormap: str,
    value_range: Tuple[float, float],
    visualization_mode: str,
    unit: str = "",
    save_path: str = None,
    figsize: Tuple[float, float] = (1.5, 6),
    dpi: int = 150,
    transparent_bg: bool = True,
) -> bool:
    """
    生成独立的colorbar图片（定量或定性模式）

    Args:
        colormap: 颜色映射方案 (jet, viridis, water_quality, RdYlBu_r等)
        value_range: 数值范围 (vmin, vmax)
        visualization_mode: "quantitative" 或 "qualitative"
        unit: 单位（仅供日志记录，不显示在图片上）
        save_path: 保存路径
        figsize: 图片尺寸（宽, 高）英寸
        dpi: 分辨率
        transparent_bg: 是否使用透明背景

    Returns:
        bool: 是否成功生成
    """
    try:
        vmin, vmax = value_range

        # 处理所有值相同的特殊情况（参考maps.py第1534-1549行）
        if vmin == vmax:
            logger.warning(f"数值范围相同 ({vmin})，扩展10%范围以生成有效colorbar")
            if vmin == 0:
                display_range = (0, 1)
            else:
                delta = abs(vmin) * 0.1
                display_range = (vmin - delta, vmax + delta)
        else:
            display_range = (vmin, vmax)

        # 创建figure和axis
        fig, ax = plt.subplots(figsize=figsize)

        # 设置透明背景
        if transparent_bg:
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)

        # 创建Normalize对象
        norm = Normalize(vmin=display_range[0], vmax=display_range[1])

        # 创建ColorbarBase（独立的colorbar，不依赖于主图）
        cb = ColorbarBase(
            ax,
            cmap=colormap,
            norm=norm,
            orientation="vertical",
        )

        # 根据模式设置刻度和标签
        if visualization_mode == "qualitative":
            # 定性模式：只显示"低"和"高"
            cb.set_ticks([display_range[0], display_range[1]])
            cb.set_ticklabels(["低", "高"])
            logger.info(f"生成定性colorbar: 低({display_range[0]:.3f}) - 高({display_range[1]:.3f})")
        else:
            # 定量模式：显示数值刻度（自动格式化）
            # matplotlib会自动选择合适的刻度位置，我们可以自定义格式
            ticks = _calculate_optimal_ticks(display_range[0], display_range[1])
            cb.set_ticks(ticks)

            # 格式化刻度标签
            tick_labels = [_format_tick_label(tick) for tick in ticks]
            cb.set_ticklabels(tick_labels)
            logger.info(
                f"生成定量colorbar: 范围 [{display_range[0]:.3f}, {display_range[1]:.3f}], "
                f"刻度数: {len(ticks)}"
            )

        # 设置刻度标签字体大小
        cb.ax.tick_params(labelsize=32)

        # 设置中文字体
        plt.rcParams["font.family"] = "SimHei"
        plt.rcParams["axes.unicode_minus"] = False

        # 紧凑布局
        plt.subplots_adjust(left=0.2, right=0.8, top=0.98, bottom=0.02)

        # 保存图片
        save_kwargs = {
            "dpi": dpi,
            "bbox_inches": "tight",
            "pad_inches": 0.05,
        }

        if transparent_bg:
            save_kwargs["transparent"] = True
            save_kwargs["facecolor"] = "none"
        else:
            save_kwargs["facecolor"] = "white"

        plt.savefig(save_path, **save_kwargs)

        logger.info(f"Colorbar图片已保存至: {save_path}")

        # 清理
        plt.clf()
        plt.cla()
        plt.close()

        return True

    except Exception as e:
        logger.error(f"生成colorbar图片失败: {str(e)}")
        return False


def _calculate_optimal_ticks(vmin: float, vmax: float, max_ticks: int = 6) -> list:
    """
    计算最优刻度位置

    Args:
        vmin: 最小值
        vmax: 最大值
        max_ticks: 最大刻度数

    Returns:
        list: 刻度位置列表
    """
    value_range = vmax - vmin

    # 根据数值范围选择合适的刻度数量
    if value_range < 1:
        # 小范围：使用更多刻度
        n_ticks = 5
    elif value_range < 10:
        n_ticks = 5
    elif value_range < 100:
        n_ticks = 5
    else:
        n_ticks = 4

    n_ticks = min(n_ticks, max_ticks)

    # 生成均匀分布的刻度
    ticks = np.linspace(vmin, vmax, n_ticks)

    return ticks.tolist()


def _format_tick_label(value: float) -> str:
    """
    格式化刻度标签

    规则：
    - 0.01 ≤ |value| < 1.0: 保留2位小数
    - 1.0 ≤ |value| < 100: 保留1位小数
    - |value| ≥ 100: 保留0位小数
    - 对于非常小的数使用科学计数法

    Args:
        value: 数值

    Returns:
        str: 格式化后的字符串
    """
    abs_value = abs(value)

    if abs_value == 0:
        return "0"
    elif abs_value < 0.01:
        # 科学计数法
        return f"{value:.1e}"
    elif abs_value < 1.0:
        # 2位小数
        return f"{value:.2f}"
    elif abs_value < 100:
        # 1位小数
        return f"{value:.1f}"
    else:
        # 整数
        return f"{value:.0f}"
