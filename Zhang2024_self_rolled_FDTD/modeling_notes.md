# Zhang 2024 自卷曲结构 FDTD 建模纪要

## 目标

复现 Zhang 等 2024 年文章中光电测试用的非 planar 自卷曲结构。当前阶段先确认并上传已经通过几何检查的两个结构：ring 和 tube。

## 已确认参数

- 材料：VO2 薄膜，SiO2 基底。
- VO2 薄膜厚度：200 nm。
- 当前脚本只保留几何和基底；已去掉 FDTD 仿真区域、光源和 monitor。
- Ring 和 Tube 改用 Lumerical 内置 `addring` primitive，不再手写 `addplanarsolid` 网格。

## Ring

- 文件：`Ring_FDTD.txt`
- 结构：直接使用 `addring` 建模。
- 半径：中心半径 `ring_R = 100 um`。
- 薄膜厚度通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：`pattern_W = 30 um`，通过 `z span` 设置。
- 圆环中心位置：`x = 0`，`y = 0`，`z = 0`。
- SiO2 基底顶面：`substrate_top_z = -outer_R`，使圆环最低点正好接触基底。

## Tube

- 文件：`Tube_FDTD.txt`
- 结构：直接使用 `addring` 建模为圆筒。
- 半径：中心半径 `tube_R = 50 um`。
- 薄膜厚度通过 `inner_R = tube_R - film_t/2` 和 `outer_R = tube_R + film_t/2` 设置。
- 轴向宽度：`pattern_W = 250 um`，通过 `z span` 设置。
- 圆筒中心位置：`x = 0`，`y = 0`，`z = 0`。
- SiO2 基底顶面：`substrate_top_z = -outer_R`，使圆筒最低点正好接触基底。

## 迭代记录

1. 初始尝试使用 `addplanarsolid` 手写等厚曲面，但 ring 和 tube 形态过于复杂且不必要。
2. 讨论后确认 ring 和 tube 可以直接使用 Lumerical Structure 中的 ring primitive。
3. 将 ring 半径固定为 100 um，tube 半径固定为 50 um。
4. 根据要求将 ring/tube 的中心位置放到坐标原点，随后根据外半径调整衬底高度。

## 待继续结构

Arch、Helix、Taper 仍需继续按文章 SEM 形态进一步校准；当前只上传已确认无问题的 Ring 和 Tube。
