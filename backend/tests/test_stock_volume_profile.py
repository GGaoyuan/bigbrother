from unittest import TestCase

from app.data.stock_market_types import Candle
from app.data.stock_volume_profile import calculate_profile


def minute(low, high, close, volume, stamp=0):
    return Candle(stamp, stamp + 60, low, high, low, close, volume, None, "shares")


class ProfileCalculationTests(TestCase):
    def test_flat_minute_and_zero_volume(self):
        step, result = calculate_profile((minute(10.13, 10.13, 10.13, 1200),))
        self.assertEqual((step, result["total"], result["poc"]["priceCents"]), (1, 1200, 1013))
        self.assertEqual(result["valueArea"], {"low": 1013, "high": 1013, "volume": 1200})
        self.assertFalse(result["hasDirection"])
        self.assertIsNone(result["poc"]["delta"])
        self.assertEqual(calculate_profile((minute(10, 10, 10, 0),))[1]["total"], 0)

    def test_representative_price_weights_and_exact_share_conservation(self):
        step, result = calculate_profile((minute(10.00, 10.04, 10.04, 97),))
        volumes = {level["priceCents"]: level["total"] for level in result["levels"]}
        self.assertEqual(step, 1)
        self.assertEqual(result["total"], 97)
        self.assertEqual(sum(volumes.values()), 97)
        self.assertEqual(set(volumes), set(range(1000, 1005)))
        self.assertGreater(volumes[1003], volumes[1000])
        self.assertEqual(result["poc"]["priceCents"], 1003)

    def test_adaptive_step_and_flat_off_center_minute(self):
        step, result = calculate_profile((
            minute(10.01, 10.01, 10.01, 17), minute(12, 22.09, 21, 100_003, 60),
        ))
        self.assertGreater(step, 1)
        self.assertEqual(sum(level["total"] for level in result["levels"]), 100_020)
        self.assertTrue(all(1001 <= level["lowPriceCents"] <= level["highPriceCents"] <= 2209
                            for level in result["levels"]))
        bottom = result["levels"][-1]
        self.assertEqual(bottom["lowPriceCents"], 1001)
        self.assertEqual(bottom["total"], 17)
        self.assertGreaterEqual(result["valueArea"]["volume"] * 100, 70 * result["total"])

    def test_value_area_widens_contiguously_across_empty_bands(self):
        _, result = calculate_profile((minute(9.01, 9.01, 9.01, 40), minute(10, 10, 10, 60, 60)))
        self.assertEqual(result["valueArea"], {"low": 901, "high": 1000, "volume": 100})

    def test_steps_are_aligned_to_market_tick_size(self):
        step, result = calculate_profile((minute(10.00, 30.10, 19.20, 101),), tick_cents=5)
        self.assertGreater(step, 5)
        self.assertEqual(step % 5, 0)
        self.assertTrue(all(level["priceCents"] % 5 == 0 for level in result["levels"]))
