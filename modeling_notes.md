# Zhang 2024 自卷曲结构 FDTD 建模纪要

## 目标

复现 Zhang 等 2024 年文章中用于光电测试的非平面自卷曲结构。当前已完成并统一维护八类结构：Ring、Tube、Arch、Helix、Taper、1V、2V 和 3V。

## 统一设置

- 材料：VO2 薄膜，SiO2 衬底。
- VO2 薄膜厚度：500 nm。
- 光源：统一使用 Bloch/Periodic 平面波，`polarization angle = 90 deg`。整体建模脚本默认沿 `-z` 方向正入射；批量角度脚本根据经纬度选择最近的注入面。
- FDTD：所有含 FDTD 区域的脚本统一采用 `fdtd_margin_x = 50 um`、`fdtd_margin_y = 50 um`，`mesh accuracy = 1`；`x min`、`x max`、`y min`、`y max`、`z min`、`z max` 六个边界均为 PML。
- 衬底：统一使用 `SiO2 (Glass) - Palik`。为表示半无限 SiO2 基底，衬底在 `x/y` 四侧均比 FDTD 区域额外延伸 `5 um`；衬底厚度为 `10 um`，而 FDTD 仅进入衬底 `4 um`，因此衬底底面比 `z min` 再向下延伸 `6 um`。
- 每个脚本统一包含五个频域场 monitor：`field_xy_lower`、`field_xy_upper`、`field_yz_center`、`field_yz_side` 和 `field_xz_reference`。

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

## Monitor 与图片代码

- 八个器件文件夹中各有五个后处理文件：`monitor_field_xy_lower.txt`、`monitor_field_xy_upper.txt`、`monitor_field_yz_center.txt`、`monitor_field_yz_side.txt` 和 `monitor_field_xz_reference.txt`。
- 每个文件对应一个同名 monitor。代码通过 `getresult("<monitor name>","E")` 取得电场，计算 `sqrt(abs(Ex)^2 + abs(Ey)^2 + abs(Ez)^2)`，再用 `image` 绘制电场模长 `|E|`。
- XY 截面使用 `x`、`y` 坐标；YZ 截面使用 `y`、`z` 坐标；XZ 截面使用 `x`、`z` 坐标。坐标统一换算为 `um`。
- 所有图片代码沿用根目录 `monitor.txt` 的显示范围，将 colorbar 固定为 `0` 到 `3`。
- 后处理文件应在对应 FDTD 仿真已经运行并且 monitor 数据可用时执行。文件通过 `image` 打开图窗，不会自动写出 PNG 文件。

## Ring

- 文件：`整体建模/Ring_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive。
- 卷曲前尺寸：`pattern_W = 30 um`，等效环长约 `300 um`。
- 中心半径：`ring_R = 100 um`。
- 薄膜厚度：通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆环最低点接触衬底。
- Monitors：五个统一命名的频域场 monitor。

## Tube

- 文件：`整体建模/Tube_FDTD.txt`
- 结构：使用 Lumerical 内置 `addring` primitive 作为卷曲圆筒。
- 卷曲前尺寸：`pattern_W = 250 um`，`pattern_L = 150 um`。
- 中心半径：`tube_R = 50 um`。
- 薄膜厚度：通过 `inner_R = tube_R - film_t/2` 和 `outer_R = tube_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`。
- Monitors：五个统一命名的频域场 monitor。

## Arch

- 文件：`整体建模/Arch_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚曲面。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 150 um`。
- 固定边：`y = 0` 的整条短边固定在 SiO2 衬底上，衬底顶面为 `z = 0`。
- 高度：沿 L 方向逐渐升高，任意固定 L 截面沿 W 方向为抛物线，中间低、两侧高。
- `L = 150 um` 端部：中心最低点约 `z = 10 um`，两侧最高点约 `z = 20 um`。
- 中心曲面：`z = (y/pattern_L) * (10 um + 10 um*(x/(pattern_W/2))^2)`。
- 通过曲面法向正负偏移形成 500 nm 等厚实体，并整体平移使薄膜最低点接触衬底顶面。
- Monitors：五个统一命名的频域场 monitor。

## Helix

- 文件：`整体建模/Helix_FDTD.txt`
- 结构：使用 `addplanarsolid` 手写等厚斜折/卷曲曲面。
- 卷曲前尺寸：`pattern_W = 50 um`，`pattern_L = 150 um`。
- 几何理解：卷曲前矩形沿约 45 deg 斜向折痕发生卷曲式折叠；折叠后的自由短边相对原长边外伸约 `20 um`，并在 XY 投影中转为与原短边垂直。
- 折痕位置：近似为 `y = x + fold_c`，其中 `fold_c = pattern_L - half_W - edge_overhang`。
- 折痕区：使用有限宽度 `curl_width` 的平滑过渡。
- 关键可调参数：`curl_width`、`pre_lift_slope`、`fold_extra_lift`、`fold_start_tangent`、`fold_end_tangent`、`post_lift_slope`。
- Monitors：五个统一命名的频域场 monitor。

## Taper

- 文件：`整体建模/Taper_FDTD.txt`
- 脚本范围：仅生成 VO2 薄膜和 SiO2 衬底，不含 FDTD 区域、光源、monitor 或 `run`。
- 结构：使用 `addplanarsolid` 构造一张连续等厚自卷曲膜，不再使用两条斜折痕或相互独立的三角片。
- 卷曲前尺寸：`pattern_L = 200 um`，`pattern_W = 250 um`，`film_t = 500 nm`。
- 固定边：`y = 0` 的完整 250 um 短边固定在 SiO2 衬底顶面 `z = 0`。
- 卷曲方式：沿 200 um 长度方向，两条长边同时向中线内收并朝 `y = 0` 固定边回卷；自由端两个角点最终在固定边中点正上方精确重合。
- 无自交约束：左右半膜共享中线，但左半始终位于 `x <= 0`、右半始终位于 `x >= 0`；旧版内部权重导致的交叉穿插已移除。
- 锥形前部：中心线先向前拱出再回卷，两条长边以更短的前拱路径完全返回 `y = 0`；自由短边在汇合点下方形成窄小水滴形开口，整体构成连续类圆锥壳。
- 当前 SEM 标定形态：两个自由角点在模型最高位置 `(x,y,z) = (0,45,105) um` 精确汇合，不再强制返回固定边 `y = 0`；自由短边中点位于 `y = 65 um, z = 105 um`，开口半宽仅 `2.5 um`。
- 横向高度约束：除固定边及最终闭合边外，每个材料长度截面均由左右两侧向中线单调升高；`center_ridge_lift = 18 um` 用于形成连续中央高脊，不再出现中间低、两侧高的截面。
- 关键可调参数：`apex_height`、`apex_y`、`free_center_height`、`free_center_y`、`center_ridge_lift`、`center_forward_bulge`、`edge_forward_bulge`、`free_lobe_half_width`。
- `Taper/` 中经度 `0:30:180 deg`、纬度 `-60:30:60 deg` 的全部 `35` 个角度脚本已同步使用上述几何；各文件原有的经纬度、注入轴、平面波和五个 monitor 设置保持不变。

## 1V

- 文件：`整体建模/1V_FDTD.txt`
- 结构：模仿 Ring，使用 Lumerical 内置 `addring` primitive 建立不到一圈的开口圆弧。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 300 um`。
- 卷曲后直径：`ring_D = 110 um`，对应中心半径 `ring_R = 55 um`。
- 圆弧角：由 `arc_angle_deg = pattern_L/ring_R*180/pi_val` 自动计算，当前为约 `312.522434 deg`，接近一圈。
- 薄膜厚度：500 nm，通过 `inner_R = ring_R - film_t/2` 和 `outer_R = ring_R + film_t/2` 设置。
- 轴向宽度：通过 `z span = pattern_W` 设置。
- 衬底顶面：`substrate_top_z = -outer_R`，使圆弧最低点接触衬底。
- Monitors：五个统一命名的频域场 monitor。

## 2V

- 文件：`整体建模/2V_FDTD.txt`
- 结构：综合 Ring/Tube 的圆弧参数化和 Arch/Helix/Taper 的 `addplanarsolid` 等厚曲面方法，建立带连续侧向偏移的开口卷曲薄膜。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 300 um`；VO2 厚度为 `500 nm`。
- 卷曲后直径：默认 `ring_D = 140 um`，对应圆弧角约 `245.55 deg`、开口约 `114.45 deg`，明显大于 1V 的约 `47.48 deg` 开口。
- 左倾方式：使用 `x = x0-z0*tan(axis_tilt_deg)` 让各卷曲截面随高度连续向宽度方向的 `-x` 侧移动，默认 `axis_tilt_deg = 10 deg`；固定短边仍完整贴合衬底，自由端在正视图中明确向左偏移。
- `ring_D` 与 `axis_tilt_deg` 均集中在脚本开头，便于根据显微图继续标定。
- `2V/` 文件夹按统一经纬度规则包含 `35` 个角度脚本。

## 3V

- 文件：`整体建模/3V_FDTD.txt`
- 结构：完全沿用 2V 的 `addplanarsolid` 等厚曲面、衬底、FDTD 区域、光源和监视器设置。
- 卷曲前尺寸：`pattern_W = 30 um`，`pattern_L = 300 um`；VO2 厚度为 `500 nm`。
- 材料：卷曲薄膜改为 `VO2 80`，SiO2 衬底及其余光学参数不变。
- 开口与直径：`opening_angle_deg = 150 deg`，对应材料圆弧角 `210 deg`；由 300 um 展开长度反算 `ring_R = 81.851114 um`、`ring_D = 163.702227 um`。
- 左倾方式：继续使用 `x = x0-z0*tan(axis_tilt_deg)`，并将 `axis_tilt_deg` 改为 `30 deg`。
- `3V/` 文件夹按统一经纬度规则包含 `35` 个角度脚本。

## 2026-09-11 横向余量与半无限衬底统一

- 修改范围：八个器件文件夹中的全部角度脚本，以及 `整体建模/` 中除几何专用 `Taper_FDTD.txt` 外的七个基础 FDTD 脚本，共 `286` 个含 FDTD 区域的脚本。
- 所有上述脚本的 FDTD 区域在 `x`、`y` 两方向均采用 `50 um` 单边余量，不再保留原来的 `5 um` 或 `10 um` 横向余量。
- 所有上述脚本增加统一变量 `substrate_xy_overhang = 5 um`。SiO2 衬底的 `x/y` 覆盖范围由 FDTD 横向范围向外再延伸 `5 um`，确保衬底完整穿过横向 PML 边界，不在仿真域内部产生人为基底侧壁。
- `z` 方向保持 `fdtd_substrate_depth = 4 um`，衬底厚度保持 `10 um`；衬底底面比 FDTD 的 `z min` 深 `6 um`，确保衬底穿过底部 PML。
- `整体建模/Taper_FDTD.txt` 只建立薄膜和衬底，不含 FDTD 区域，因此不纳入 `50 um` FDTD 单边余量统一；`Taper/` 中的 `35` 个完整角度仿真脚本已纳入。
- 此次修改不改变器件几何、材料、经纬度入射角、注入轴、波长、偏振、边界类型或 monitor 设置。

## 当前状态

- `整体建模/` 中除 `Taper_FDTD.txt` 外的七个基础脚本包含结构、SiO2 衬底、统一 `50 um` 横向单边余量的 FDTD 区域、Bloch/Periodic 平面波和五个统一命名的 profile monitor；`Taper_FDTD.txt` 按最新要求仅保留薄膜与衬底模型。
- `Taper/` 的 `35` 个角度脚本均已改用当前 200 um × 250 um × 500 nm 的 SEM 标定类圆锥模型，且所有角度特有的光源参数未改动。
- Tube、Ring、Taper、Helix、Arch、2V 和 3V 文件夹当前各保留 `35` 个角度脚本：经度 `0:30:180 deg`，纬度 `-60:30:60 deg`。
- `1V/` 文件夹当前保留 `34` 个角度脚本；`1V_lon030_latp30_FDTD.txt` 已被删除，其余文件仍使用相同的经纬度命名规则。
- 八个器件文件夹当前各包含五个 monitor 图片代码文件，可用于绘制对应仿真的五个电场截面。
