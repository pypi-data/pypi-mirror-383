"""Adaptive material band localisation utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
from PIL import Image

import chanfig
import cv2 as cv
import pandas as pd
import numpy as np
from tqdm import tqdm


@dataclass
class MaterialBBox:
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


def _largest_segment(mask: np.ndarray, scores: np.ndarray) -> Tuple[int, int]:
    best_start = best_end = 0
    best_score = -np.inf
    current_start = None
    for idx, flag in enumerate(mask):
        if flag:
            if current_start is None:
                current_start = idx
        elif current_start is not None:
            candidate = slice(current_start, idx)
            score = float(scores[candidate].sum())
            if score > best_score:
                best_start, best_end, best_score = current_start, idx, score
            current_start = None
    if current_start is not None:
        candidate = slice(current_start, mask.size)
        score = float(scores[candidate].sum())
        if score > best_score:
            best_start, best_end = current_start, mask.size
    if best_end <= best_start:
        peak = int(np.argmax(scores))
        return peak, peak + 1
    return best_start, best_end


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


def _column_weights(width: int) -> np.ndarray:
    positions = (np.arange(width) - (width - 1) / 2) / max(width / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


def _row_weights(height: int) -> np.ndarray:
    positions = (np.arange(height) - (height - 1) / 2) / max(height / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


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


def _vertical_gradient_profiles(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    sigma = max(1.0, min(image.shape) / 1500.0)
    blurred = cv.GaussianBlur(image, (0, 0), sigma)
    sobel = cv.Sobel(blurred, cv.CV_32F, 0, 1, ksize=3)
    col_weights = _column_weights(image.shape[1])
    row_weights = _row_weights(image.shape[0])
    positive = np.maximum(sobel, 0.0) * col_weights
    negative = np.maximum(-sobel, 0.0) * col_weights
    pos_profile = positive.sum(axis=1) * row_weights
    neg_profile = negative.sum(axis=1) * row_weights
    return pos_profile, neg_profile


def _initial_vertical_bounds(pos_profile: np.ndarray, neg_profile: np.ndarray) -> Tuple[int, int, int]:
    height = pos_profile.size
    window = max(5, height // 200)
    pos_smooth = _smooth_sequence(pos_profile, window)
    neg_smooth = _smooth_sequence(neg_profile, window)
    bottom_peak = int(np.argmax(neg_smooth))
    peaks = _local_maxima(pos_smooth)
    max_gap = max(height // 4, 400)
    candidates = [idx for idx in peaks if 0 < bottom_peak - idx <= max_gap]
    if not candidates and bottom_peak > 0:
        candidates = [int(np.argmax(pos_smooth[:bottom_peak]))]
    top_peak = max(candidates, key=lambda idx: pos_smooth[idx]) if candidates else 0
    top_peak = int(top_peak)
    bottom_peak = max(top_peak + 1, bottom_peak)
    return top_peak, bottom_peak, window


def _refine_vertical_bounds(band: np.ndarray, start: int, end: int, window: int) -> Tuple[int, int]:
    height = band.shape[0]
    if height == 0:
        return 0, 0
    lower = max(0, min(start, end) - max(window * 2, 15))
    upper = min(height, max(start, end) + max(window * 2, 15))
    if upper - lower <= 1:
        return lower, upper
    band_slice = band[lower:upper]
    percentile = min(99.0, 95.0 + height / 8000.0)
    row_scores = np.percentile(band_slice, percentile, axis=1)
    row_scores = _smooth_sequence(row_scores, max(3, band_slice.shape[0] // 120))
    row_scores = np.clip(row_scores, 0.0, None)
    rel_top, rel_bottom = _energy_window(row_scores, 0.2, 0.8)
    top = lower + rel_top
    bottom = lower + rel_bottom
    if bottom <= top:
        bottom = min(height, top + max(2, int(np.ceil((upper - lower) * 0.1))))
    return top, bottom


def _horizontal_bounds(gray: np.ndarray, top: int, bottom: int) -> Tuple[int, int]:
    height, width = gray.shape
    top = max(0, min(top, height - 1))
    bottom = max(top + 1, min(bottom, height))
    strip = gray[top:bottom]
    if strip.size == 0:
        return 0, width
    profile = strip.mean(axis=0).astype(np.float64)
    sigma = max(1.0, width / 1500.0)
    smoothed = cv.GaussianBlur(profile.reshape(1, -1), (0, 0), sigma).reshape(-1)
    gradient = np.gradient(smoothed)
    center = (width - 1) / 2.0
    sigma_weight = max(width / 3.5, 1.0)
    weights = np.exp(-((np.arange(width) - center) ** 2) / (2.0 * sigma_weight**2))
    weighted = gradient * weights
    center_idx = int(round(center))
    if center_idx <= 0:
        left = int(np.argmin(weighted))
    else:
        left = int(np.argmin(weighted[:center_idx]))
    if center_idx >= width - 1:
        right = int(np.argmax(weighted))
    else:
        right = center_idx + int(np.argmax(weighted[center_idx:]))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width - 1))
    return left, right


def detect_material_bbox(gray: np.ndarray, config: Config) -> MaterialBBox:
    processed = _preprocess(gray)
    band = _band_image(processed)

    pos_profile, neg_profile = _vertical_gradient_profiles(processed)
    rough_top, rough_bottom, window = _initial_vertical_bounds(pos_profile, neg_profile)
    top, bottom = _refine_vertical_bounds(band, rough_top, rough_bottom, window)

    left, right = _horizontal_bounds(gray, top, bottom)

    height, width = processed.shape
    top = max(0, min(top, height - 2))
    bottom = max(top + 1, min(bottom, height))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width))

    return MaterialBBox(top=top, bottom=bottom, left=left, right=right)


def draw_bbox(image: np.ndarray, box: MaterialBBox, config: Config) -> np.ndarray:
    annotated = image.copy()
    cv.rectangle(
        annotated,
        (int(box.left), int(box.top)),
        (int(box.right), int(box.bottom)),
        tuple(int(v) for v in config.bbox_color),
        int(config.bbox_thickness),
    )
    return annotated


def process_image(input: str, output: str, config: Config) -> Tuple[MaterialBBox, Path]:
    input_path = Path(input)
    color = cv.imread(str(input_path), cv.IMREAD_COLOR)
    if color is None:
        raise FileNotFoundError(f"unable to read image: {input_path}")
    gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)

    bbox = detect_material_bbox(gray, config)
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
        ret.append({"id": f, "time": time, "height": box.height, "width": box.width, "top": box.top, "left": box.left, "bottom": box.bottom, "right": box.right})
    df = pd.DataFrame(ret)
    df.to_csv(cfg.table, index=False)
    print(f"saved table -> {cfg.table}")
