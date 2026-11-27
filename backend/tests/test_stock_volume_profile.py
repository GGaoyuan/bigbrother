from unittest import TestCase

from app.models.kline.model import Candle
from app.models.volume_profile.model import ValueArea
from app.api.volume_profile import calculate_profile


def minute(low, high, close, volume, stamp=0):
    return Candle(stamp, stamp + 60, low, high, low, close, volume, None, "shares")


class ProfileCalculationTests(TestCase):
    def test_flat_minute_and_zero_volume(self):
        result = calculate_profile((minute(10.13, 10.13, 10.13, 1200),))
        self.assertEqual((result.step_cents, result.total_volume, result.poc.price_cents), (1, 1200, 1013))
        self.assertEqual(result.value_area, ValueArea(1013, 1013, 1200))
        empty = calculate_profile((minute(10, 10, 10, 0),))
        self.assertEqual(empty.total_volume, 0)
        self.assertIsNone(empty.poc)

    def test_representative_price_weights_and_exact_share_conservation(self):
        result = calculate_profile((minute(10.00, 10.04, 10.04, 97),))
        volumes = {level.price_cents: level.volume for level in result.levels}
        self.assertEqual(result.step_cents, 1)
        self.assertEqual(result.total_volume, 97)
        self.assertEqual(sum(volumes.values()), 97)
        self.assertEqual(set(volumes), set(range(1000, 1005)))
        self.assertGreater(volumes[1003], volumes[1000])
        self.assertEqual(result.poc.price_cents, 1003)

    def test_adaptive_step_and_flat_off_center_minute(self):
        result = calculate_profile((
            minute(10.01, 10.01, 10.01, 17), minute(12, 22.09, 21, 100_003, 60),
        ))
        self.assertGreater(result.step_cents, 1)
        self.assertEqual(sum(level.volume for level in result.levels), 100_020)
        self.assertTrue(all(1001 <= level.low_price_cents <= level.high_price_cents <= 2209
                            for level in result.levels))
        bottom = result.levels[-1]
        self.assertEqual(bottom.low_price_cents, 1001)
        self.assertEqual(bottom.volume, 17)
        self.assertGreaterEqual(result.value_area.volume * 100, 70 * result.total_volume)

    def test_value_area_widens_contiguously_across_empty_bands(self):
        result = calculate_profile((minute(9.01, 9.01, 9.01, 40), minute(10, 10, 10, 60, 60)))
        self.assertEqual(result.value_area, ValueArea(901, 1000, 100))

    def test_steps_are_aligned_to_market_tick_size(self):
        result = calculate_profile((minute(10.00, 30.10, 19.20, 101),), tick_cents=5)
        self.assertGreater(result.step_cents, 5)
        self.assertEqual(result.step_cents % 5, 0)
        self.assertTrue(all(level.price_cents % 5 == 0 for level in result.levels))
