from neo_monitor.dashboard import _comparison_chart, _ranked_chart


def test_comparison_chart_encodes_the_four_primary_neo_attributes():
    chart = _comparison_chart()
    encoding = chart["encoding"]

    assert encoding["x"]["field"] == "miss_distance_lunar"
    assert encoding["y"]["field"] == "velocity_kph"
    assert encoding["size"]["field"] == "diameter_meters"
    assert encoding["color"]["field"] == "hazardous"


def test_ranked_chart_uses_a_point_for_closest_and_bars_for_larger_values():
    assert _ranked_chart("closest")["mark"]["type"] == "circle"
    assert _ranked_chart("fastest")["mark"]["type"] == "bar"
    assert _ranked_chart("largest")["mark"]["type"] == "bar"
