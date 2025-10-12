#!/usr/bin/env python3
import argparse
import os
import sys
import time
import shutil
from pathlib import Path
from PIL import Image

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
IGNORE_DIR_NAMES = set()  # will add backup dir dynamically later

def human_kb(n):  # bytes -> KB str
    return f"{n/1024:.0f} KB"

def save_webp_fit_size(img: Image.Image, out_path: Path, target_kb=1024, tolerance=0.10,
                       q_min=60, q_max=95, method=6, icc_profile=None):
    """
    Encode to WebP trying to land near target_kb (+/- tolerance).
    Uses binary search on quality.
    """
    # First try with q_max once (fast path)
    def encode(q):
        params = {"format": "WEBP", "quality": int(q), "method": method}
        if icc_profile:
            params["icc_profile"] = icc_profile
        img.save(out_path, **params)
        return out_path.stat().st_size

    # initial attempt
    size = encode(q_max)
    if size <= (target_kb * 1024) * (1 + tolerance):
        return size, q_max

    # binary search between q_min..q_max
    lo, hi = q_min, q_max
    best_size, best_q = size, q_max
    target_bytes = target_kb * 1024
    for _ in range(12):  # enough for convergence
        mid = (lo + hi) // 2
        size = encode(mid)
        if abs(size - target_bytes) < abs(best_size - target_bytes):
            best_size, best_q = size, mid
        if size > target_bytes:  # too big -> lower quality
            hi = mid - 1
        else:
            lo = mid + 1
    # write best (already on disk at last mid; ensure best is saved)
    if best_q != mid:
        encode(best_q)
        best_size = out_path.stat().st_size
    return best_size, best_q

def process_folder(folder: Path, target_kb=1024, max_width=None, recursive=False):
    if not folder.exists() or not folder.is_dir():
        sys.exit(f"Error: {folder} is not a directory.")

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup_dir = folder / f"_backup_originals_{ts}"
    backup_dir.mkdir(exist_ok=True)
    IGNORE_DIR_NAMES.add(backup_dir.name)

    files = []
    if recursive:
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS and backup_dir not in p.parents:
                files.append(p)
    else:
        files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

    if not files:
        print("No images found.")
        return

    total_in = 0
    total_out = 0

    for src in files:
        rel = src.relative_to(folder)
        if any(part in IGNORE_DIR_NAMES for part in rel.parts):
            continue

        dst = src.with_suffix(".webp")
        try:
            with Image.open(src) as im:
                # Preserve alpha if present
                if im.mode in ("RGBA", "LA"):
                    im = im.convert("RGBA")
                else:
                    im = im.convert("RGB")

                # optional resize
                if max_width and im.width > max_width:
                    ratio = max_width / im.width
                    new_size = (max_width, int(im.height * ratio))
                    im = im.resize(new_size, Image.LANCZOS)

                icc = im.info.get("icc_profile")

                size_before = src.stat().st_size
                size_after, used_q = save_webp_fit_size(
                    im, dst, target_kb=target_kb, icc_profile=icc
                )


            # move original to backup
            rel_parent = src.parent.relative_to(folder)
            (backup_dir / rel_parent).mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(backup_dir / rel_parent / src.name))

            total_in += size_before
            total_out += size_after

            print(f"[OK] {rel} -> {dst.name} "
                  f"(q={used_q}, {human_kb(size_before)} → {human_kb(size_after)})")

        except Exception as e:
            print(f"[ERR] {rel}: {e}")

    print("\nDone.")
    print(f"Original total: {human_kb(total_in)}")
    print(f"WebP total    : {human_kb(total_out)}")
    print(f"Saved         : {human_kb(total_in - total_out)}")
    print(f"Originals backed up to: {backup_dir}")

def main():
    ap = argparse.ArgumentParser(
        description="Convert all images in a folder to WebP (~target size) and back up originals."
    )
    ap.add_argument("--folder", required=True, help="Folder containing images")
    ap.add_argument("--target-kb", type=int, default=1024,
                    help="Target size per image in KB (default: 1024 ≈ 1MB)")
    ap.add_argument("--max-width", type=int, default=1920,
                    help="Optional max width resize (default: 1920; set 0 to disable)")
    ap.add_argument("--recursive", action="store_true",
                    help="Recurse into subfolders")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    max_w = None if (args.max_width is None or args.max_width == 0) else args.max_width
    process_folder(folder, target_kb=args.target_kb, max_width=max_w, recursive=args.recursive)

if __name__ == "__main__":
    main()
