"""Creek measurement math: float method, cross-section, continuity speed-up."""

import pytest

from creekturbine import siting


def test_velocity_from_float_applies_correction():
    # 5 m in 10 s = 0.5 m/s surface -> 0.425 m/s mean at default 0.85
    assert siting.velocity_from_float(5.0, 10.0) == pytest.approx(0.425)


def test_velocity_from_float_rejects_zero_time():
    with pytest.raises(ValueError):
        siting.velocity_from_float(5.0, 0.0)


def test_channel_area_and_flow():
    assert siting.channel_area(2.0, 0.5) == pytest.approx(1.0)
    assert siting.flow_rate_m3s(1.0, 0.4) == pytest.approx(0.4)
    assert siting.flow_rate_lpm(1.0, 0.4) == pytest.approx(0.4 * 60000)


def test_continuity_speed_up():
    # halve the area -> double the speed
    assert siting.continuity_velocity(0.5, 1.0, 0.5) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        siting.continuity_velocity(0.5, 1.0, 0.0)


def test_creek_measurement_dataclass():
    m = siting.CreekMeasurement(width_m=1.6, avg_depth_m=0.4,
                                float_distance_m=5.0, float_seconds=9.5)
    assert m.area == pytest.approx(0.64)
    assert m.mean_velocity == pytest.approx((5.0 / 9.5) * 0.85)
    assert m.flow_m3s == pytest.approx(m.area * m.mean_velocity)
