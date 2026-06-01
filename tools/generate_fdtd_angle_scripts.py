from __future__ import annotations

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRUCTURES = ["Arch", "Ring", "Tube", "Helix"]
LONGITUDES = range(0, 181, 30)
LATITUDES = range(-60, 61, 30)


def fmt(value: float) -> str:
    if abs(value) < 5e-10:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def lat_token(lat: int) -> str:
    if lat < 0:
        return f"m{abs(lat):02d}"
    return f"p{lat:02d}"


def target_k(lat_deg: int, lon_deg: int) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    kx = -math.cos(lat) * math.cos(lon)
    ky = -math.sin(lat)
    kz = -math.cos(lat) * math.sin(lon)
    return kx, ky, kz


def select_source_settings(kx: float, ky: float, kz: float) -> tuple[str, str, float, float]:
    ax, ay, az = abs(kx), abs(ky), abs(kz)
    if az >= ax and az >= ay:
        axis = "z"
        direction = "forward" if kz >= 0 else "backward"
        base = kz if direction == "forward" else -kz
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(ky, kx))
    elif ay >= ax and ay >= az:
        axis = "y"
        direction = "forward" if ky >= 0 else "backward"
        base = ky if direction == "forward" else -ky
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(kx, kz))
    else:
        axis = "x"
        direction = "forward" if kx >= 0 else "backward"
        base = kx if direction == "forward" else -kx
        theta = math.degrees(math.acos(max(-1.0, min(1.0, base))))
        phi = math.degrees(math.atan2(kz, ky))

    if phi > 180:
        phi -= 360
    if phi <= -180:
        phi += 360
    return axis, direction, theta, phi


def source_geometry_block(axis: str, direction: str) -> str:
    if axis == "z":
        return """set(\"x\",fdtd_xc);
set(\"x span\",fdtd_xs);
set(\"y\",fdtd_yc);
set(\"y span\",fdtd_ys);
set(\"z\",source_z);"""
    if axis == "x":
        x_expr = "fdtd_xmin + 0.5*source_top_gap" if direction == "forward" else "fdtd_xmax - 0.5*source_top_gap"
        return f"""set(\"x\",{x_expr});
set(\"y\",fdtd_yc);
set(\"y span\",fdtd_ys);
set(\"z\",fdtd_zc);
set(\"z span\",fdtd_zs);"""
    y_expr = "fdtd_ymin + 0.5*source_top_gap" if direction == "forward" else "fdtd_ymax - 0.5*source_top_gap"
    return f"""set(\"x\",fdtd_xc);
set(\"x span\",fdtd_xs);
set(\"y\",{y_expr});
set(\"z\",fdtd_zc);
set(\"z span\",fdtd_zs);"""


def source_block(structure: str, lon: int, lat: int) -> str:
    kx, ky, kz = target_k(lat, lon)
    axis, direction, fdtd_theta, fdtd_phi = select_source_settings(kx, ky, kz)
    lon_tok = f"{lon:03d}"
    lat_tok = lat_token(lat)
    src_name = f"src_lon{lon_tok}_lat{lat_tok}"
    geom = source_geometry_block(axis, direction)
    return f"""# User spherical direction: longitude phi = {lon} deg, latitude theta = {lat} deg.
# Target propagation unit vector toward the structure center:
# kx = {fmt(kx)}, ky = {fmt(ky)}, kz = {fmt(kz)}.
# The injection axis is selected from the largest |k| component to avoid grazing source injection.
source_longitude_deg = {lon};
source_latitude_deg = {lat};
target_kx = {fmt(kx)};
target_ky = {fmt(ky)};
target_kz = {fmt(kz)};
fdtd_source_theta_deg = {fmt(fdtd_theta)};
fdtd_source_phi_deg = {fmt(fdtd_phi)};

addplane;
set(\"name\",\"{src_name}\");
set(\"plane wave type\",\"BFAST\");
set(\"injection axis\",\"{axis}\");
set(\"direction\",\"{direction}\");
set(\"angle theta\",fdtd_source_theta_deg);
set(\"angle phi\",fdtd_source_phi_deg);
set(\"polarization angle\",90);
{geom}
set(\"wavelength start\",lambda0);
set(\"wavelength stop\",lambda0);"""


def generate_structure(structure: str) -> int:
    template_path = ROOT / f"{structure}_FDTD.txt"
    template = template_path.read_text(encoding="utf-8")
    out_dir = ROOT / structure
    out_dir.mkdir(exist_ok=True)

    count = 0
    for lon in LONGITUDES:
        for lat in LATITUDES:
            lon_tok = f"{lon:03d}"
            lat_tok = lat_token(lat)
            file_name = f"{structure}_lon{lon_tok}_lat{lat_tok}_FDTD.txt"
            text = re.sub(r"# [A-Za-z]+_FDTD\.txt", f"# {file_name}", template, count=1)
            text = re.sub(
                r"addplane;[\s\S]*?set\(\"wavelength stop\",lambda0\);",
                source_block(structure, lon, lat),
                text,
                count=1,
            )
            (out_dir / file_name).write_text(text, encoding="utf-8")
            count += 1
    return count


def main() -> None:
    total = 0
    for structure in STRUCTURES:
        total += generate_structure(structure)
    if total != 140:
        raise RuntimeError(f"Expected 140 generated scripts, got {total}")
    print(f"Generated {total} scripts")


if __name__ == "__main__":
    main()
