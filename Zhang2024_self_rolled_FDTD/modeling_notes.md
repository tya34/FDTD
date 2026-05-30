# Zhang 2024 自卷曲结构 FDTD 建模纪要

## 目标

复现 Zhang 等 2024 年文章中光电测试用的非 planar 自卷曲结构。当前阶段先确认并上传已经通过几何检查的结构：ring、tube 和 arch。

## 已确认参数

- 材料：VO2 薄膜，SiO2 基底。
- VO2 薄膜厚度：200 nm。
- Ring 和 Tube 脚本只保留几何和基底；Arch 已按最新要求加入紧凑 FDTD 区域、光源和 monitor。
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

## Arch

- 文件：`Arch_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚曲面。
- 平面尺寸：`pattern_W = 30 um`，`pattern_L = 150 um`。
- L 方向：`y = 0` 的整条边固定在 SiO2 基底上，基底顶面设为 `z = 0`。
- 翘起高度沿 L 方向近似线性增大。
- 任意固定 L 截面沿 W 方向为抛物线：中间低，两边高。
- `L = 150 um` 端部：中心最低点 `z = 10 um`，两侧最高点 `z = 20 um`。
- 解析中心曲面：`z = (y/pattern_L) * (10 um + 10 um*(x/(pattern_W/2))^2)`。
- 薄膜厚度仍为 `200 nm`，通过曲面法向正负偏移形成等厚实体；随后整体平移使薄膜最低点接触基底顶面。
- 当前已加入紧凑 FDTD 区域、向 `-z` 方向入射的平面波光源（偏振角 `90 deg`）和多个 profile monitor；monitor 均位于光源下方，并包含一部分衬底区域。

## 迭代记录

1. 初始尝试使用 `addplanarsolid` 手写等厚曲面，但 ring 和 tube 形态过于复杂且不必要。
2. 讨论后确认 ring 和 tube 可以直接使用 Lumerical Structure 中的 ring primitive。
3. 将 ring 半径固定为 100 um，tube 半径固定为 50 um。
4. 根据要求将 ring/tube 的中心位置放到坐标原点，随后根据外半径调整衬底高度。

## 待继续结构

Helix、Taper 仍需继续按文章 SEM 形态进一步校准；当前已按明确参数完成 Ring、Tube 和 Arch。
