# Zhang 2024 自卷曲结构 FDTD 建模纪要

## 目标

复现 Zhang 等 2024 年文章中用于光电测试的非平面自卷曲结构。当前已完成并统一维护四类结构：Ring、Tube、Arch 和 Helix。

## 统一设置

- 材料：VO2 薄膜，SiO2 衬底。
- VO2 薄膜厚度：200 nm。
- 光源：沿 `-z` 方向入射的 BFAST 平面波，`polarization angle = 90 deg`。
- FDTD：紧凑区域，`mesh accuracy = 3`，各边界使用 PML。
- XY monitor：不再放在结构上方或衬底中；统一改为两个穿过结构的水平截面：
  - `xy_lower_through_*`
  - `xy_upper_through_*`
- 竖直截面 monitor：保留 `yz_center`、`yz_side`、`xz_center`，其 z span 覆盖结构和部分衬底区域。

## 经纬度入射角定义

- 角度定义采用半球表面到结构中心的入射方向。半球沿 `+z` 方向突出，半球圆底面位于 `xy` 平面。
- 经度记为 `phi`，范围为 `0 deg` 到 `180 deg`；纬度记为 `theta`，范围为 `-90 deg` 到 `90 deg`。
- 典型方向：
  - `theta = 0 deg, phi = 90 deg`：沿 `-z` 方向正入射。
  - `theta = +90 deg`：沿 `-y` 方向入射。
  - `theta = -90 deg`：沿 `+y` 方向入射。
- 正纬度表示光源位于 `+theta` 一侧；FDTD 红色箭头表示的是光从该位置射向结构中心的传播方向，因此传播矢量与光源位置径向矢量相反。
- 从用户经纬度换算到 FDTD 中红色箭头表示的传播方向单位矢量：

```text
kx = -cos(theta) * cos(phi)
ky = -sin(theta)
kz = -cos(theta) * sin(phi)
```

- 批量角度脚本中，先根据上述公式计算 `target_kx`、`target_ky`、`target_kz`，再选择绝对值最大的分量作为 `injection axis`，以避免接近擦边的源注入。
- Lumerical `angle theta` 是相对所选 `injection axis` 的夹角，`angle phi` 是绕所选 `injection axis` 的方位角；它们不是用户半球坐标里的 `theta`、`phi`。
- 当前为 Ring、Tube、Arch、Helix 各生成了 `35` 个角度脚本：经度 `0:30:180 deg`，纬度 `-60:30:60 deg`。生成脚本保存在对应结构文件夹内，结构参数保持不变，只改变平面波源设置。

## Ring

- 文件：`Ring_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive。
- 中心半径：`ring_R = 100 um`。
- 薄膜厚度：通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：`pattern_W = 30 um`，通过 `z span` 设置。
- 中心位置：`x = 0`，`y = 0`，`z = 0`。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆环最低点接触衬底。
- XY monitors：`xy_lower_through_ring` 和 `xy_upper_through_ring`，均穿过环结构。

## Tube

- 文件：`Tube_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive 作为卷曲圆筒。
- 中心半径：`tube_R = 50 um`。
- 薄膜厚度：通过 `inner_R = tube_R - film_t/2` 和 `outer_R = tube_R + film_t/2` 设置。
- 轴向宽度：`pattern_W = 250 um`，通过 `z span` 设置。
- 中心位置：`x = 0`，`y = 0`，`z = 0`。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆筒最低点接触衬底。
- XY monitors：`xy_lower_through_tube` 和 `xy_upper_through_tube`，均穿过 tube 结构。

## Arch

- 文件：`Arch_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚曲面。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 150 um`。
- 固定边：`y = 0` 的整条短边固定在 SiO2 衬底上，衬底顶面为 `z = 0`。
- 高度：沿 L 方向逐渐升高，任意固定 L 截面沿 W 方向为抛物线，中间低、两侧高。
- `L = 150 um` 端部：中心最低点约 `z = 10 um`，两侧最高点约 `z = 20 um`。
- 中心曲面：`z = (y/pattern_L) * (10 um + 10 um*(x/(pattern_W/2))^2)`。
- 通过曲面法向正负偏移形成 200 nm 等厚实体，并整体平移使薄膜最低点接触衬底顶面。
- XY monitors：`xy_lower_through_arch` 和 `xy_upper_through_arch`，均穿过 arch 结构。

## Helix

- 文件：`Helix_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚斜折/卷曲曲面。
- 卷曲前尺寸：`pattern_W = 50 um`，`pattern_L = 150 um`。
- 几何理解：卷曲前矩形沿约 45 deg 斜向折痕发生卷曲式折叠；折叠后的自由短边相对原长边外伸约 `20 um`，并在 XY 投影中转为与原短边垂直。
- 折痕位置：近似为 `y = x + fold_c`，其中 `fold_c = pattern_L - half_W - edge_overhang`。
- 折痕区：使用有限宽度 `curl_width` 的平滑过渡，不再使用硬折线。
- 高度场：
  - 固定端从衬底开始。
  - 从固定端到折痕区开始，逐渐抬升。
  - 折痕变化区高度单调继续上升，不采用“中间最高后下降”的峰形函数。
  - 折痕区结束到自由端以较小斜率继续轻微上翘。
- 关键可调参数：`curl_width`、`pre_lift_slope`、`fold_extra_lift`、`fold_start_tangent`、`fold_end_tangent`、`post_lift_slope`。
- 已加入紧凑 FDTD 区域、`-z` 入射光源和 profile monitors。
- XY monitors：`xy_lower_through_helix` 和 `xy_upper_through_helix`，均穿过 helix 结构。

## 当前状态

- `Ring_FDTD.txt`、`Tube_FDTD.txt`、`Arch_FDTD.txt` 和 `Helix_FDTD.txt` 均包含结构、衬底、紧凑 FDTD 区域、`-z` 入射光源和 profile monitors。
- 四个模型的 XY monitors 已统一为上下两个穿过结构的截面。
- Taper 结构尚未建模。
