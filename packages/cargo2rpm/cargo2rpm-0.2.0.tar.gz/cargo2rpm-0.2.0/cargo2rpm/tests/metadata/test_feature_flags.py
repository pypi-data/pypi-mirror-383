from cargo2rpm.metadata import FeatureFlags

import pytest


def test_feature_flags_invalid():
    with pytest.raises(ValueError) as exc:
        FeatureFlags(all_features=True, features=["default"])
    assert "Cannot specify both '--all-features' and '--features'." in str(exc.value)

    with pytest.raises(ValueError) as exc:
        FeatureFlags(no_default_features=True, all_features=True)
    assert "Cannot specify both '--all-features' and '--no-default-features'." in str(exc.value)
