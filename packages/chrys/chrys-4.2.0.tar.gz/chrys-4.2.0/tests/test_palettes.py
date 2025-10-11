from chrys.palettes import discrete_palette, parse_palette_name, VEGA_ACCENT

import pytest
import unittest


class TestParsePaletteName(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(parse_palette_name(VEGA_ACCENT), ("vega", "accent"))

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            parse_palette_name("lorem ipsum")


class TestDiscretePalette(unittest.TestCase):
    def test_no_size(self):
        self.assertEqual(
            discrete_palette(VEGA_ACCENT),
            ["#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0", "#f0027f"],
        )

    def test_valid_size(self):
        self.assertEqual(
            discrete_palette(VEGA_ACCENT, 8),
            [
                "#7fc97f",
                "#beaed4",
                "#fdc086",
                "#ffff99",
                "#386cb0",
                "#f0027f",
                "#bf5b17",
                "#666666",
            ],
        )

    def test_invalid_size(self):
        self.assertEqual(
            discrete_palette(VEGA_ACCENT, 20),
            [
                "#7fc97f",
                "#beaed4",
                "#fdc086",
                "#ffff99",
                "#386cb0",
                "#f0027f",
                "#bf5b17",
                "#666666",
            ],
        )

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            discrete_palette("lorem ipsum")
