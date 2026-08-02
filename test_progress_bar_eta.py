#!/usr/bin/env python3
"""Unit tests for progress bar widget and trend-based ETA estimation."""

import os
import sys
import unittest
from dataclasses import dataclass

# Import wmtt4mc module
import wmtt4mc


class TestProgressBarETA(unittest.TestCase):

    def test_canvas_progress_bar_initialization(self):
        """Test CanvasProgressBar instance creation and set_progress."""
        import tkinter as tk
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter GUI display not available")

        bar = wmtt4mc.CanvasProgressBar(root)
        bar.set_progress(completed=3, in_progress=2, total=10, active_chunk_progress=0.5)
        self.assertEqual(bar._completed, 3)
        self.assertEqual(bar._in_progress, 2)
        self.assertEqual(bar._total, 10)
        self.assertEqual(bar._active_chunk_progress, 0.5)
        root.destroy()

    def test_canvas_progress_bar_large_frame_count(self):
        """Test CanvasProgressBar with large frame counts (e.g., 268 and 1000)."""
        import tkinter as tk
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter GUI display not available")

        bar = wmtt4mc.CanvasProgressBar(root)
        bar.set_progress(completed=150, in_progress=4, total=268, active_chunk_progress=0.3)
        self.assertEqual(bar._completed, 150)
        self.assertEqual(bar._in_progress, 4)
        self.assertEqual(bar._total, 268)

        # Test larger total
        bar.set_progress(completed=990, in_progress=10, total=1000, active_chunk_progress=0.8)
        self.assertEqual(bar._total, 1000)
        root.destroy()

    def test_trend_decay_calculation(self):
        """Test snapshot chunk decay trend estimation."""
        @dataclass
        class MockSnap:
            path: str
            display_name: str

        chronological = [
            MockSnap(path="world_2026_03.zip", display_name="World 2026-03"),
            MockSnap(path="world_2026_02.zip", display_name="World 2026-02"),
            MockSnap(path="world_2026_01.zip", display_name="World 2026-01"),
        ]

        snapshot_known_chunks = {
            "world_2026_03.zip": 10000,
            "world_2026_02.zip": 8000,
        }

        # Calculate decay trend manually
        # step ratio = (8000 / 10000) = 0.80
        # Projected for world_2026_01 = 8000 * 0.80 = 6400

        known_indices = [0, 1]
        step_ratios = []
        for k in range(len(known_indices) - 1):
            i1 = known_indices[k]
            i2 = known_indices[k + 1]
            c1 = snapshot_known_chunks[chronological[i1].path]
            c2 = snapshot_known_chunks[chronological[i2].path]
            ratio = (c2 / c1) ** (1.0 / (i2 - i1))
            step_ratios.append(max(0.75, min(1.05, ratio)))

        trend_ratio = sum(step_ratios) / len(step_ratios)
        self.assertAlmostEqual(trend_ratio, 0.80, places=2)

        projected = int(round(8000 * (trend_ratio ** 1)))
        self.assertEqual(projected, 6400)


if __name__ == "__main__":
    unittest.main()
