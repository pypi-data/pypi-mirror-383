import json

import pytest
from shapely.geometry import shape, Point
from clldutils.jsonlib import load

from cldfgeojson.create import *


def test_feature_collection():
    assert 'type' in feature_collection([])


@pytest.mark.parametrize(
    'in_,out_',
    [
        (0, 0),
        (1, 1),
        (-1, -1),
        (180, 180),
        (-180, -180),
        (181, -179),
        (540, 180),
        (-900, 180),
        (-181, 179),
    ]
)
def test_correct_longitude(in_, out_):
    assert correct_longitude(in_) == out_


def test_fixed_geometry(recwarn):
    f = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-10, -10],
                    [-10, 10],
                    [10, 10],
                    [10, -10],
                    [-10, -10],
                ],
                [
                    [-5, -5],
                    [-5, 5],
                    [5, 5],
                    [5, -5],
                    [-5, -5],
                ],
            ]
        }
    }
    assert not shape(f['geometry']).contains(Point(0, 0))
    res = fixed_geometry(f)
    assert not shape(res['geometry']).contains(Point(0, 0))
    assert shapely_fixed_geometry(f)

    f = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [5, 0],
                [-5, 0],
                [-5, 5],
                [0, 5],
                [0, -5],
                [5, -5],
                [5, 0],
            ]]
        }
    }
    res = fixed_geometry(f)
    assert res['geometry']['type'] == 'MultiPolygon'
    assert shape(res['geometry']).contains(Point(-2, 2))
    assert not shape(res['geometry']).contains(Point(2, 2))
    assert shapely_fixed_geometry(f)

    f = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [[
                    [5, 0],
                    [-5, 0],
                    [-5, 5],
                    [0, 5],
                    [0, -5],
                    [5, -5],
                    [5, 0],
                ]],
                [[
                    [370, 5],
                    [15, 5],
                    [15, 10],
                    [10, 10],
                    [10, 5],
                ]],
            ]
        }
    }
    res = fixed_geometry(f, fix_longitude=True)
    assert shape(res['geometry']).contains(Point(12, 7))
    assert shapely_fixed_geometry(f)

    f = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -179.70358951407547,
                        52.750507455036264
                    ],
                    [
                        179.96672360880183,
                        52.00163609753924
                    ],
                    [
                        -177.89334479610974,
                        50.62805205289558
                    ],
                    [
                        -179.9847165338706,
                        51.002602948712465
                    ],
                    [
                        -179.70358951407547,
                        52.750507455036264
                    ]
                ]
            ]
        }
    }
    res = fixed_geometry(f, fix_antimeridian=True)
    assert res['geometry']['type'] == 'MultiPolygon' and len(res['geometry']['coordinates']) == 2
    assert shapely_fixed_geometry(f)


def test_aggregate(glottolog_cldf):
    def make_feature(latoffset=0, lonoffset=0):
        return {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-90 + lonoffset, 35 + latoffset],
                    [-90 + lonoffset, 30 + latoffset],
                    [-85 + lonoffset, 30 + latoffset],
                    [-85 + lonoffset, 35 + latoffset],
                    [-90 + lonoffset, 35 + latoffset]
                ]]
            }
        }

    shapes = [
        (1, make_feature(latoffset=10), 'berl1235'),  # a dialect
        (2, make_feature(lonoffset=10), 'stan1295'),  # a language
        (3, make_feature(), 'high1289'),  # a subgroup
        (4, make_feature(), 'abin1243'),  # an isolate
    ]
    features, langs = aggregate(
        shapes,
        glottolog_cldf,
    )
    assert len(langs) == 2
    for feature, (glang, pids, fam) in zip(features, langs):
        if glang.id == 'stan1295':
            break
    assert len(pids) == 2
    # Make sure a point from the dialect polygon is in the merged language feature:
    assert shape(feature['geometry']).contains(Point(-87, 42))
    # Make sure a point from the sub-group polygon is **not** in the merged feature:
    assert not shape(feature['geometry']).contains(Point(-87, 33))

    features, langs = aggregate(
        shapes,
        glottolog_cldf,
        level='family',
    )
    assert len(langs) == 2
    for feature, (glang, pids, fam) in zip(features, langs):
        if glang.id == 'abin1243':
            assert fam is None
        if glang.id == 'indo1319':
            break
    assert len(pids) == 3
    # Make sure a point from the sub-group polygon is in the merged feature:
    assert shape(feature['geometry']).contains(Point(-87, 33))


@pytest.mark.parametrize(
    'tolerance,reduction',
    [
        (0.1, 50),
        (0.01, 40),
        (0.001, 10),  # the default
        (0.0001, 1.1),
    ]
)
def test_shapely_simplified_geometry(fixtures_dir, tolerance, reduction):
    f = load(fixtures_dir / 'irish.geojson')
    size = len(json.dumps(f))
    shapely_simplified_geometry(f, tolerance=tolerance)
    assert size / (2 * reduction) < len(json.dumps(f)) < size / reduction
