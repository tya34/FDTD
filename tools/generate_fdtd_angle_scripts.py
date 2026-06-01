from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
STRUCTURES = ["Arch", "Ring", "Tube", "Helix", "Taper"]
LONGITUDES = range(0, 181, 30)
LATITUDES = range(-60, 61, 30)


def fmt_num(x):
    if abs(x) < 5e-12:
        x = 0.0
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


def lat_tag(lat):
    return f"latp{abs(lat):02d}" if lat >= 0 else f"latm{abs(lat):02d}"


def split_base(text):
    source_start = text.index("addplane;")
    blank_before_comment = text.rfind("\n\n", 0, source_start)
    if blank_before_comment != -1:
        source_start = blank_before_comment + 2
    stop = text.index('set("wavelength stop",lambda0);', source_start)
    line_end = text.index("\n", stop)
    return text[:source_start], text[line_end + 1:]


def source_position(source_lon_deg, source_lat_deg):
    lon = math.radians(source_lon_deg)
    lat = math.radians(source_lat_deg)
    clat = math.cos(lat)
    return (-clat * math.cos(lon), math.sin(lat), clat * math.sin(lon))


def source_angles_from_k(kx, ky, kz):
    comps = {"x": abs(kx), "y": abs(ky), "z": abs(kz)}
    axis = max(("x", "y", "z"), key=lambda a: (comps[a], {"x": 2, "y": 1, "z": 0}[a]))
    if axis == "z":
        forward = kz >= 0
        base = kz if forward else -kz
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(ky, kx) if forward else math.atan2(-ky, -kx))
    elif axis == "y":
        forward = ky >= 0
        base = ky if forward else -ky
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(kx, kz) if forward else math.atan2(-kx, -kz))
    else:
        forward = kx >= 0
        base = kx if forward else -kx
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(kz, ky) if forward else math.atan2(-kz, -ky))
    if abs(theta) < 5e-12:
        theta = 0.0
    if abs(phi) < 5e-12:
        phi = 0.0
    return axis, "forward" if forward else "backward", theta, phi


def source_position_lines(axis, direction):
    if axis == "x":
        x_expr = "fdtd_xmin + 0.5*source_top_gap" if direction == "forward" else "fdtd_xmax - 0.5*source_top_gap"
        return [f'set("x",{x_expr});', 'set("y",fdtd_yc);', 'set("y span",fdtd_ys);', 'set("z",fdtd_zc);', 'set("z span",fdtd_zs);']
    if axis == "y":
        y_expr = "fdtd_ymin + 0.5*source_top_gap" if direction == "forward" else "fdtd_ymax - 0.5*source_top_gap"
        return ['set("x",fdtd_xc);', 'set("x span",fdtd_xs);', f'set("y",{y_expr});', 'set("z",fdtd_zc);', 'set("z span",fdtd_zs);']
    z_expr = "fdtd_zmin + 0.5*source_top_gap" if direction == "forward" else "fdtd_zmax - 0.5*source_top_gap"
    return ['set("x",fdtd_xc);', 'set("x span",fdtd_xs);', 'set("y",fdtd_yc);', 'set("y span",fdtd_ys);', f'set("z",{z_expr});']


def build_source_block(source_lon_deg, source_lat_deg):
    sx, sy, sz = source_position(source_lon_deg, source_lat_deg)
    kx, ky, kz = -sx, -sy, -sz
    axis, direction, fdtd_theta, fdtd_phi = source_angles_from_k(kx, ky, kz)
    name = f"src_lon{source_lon_deg:03d}_{lat_tag(source_lat_deg)}"
    lines = [
        f"# User source coordinates: source_lon_deg = {source_lon_deg} deg, source_lat_deg = {source_lat_deg} deg.",
        "# Earth-like source hemisphere: longitude runs from -x through +z to +x; latitude runs from -y to +y.",
        f"# Source-position unit vector: src_pos_x = {fmt_num(sx)}, src_pos_y = {fmt_num(sy)}, src_pos_z = {fmt_num(sz)}.",
        "# Target propagation unit vector from the source position back toward the structure center:",
        f"# kx = {fmt_num(kx)}, ky = {fmt_num(ky)}, kz = {fmt_num(kz)}.",
        "# User longitude/latitude are source-position coordinates; FDTD angle theta/phi below are Lumerical source angles.",
        "# The injection axis is selected from the largest |k| component to avoid grazing source injection.",
        f"source_lon_deg = {source_lon_deg};",
        f"source_lat_deg = {source_lat_deg};",
        f"src_pos_x = {fmt_num(sx)};",
        f"src_pos_y = {fmt_num(sy)};",
        f"src_pos_z = {fmt_num(sz)};",
        f"target_kx = {fmt_num(kx)};",
        f"target_ky = {fmt_num(ky)};",
        f"target_kz = {fmt_num(kz)};",
        f"fdtd_angle_theta_deg = {fmt_num(fdtd_theta)};",
        f"fdtd_angle_phi_deg = {fmt_num(fdtd_phi)};",
        "",
        "addplane;",
        f'set("name","{name}");',
        'set("plane wave type","BFAST");',
        f'set("injection axis","{axis}");',
        f'set("direction","{direction}");',
        'set("angle theta",fdtd_angle_theta_deg);',
        'set("angle phi",fdtd_angle_phi_deg);',
        'set("polarization angle",90);',
    ]
    lines.extend(source_position_lines(axis, direction))
    lines.extend(['set("wavelength start",lambda0);', 'set("wavelength stop",lambda0);', ""])
    return "\n".join(lines)


def main():
    count = 0
    for structure in STRUCTURES:
        prefix, suffix = split_base((ROOT / f"{structure}_FDTD.txt").read_text(encoding="utf-8"))
        out_dir = ROOT / structure
        out_dir.mkdir(exist_ok=True)
        for old in out_dir.glob(f"{structure}_lon*_lat*_FDTD.txt"):
            old.unlink()
        for lon in LONGITUDES:
            for lat in LATITUDES:
                out = out_dir / f"{structure}_lon{lon:03d}_{lat_tag(lat)}_FDTD.txt"
                out.write_text(prefix + build_source_block(lon, lat) + suffix, encoding="utf-8")
                count += 1
    print(f"Generated {count} scripts")


if __name__ == "__main__":
    main()
