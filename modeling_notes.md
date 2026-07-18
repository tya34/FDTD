# Zhang 2024 自卷曲结构 FDTD 建模纪要

## 目标

复现 Zhang 等 2024 年文章中用于光电测试的非平面自卷曲结构。当前已完成并统一维护六类结构：Ring、Tube、Arch、Helix、Taper 和 1V。

## 统一设置

- 材料：VO2 薄膜，SiO2 衬底。
- VO2 薄膜厚度：500 nm。
- 光源：默认使用沿 `-z` 方向入射的 BFAST 平面波，`polarization angle = 90 deg`。
- FDTD：紧凑区域，`mesh accuracy = 1`，各边界使用 PML。
- XY monitor：统一为两个穿过结构的水平截面：
  - `xy_lower_through_*`
  - `xy_upper_through_*`
- 竖直截面 monitor：保留 `yz_center`、`yz_side`、`xz_center`，z span 覆盖结构和部分衬底区域。

## 经纬度入射角定义

- 角度定义采用光源在半球表面上的位置。半球沿 `+z` 方向凸出，半球圆底面位于 `xy` 平面；光从该位置射向结构中心。
- 可按地球经纬度理解：`source_lat_deg = 0 deg` 为赤道，赤道位于 `xz` 平面内；`source_lon_deg` 沿赤道从 `-x` 侧出发，经过 `+z` 顶点投影方向，到达 `+x` 侧。纬度方向沿 `y` 轴变化，负纬度在 `-y` 侧，正纬度在 `+y` 侧。
- 为避免和 Lumerical/FDTD 的 `angle theta`、`angle phi` 混淆，用户经纬度在脚本中统一写为 `source_lon_deg` 和 `source_lat_deg`。
- `source_lon_deg` 范围为 `0 deg` 到 `180 deg`；`source_lat_deg` 范围为 `-90 deg` 到 `90 deg`。
- 当前采用的锚点：
  - `source_lon_deg = 0 deg, source_lat_deg = 0 deg`：光源位于 `-x` 侧，沿 `+x` 方向入射。
  - `source_lon_deg = 90 deg, source_lat_deg = 0 deg`：光源位于 `+z` 侧，沿 `-z` 方向正入射。
  - `source_lon_deg = 180 deg, source_lat_deg = 0 deg`：光源位于 `+x` 侧，沿 `-x` 方向入射。
  - `source_lat_deg = -90 deg`：光源位于 `-y` 侧，沿 `+y` 方向入射。
  - `source_lat_deg = +90 deg`：光源位于 `+y` 侧，沿 `-y` 方向入射。

按上述半球定义，光源位置单位矢量为：

```text
src_pos_x = -cos(source_lat_deg) * cos(source_lon_deg)
src_pos_y =  sin(source_lat_deg)
src_pos_z =  cos(source_lat_deg) * sin(source_lon_deg)
```

FDTD 红色箭头表示光从光源位置射向结构中心的传播方向，因此传播方向单位矢量为：

```text
target_kx = -src_pos_x
target_ky = -src_pos_y
target_kz = -src_pos_z
```

批量角度脚本中，先根据上述公式计算 `src_pos_x`、`src_pos_y`、`src_pos_z` 和 `target_kx`、`target_ky`、`target_kz`，再选择绝对值最大的传播分量作为 `injection axis`，以避免接近擦边的源注入。

## Ring

- 文件：`Ring_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive。
- 卷曲前尺寸：`pattern_W = 30 um`，等效环长约 `300 um`。
- 中心半径：`ring_R = 100 um`。
- 薄膜厚度：通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆环最低点接触衬底。
- XY monitors：`xy_lower` 和 `xy_upper`。

## Tube

- 文件：`Tube_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive 作为卷曲圆筒。
- 卷曲前尺寸：`pattern_W = 250 um`，`pattern_L = 150 um`。
- 中心半径：`tube_R = 50 um`。
- 薄膜厚度：通过 `inner_R = tube_R - film_t/2` 和 `outer_R = tube_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`。
- XY monitors：`xy_lower` 和 `xy_upper`。

## Arch

- 文件：`Arch_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚曲面。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 150 um`。
- 固定边：`y = 0` 的整条短边固定在 SiO2 衬底上，衬底顶面为 `z = 0`。
- 高度：沿 L 方向逐渐升高，任意固定 L 截面沿 W 方向为抛物线，中间低、两侧高。
- `L = 150 um` 端部：中心最低点约 `z = 10 um`，两侧最高点约 `z = 20 um`。
- 中心曲面：`z = (y/pattern_L) * (10 um + 10 um*(x/(pattern_W/2))^2)`。
- 通过曲面法向正负偏移形成 500 nm 等厚实体，并整体平移使薄膜最低点接触衬底顶面。
- XY monitors：`xy_lower` 和 `xy_upper`。

## Helix

- 文件：`Helix_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚斜折/卷曲曲面。
- 卷曲前尺寸：`pattern_W = 50 um`，`pattern_L = 150 um`。
- 几何理解：卷曲前矩形沿约 45 deg 斜向折痕发生卷曲式折叠；折叠后的自由短边相对原长边外伸约 `20 um`，并在 XY 投影中转为与原短边垂直。
- 折痕位置：近似为 `y = x + fold_c`，其中 `fold_c = pattern_L - half_W - edge_overhang`。
- 折痕区：使用有限宽度 `curl_width` 的平滑过渡。
- 关键可调参数：`curl_width`、`pre_lift_slope`、`fold_extra_lift`、`fold_start_tangent`、`fold_end_tangent`、`post_lift_slope`。
- XY monitors：`xy_lower` 和 `xy_upper`。

## Taper

- 文件：`Taper_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚双侧斜折/卷曲曲面，并保留 SiO2 衬底。
- 卷曲前尺寸：`pattern_W = 150 um`，`pattern_L = 150 um`。
- 固定边：`y = 0` 的整条边固定在 SiO2 衬底上，衬底顶面为 `z = 0`。
- 折痕位置：两条对称斜折痕分别从 `(-pattern_W/2, 0)` 和 `(pattern_W/2, 0)` 连到 `(0, pattern_L)`。
- 左右上角三角区域在有限宽度 `curl_width` 的平滑折痕区内向中线卷起，最终在中线附近形成一对靠近的三角卷曲片。
- 关键可调参数：`curl_width`、`side_closure`、`center_lift_slope`、`fold_extra_lift`、`tip_extra_lift`、`transition_round_lift`。
- XY monitors：`xy_lower` 和 `xy_upper`。

## 1V

- 文件：`1V_FDTD.txt`
- 结构：模仿 Ring，使用 Lumerical 内置 `addring` primitive 建立不到一圈的开口圆弧。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 300 um`。
- 卷曲后直径：`ring_D = 110 um`，对应中心半径 `ring_R = 55 um`。
- 圆弧角：由 `arc_angle_deg = pattern_L/ring_R*180/pi_val` 自动计算，当前为约 `312.522434 deg`，接近一圈。
- 薄膜厚度：500 nm，通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆弧最低点接触衬底。
- XY monitors：`xy_lower` 和 `xy_upper`。

## 当前状态

- `Ring_FDTD.txt`、`Tube_FDTD.txt`、`Arch_FDTD.txt`、`Helix_FDTD.txt`、`Taper_FDTD.txt` 和 `1V_FDTD.txt` 均包含结构、衬底、紧凑 FDTD 区域、默认 `-z` 入射光源和 profile monitors。
- Ring、Tube、Arch、Helix、Taper 已各生成 `35` 个角度脚本：经度 `0:30:180 deg`，纬度 `-60:30:60 deg`。
- `1V_FDTD.txt` 当前为基础正入射脚本；`1V/` 文件夹已按 Ring 的批量角度生成逻辑展开 `35` 个角度脚本，经度 `0:30:180 deg`，纬度 `-60:30:60 deg`。
