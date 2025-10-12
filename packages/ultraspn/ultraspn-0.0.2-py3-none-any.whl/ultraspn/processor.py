from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import chanfig
import cv2 as cv
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm


@dataclass
class BoundingBox:
    top: int
    bottom: int
    left: int
    right: int

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)


class Config(chanfig.Config):
    input: str = "images"
    output: str = "outputs"
    table: str = "zx.csv"
    percentile: float = 92.0
    bbox_color: Tuple[int, int, int] = (0, 255, 0)
    bbox_thickness: int = 5

    def post(self) -> None:
        if not (0.0 < self.percentile <= 100.0):
            raise ValueError("percentile must be within (0, 100]")


def _ensure_odd(value: int) -> int:
    return value if value % 2 == 1 else value + 1


def _smooth_sequence(sequence: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return sequence
    window = _ensure_odd(int(window))
    kernel = np.ones(window, dtype=np.float64) / window
    return np.convolve(sequence, kernel, mode="same")


def _clahe_parameters(gray: np.ndarray) -> Tuple[float, Tuple[int, int]]:
    h, w = gray.shape
    grid = max(2, int(round(np.sqrt(h * w) / 150)))
    clip = float(np.clip(np.var(gray) / 1024 + 1.5, 1.0, 8.0))
    return clip, (grid, grid)


def _preprocess(gray: np.ndarray) -> np.ndarray:
    clip_limit, tile_grid = _clahe_parameters(gray)
    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
    enhanced = clahe.apply(gray)
    kernel = _ensure_odd(max(3, int(round(min(gray.shape) / 150))))
    return cv.GaussianBlur(enhanced, (kernel, kernel), 0)


def _band_image(gray: np.ndarray) -> np.ndarray:
    blur_size = _ensure_odd(max(21, int(round(gray.shape[1] / 20))))
    baseline = cv.GaussianBlur(gray, (blur_size, blur_size), 0)
    band = cv.subtract(gray, baseline)
    return cv.normalize(band, None, 0, 255, cv.NORM_MINMAX).astype(np.float32)


def _color_band(image: np.ndarray) -> np.ndarray:
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    processed_sat = _preprocess(saturation)
    band_sat = _band_image(processed_sat)

    red = image[:, :, 2]
    blue = image[:, :, 0]
    rb_diff = cv.absdiff(red, blue)
    processed_diff = _preprocess(rb_diff)
    band_diff = _band_image(processed_diff)

    return np.maximum(band_sat, band_diff).astype(np.float32)


def _column_weights(width: int) -> np.ndarray:
    positions = (np.arange(width) - (width - 1) / 2) / max(width / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


def _row_weights(height: int) -> np.ndarray:
    positions = (np.arange(height) - (height - 1) / 2) / max(height / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


def _sobel_profiles(image: np.ndarray, axis: int) -> Tuple[np.ndarray, np.ndarray]:
    if axis == 0:
        grad = cv.Sobel(image, cv.CV_32F, 0, 1, ksize=3)
        col_weights = _column_weights(image.shape[1])
        row_weights = _row_weights(image.shape[0])
        positive = (np.maximum(grad, 0.0) * col_weights).sum(axis=1) * row_weights
        negative = (np.maximum(-grad, 0.0) * col_weights).sum(axis=1) * row_weights
    elif axis == 1:
        grad = cv.Sobel(image, cv.CV_32F, 1, 0, ksize=3)
        row_weights = _row_weights(image.shape[0])
        weighted = np.maximum(grad, 0.0) * row_weights[:, None]
        col_weights = _column_weights(image.shape[1]) ** 0.5
        positive = weighted.sum(axis=0) * col_weights
        weighted_neg = np.maximum(-grad, 0.0) * row_weights[:, None]
        negative = weighted_neg.sum(axis=0) * col_weights
    else:
        raise ValueError("axis must be 0 (vertical) or 1 (horizontal)")
    return positive.astype(np.float64), negative.astype(np.float64)


def _column_energy(
    primary_slice: np.ndarray,
    extra_slice: Optional[np.ndarray],
    smooth_sigma: float,
    blend: float = 0.35,
) -> np.ndarray:
    energy = np.percentile(primary_slice, 97.0, axis=0).astype(np.float64)
    if extra_slice is not None and extra_slice.size:
        extra = np.percentile(extra_slice, 97.0, axis=0).astype(np.float64)
        energy = energy + blend * extra
    energy = cv.GaussianBlur(energy.reshape(1, -1), (0, 0), smooth_sigma).reshape(-1)
    energy -= energy.min()
    if not np.any(energy):
        return np.ones_like(energy)
    return energy / (energy.max() + 1e-9)


def _row_profile(band: np.ndarray, percentile: float) -> np.ndarray:
    weighted = band * _column_weights(band.shape[1])
    return np.percentile(weighted, percentile, axis=1).astype(np.float64)


def _column_profile(band_slice: np.ndarray, percentile: float) -> np.ndarray:
    weighted = (band_slice.T * _row_weights(band_slice.shape[0])).T
    return np.percentile(weighted, percentile, axis=0).astype(np.float64)


def _refine_bounds(profile: np.ndarray, start: int, end: int, margin: int) -> Tuple[int, int]:
    start = max(0, min(start, profile.size - 2))
    end = max(start + 1, min(end, profile.size))
    gradient = np.gradient(profile)
    top_window = gradient[max(0, start - margin) : min(profile.size, start + margin)]
    bottom_window = gradient[max(0, end - margin) : min(profile.size, end + margin)]
    top_idx = max(0, start - margin) + int(np.argmax(top_window)) if top_window.size else start
    bottom_idx = max(0, end - margin) + int(np.argmin(bottom_window)) if bottom_window.size else end
    bottom_idx = max(top_idx + 1, bottom_idx)
    return top_idx, min(profile.size, bottom_idx)


def _energy_window(values: np.ndarray, lower: float, upper: float) -> Tuple[int, int]:
    length = values.size
    if length == 0:
        return 0, 0

    weights = np.clip(values.astype(np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return 0, length

    cumulative = np.cumsum(weights) / total
    start = int(np.searchsorted(cumulative, float(np.clip(lower, 0.0, 1.0)), side="left"))
    end = int(np.searchsorted(cumulative, float(np.clip(upper, 0.0, 1.0)), side="right"))
    start = max(0, min(start, length - 1))
    end = max(start + 1, min(end, length))

    if end <= start:
        peak = int(np.argmax(weights))
        start = max(0, peak - 1)
        end = min(length, peak + 2)

    return start, end


def _moment_window(values: np.ndarray, minimum: int) -> Tuple[int, int]:
    length = values.size
    if length == 0:
        return 0, 0

    weights = np.clip(values.astype(np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return 0, length

    positions = (np.arange(length, dtype=np.float64) + 0.5) / float(length)
    mean = float(np.dot(weights, positions) / total)
    variance = float(np.dot(weights, (positions - mean) ** 2) / total)
    sigma = max(np.sqrt(max(variance, 0.0)), 1.0 / length)

    lower = max(0.0, mean - sigma)
    upper = min(1.0, mean + sigma)

    start = int(np.floor(lower * length))
    end = int(np.ceil(upper * length))
    if end - start < minimum:
        padding = (minimum - (end - start)) / (2.0 * length)
        lower = max(0.0, lower - padding)
        upper = min(1.0, upper + padding)
        start = int(np.floor(lower * length))
        end = int(np.ceil(upper * length))

    start = max(0, min(start, length - 1))
    end = max(start + 1, min(end, length))
    return start, end


def _local_maxima(values: np.ndarray) -> np.ndarray:
    if values.size < 3:
        return np.array([], dtype=np.int32)
    gradient = np.diff(values)
    signs = np.sign(gradient)
    turning = (np.hstack([signs, 0.0]) < 0.0) & (np.hstack([0.0, signs]) > 0.0)
    return np.where(turning)[0].astype(np.int32)


def _localize_vertical_bounds(
    enhanced_gray: np.ndarray,
    band: np.ndarray,
    percentile: float,
) -> Tuple[int, int]:
    height = enhanced_gray.shape[0]
    if height == 0:
        return 0, 0

    blur_sigma = max(1.0, min(enhanced_gray.shape) / 1500.0)
    blurred = cv.GaussianBlur(enhanced_gray, (0, 0), blur_sigma)
    upward_edges, downward_edges = _sobel_profiles(blurred, axis=0)

    smoothing = max(5, height // 200)
    upward_smooth = _smooth_sequence(upward_edges, smoothing)
    downward_smooth = _smooth_sequence(downward_edges, smoothing)

    bottom_peak = int(np.argmax(downward_smooth))
    peaks = _local_maxima(upward_smooth)
    max_gap = max(height // 4, 400)
    candidates = [idx for idx in peaks if 0 < bottom_peak - idx <= max_gap]
    if not candidates and bottom_peak > 0:
        candidates = [int(np.argmax(upward_smooth[:bottom_peak]))]
    top_estimate = (
        max(candidates, key=lambda idx: upward_smooth[idx]) if candidates else max(0, bottom_peak - height // 10)
    )
    top_estimate = int(top_estimate)
    bottom_estimate = max(top_estimate + 1, bottom_peak)

    percentile_energy = min(99.0, 95.0 + height / 8000.0)
    base_margin = max(smoothing * 3, height // 100, 40)
    min_height = max(40, height // 100)
    top_refined, bottom_refined = top_estimate, bottom_estimate

    for lower_frac, upper_frac in ((0.2, 0.8), (0.15, 0.85)):
        for scale in (1, 2):
            margin = min(height, base_margin * scale)
            lower = max(0, min(top_refined, bottom_refined) - margin)
            upper = min(height, max(top_refined, bottom_refined) + margin)
            if upper - lower <= 1:
                continue
            band_segment = band[lower:upper]
            energy = np.percentile(band_segment, percentile_energy, axis=1)
            smooth_window = max(3, band_segment.shape[0] // 120)
            energy = _smooth_sequence(energy, smooth_window)
            energy = np.clip(energy, 0.0, None)
            rel_top, rel_bottom = _energy_window(energy, lower_frac, upper_frac)
            candidate_top = lower + rel_top
            candidate_bottom = lower + rel_bottom
            if candidate_bottom <= candidate_top:
                candidate_bottom = min(height, candidate_top + max(2, int(np.ceil((upper - lower) * 0.1))))
            top_refined, bottom_refined = candidate_top, candidate_bottom
            if bottom_refined - top_refined >= min_height:
                break
        else:
            continue
        break

    row_profile = _row_profile(band, percentile)
    refinement_margin = max(10, min((bottom_refined - top_refined) // 2, 60))
    top_final, bottom_final = _refine_bounds(row_profile, top_refined, bottom_refined, refinement_margin)
    top_final = max(0, min(top_final, height - 2))
    bottom_final = max(top_final + 1, min(bottom_final, height))
    return top_final, bottom_final


def _localize_horizontal_bounds(
    enhanced_gray: np.ndarray,
    band: np.ndarray,
    top: int,
    bottom: int,
    color_band: Optional[np.ndarray] = None,
) -> Tuple[int, int]:
    height, width = enhanced_gray.shape
    top = max(0, min(top, height - 1))
    bottom = max(top + 1, min(bottom, height))
    strip_proc = enhanced_gray[top:bottom]
    if strip_proc.size == 0:
        return 0, width

    profile = strip_proc.mean(axis=0).astype(np.float64)
    sigma = max(1.0, width / 1800.0)
    smoothed = cv.GaussianBlur(profile.reshape(1, -1), (0, 0), sigma).reshape(-1)
    gradient = np.gradient(smoothed)
    center = (width - 1) / 2.0
    sigma_weight = max(width / 4.0, 1.0)
    weights = np.exp(-((np.arange(width) - center) ** 2) / (2.0 * sigma_weight**2))

    band_slice = band[top:bottom]
    smooth_cols = max(1.0, width / 2000.0)
    extra_slice = color_band[top:bottom] if color_band is not None else None
    col_norm = _column_energy(band_slice, extra_slice, smooth_cols)
    col_boost = 0.5 + 0.5 * np.clip(col_norm, 0.0, 1.0)
    center_idx = int(round(center))
    weighted = gradient * weights
    sobel_pos, sobel_neg = _sobel_profiles(strip_proc, axis=1)
    negative = (np.clip(-weighted, 0.0, None) + sobel_neg) * col_boost
    positive = (np.clip(weighted, 0.0, None) + sobel_pos) * col_boost

    if center_idx <= 0:
        left_region = negative
        grad_left = int(np.argmax(left_region)) if left_region.size else 0
        combo_left = grad_left
    else:
        left_region = negative[:center_idx]
        if np.all(left_region == 0.0):
            grad_left = int(np.argmin(weighted[:center_idx]))
            combo_left = grad_left
        else:
            grad_left = int(np.argmax(left_region))
            left_norm = left_region / (left_region.max() + 1e-9)
            combo_scores = left_norm * (0.3 + 0.7 * col_norm[:center_idx])
            combo_left = int(np.argmax(combo_scores))
    if center_idx >= width - 1:
        right_region = positive
        grad_right = int(np.argmax(right_region)) if right_region.size else width - 1
        combo_right = grad_right
    else:
        right_region = positive[center_idx:]
        if np.all(right_region == 0.0):
            grad_right = center_idx + int(np.argmax(weighted[center_idx:]))
            combo_right = grad_right
        else:
            grad_right = center_idx + int(np.argmax(right_region))
            right_norm = right_region / (right_region.max() + 1e-9)
            combo_scores = right_norm * (0.3 + 0.7 * col_norm[center_idx:])
            combo_right = center_idx + int(np.argmax(combo_scores))

    threshold = 0.15
    if left_region.size:
        left_strength = col_norm[min(grad_left, col_norm.size - 1)]
        left = grad_left if left_strength >= threshold else combo_left
    else:
        left = 0
    if right_region.size:
        right_strength = col_norm[min(grad_right, col_norm.size - 1)]
        right = grad_right if right_strength >= threshold else combo_right
    else:
        right = width - 1

    if right <= left:
        right = min(width - 1, left + max(width // 40, 10))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width - 1))
    return left, right


def detect_bbox(image: np.ndarray, config: Config) -> BoundingBox:
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    enhanced_gray = _preprocess(gray)
    gray_band = _band_image(enhanced_gray)
    color_band = _color_band(image)
    combined_band = np.maximum(gray_band, color_band)

    top, bottom = _localize_vertical_bounds(enhanced_gray, combined_band, config.percentile)
    left, right = _localize_horizontal_bounds(enhanced_gray, gray_band, top, bottom, color_band=color_band)

    height, width = enhanced_gray.shape
    top = max(0, min(top, height - 2))
    bottom = max(top + 1, min(bottom, height))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width))

    return BoundingBox(top=top, bottom=bottom, left=left, right=right)


def draw_bbox(image: np.ndarray, box: BoundingBox, config: Config) -> np.ndarray:
    annotated = image.copy()
    cv.rectangle(
        annotated,
        (int(box.left), int(box.top)),
        (int(box.right), int(box.bottom)),
        tuple(int(v) for v in config.bbox_color),
        int(config.bbox_thickness),
    )
    return annotated


def process_image(input: str, output: str, config: Config) -> Tuple[BoundingBox, Path]:
    input_path = Path(input)
    color = cv.imread(str(input_path), cv.IMREAD_COLOR)
    if color is None:
        raise FileNotFoundError(f"unable to read image: {input_path}")

    bbox = detect_bbox(color, config)
    annotated = draw_bbox(color, bbox, config)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_path)
    exif = img.getexif()
    time = exif[306]
    if not cv.imwrite(str(output_path), annotated):
        raise RuntimeError(f"failed to save {output_path}")
    return bbox, time


if __name__ == "__main__":
    cfg = Config().parse()
    ret = []
    files = sorted(os.listdir(cfg.input))
    for f in tqdm(files, total=len(files), desc="Processing images"):
        box, time = process_image(os.path.join(cfg.input, f), os.path.join(cfg.output, f), cfg)
        ret.append(
            {
                "id": f,
                "time": time,
                "height": box.height,
                "width": box.width,
                "top": box.top,
                "left": box.left,
                "bottom": box.bottom,
                "right": box.right,
            }
        )
    df = pd.DataFrame(ret)
    df.to_csv(cfg.table, index=False)
    print(f"saved table -> {cfg.table}")
