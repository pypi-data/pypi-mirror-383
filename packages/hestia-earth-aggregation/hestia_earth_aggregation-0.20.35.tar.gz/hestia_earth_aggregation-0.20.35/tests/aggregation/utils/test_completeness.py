import json
import pytest
from hestia_earth.schema import TermTermType, CompletenessField, EmissionMethodTier, SiteSiteType

from tests.utils import fixtures_path
from hestia_earth.aggregation.utils.completeness import (
    aggregate_completeness,
    emission_completeness_key,
    blank_node_completeness_key
)


def test_aggregate_completeness():
    with open(f"{fixtures_path}/cycle/wheatGrain.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    with open(f"{fixtures_path}/cycle/utils/completeness.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert aggregate_completeness(cycles) == expected


def test_get_input_completeness():
    emission = {
        'methodTier': EmissionMethodTier.BACKGROUND.value,
        'inputs': [
            {'termType': TermTermType.FUEL.value},
            {'termType': TermTermType.SEED.value},
            {'termType': TermTermType.ORGANICFERTILISER.value},
        ]
    }
    assert emission_completeness_key(emission) == 'electricityFuel-fertiliser-seed'


@pytest.mark.parametrize(
    'test_name,blank_node,site_type,expected_value',
    [
        (
            'emission no inputs',
            {'@type': 'Emission', 'methodTier': EmissionMethodTier.BACKGROUND.value},
            None,
            ''
        ),
        (
            'emission with inputs',
            {
                '@type': 'Emission',
                'methodTier': EmissionMethodTier.BACKGROUND.value,
                'inputs': [{'termType': TermTermType.ORGANICFERTILISER.value}]
            },
            None,
            CompletenessField.FERTILISER.value
        ),
        (
            'crop on agri-food processor',
            {
                '@type': 'Input',
                'term': {'termType': TermTermType.CROP.value, '@id': 'wheatGrain'}
            },
            SiteSiteType.AGRI_FOOD_PROCESSOR.value,
            CompletenessField.INGREDIENT.value
        ),
        (
            'crop on cropland',
            {
                '@type': 'Input',
                'term': {'termType': TermTermType.CROP.value, '@id': 'wheatGrain'}
            },
            SiteSiteType.CROPLAND.value,
            CompletenessField.ANIMALFEED.value
        )
    ]
)
def test_blank_node_completeness_key(test_name: str, blank_node: dict, site_type: str, expected_value: str):
    assert blank_node_completeness_key(blank_node, site_type=site_type) == expected_value, test_name
