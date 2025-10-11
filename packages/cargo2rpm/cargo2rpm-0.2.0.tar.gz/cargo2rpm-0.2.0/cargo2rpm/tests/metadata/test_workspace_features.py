from cargo2rpm.metadata import FeatureFlags
from cargo2rpm.utils import load_metadata_from_resource, short_repr

import pytest


@pytest.mark.parametrize(
    "filename,flags,expected",
    [
        # default features
        (
            "espanso-2.1.8.json",
            FeatureFlags(),
            {
                "espanso": FeatureFlags(),
                "espanso-clipboard": FeatureFlags(features=["avoid-gdi"]),
                "espanso-config": FeatureFlags(),
                "espanso-detect": FeatureFlags(),
                "espanso-engine": FeatureFlags(),
                "espanso-info": FeatureFlags(),
                "espanso-inject": FeatureFlags(),
                "espanso-ipc": FeatureFlags(),
                "espanso-kvs": FeatureFlags(),
                "espanso-mac-utils": FeatureFlags(),
                "espanso-match": FeatureFlags(),
                "espanso-migrate": FeatureFlags(),
                "espanso-modulo": FeatureFlags(),
                "espanso-package": FeatureFlags(features=["default-tls"]),
                "espanso-path": FeatureFlags(),
                "espanso-render": FeatureFlags(),
                "espanso-ui": FeatureFlags(features=["avoid-gdi"]),
            },
        ),
        # all features
        (
            "espanso-2.1.8.json",
            FeatureFlags(all_features=True),
            {
                "espanso": FeatureFlags(all_features=True),
                "espanso-clipboard": FeatureFlags(all_features=True),
                "espanso-config": FeatureFlags(all_features=True),
                "espanso-detect": FeatureFlags(all_features=True),
                "espanso-engine": FeatureFlags(all_features=True),
                "espanso-info": FeatureFlags(all_features=True),
                "espanso-inject": FeatureFlags(all_features=True),
                "espanso-ipc": FeatureFlags(all_features=True),
                "espanso-kvs": FeatureFlags(all_features=True),
                "espanso-mac-utils": FeatureFlags(all_features=True),
                "espanso-match": FeatureFlags(all_features=True),
                "espanso-migrate": FeatureFlags(all_features=True),
                "espanso-modulo": FeatureFlags(all_features=True),
                "espanso-package": FeatureFlags(all_features=True),
                "espanso-path": FeatureFlags(all_features=True),
                "espanso-render": FeatureFlags(all_features=True),
                "espanso-ui": FeatureFlags(all_features=True),
            },
        ),
        # no default features
        (
            "espanso-2.1.8.json",
            FeatureFlags(no_default_features=True),
            {
                "espanso": FeatureFlags(no_default_features=True),
                "espanso-clipboard": FeatureFlags(),
                "espanso-config": FeatureFlags(),
                "espanso-detect": FeatureFlags(),
                "espanso-engine": FeatureFlags(),
                "espanso-info": FeatureFlags(),
                "espanso-inject": FeatureFlags(),
                "espanso-ipc": FeatureFlags(),
                "espanso-kvs": FeatureFlags(),
                "espanso-mac-utils": FeatureFlags(),
                "espanso-match": FeatureFlags(),
                "espanso-migrate": FeatureFlags(),
                "espanso-modulo": FeatureFlags(),
                "espanso-package": FeatureFlags(),
                "espanso-path": FeatureFlags(),
                "espanso-render": FeatureFlags(),
                "espanso-ui": FeatureFlags(),
            },
        ),
        # default features
        (
            "fapolicy-analyzer-0.6.8.json",
            FeatureFlags(),
            {
                "fapolicy-analyzer": FeatureFlags(),
                "fapolicy-daemon": FeatureFlags(),
                "fapolicy-trust": FeatureFlags(),
                "fapolicy-util": FeatureFlags(),
                "fapolicy-rules": FeatureFlags(),
                "fapolicy-app": FeatureFlags(),
                "fapolicy-pyo3": FeatureFlags(),
                "fapolicy-tools": FeatureFlags(),
            },
        ),
        # all features
        (
            "fapolicy-analyzer-0.6.8.json",
            FeatureFlags(all_features=True),
            {
                "fapolicy-analyzer": FeatureFlags(all_features=True),
                "fapolicy-daemon": FeatureFlags(all_features=True),
                "fapolicy-trust": FeatureFlags(all_features=True),
                "fapolicy-util": FeatureFlags(all_features=True),
                "fapolicy-rules": FeatureFlags(all_features=True),
                "fapolicy-app": FeatureFlags(all_features=True),
                "fapolicy-pyo3": FeatureFlags(all_features=True),
                "fapolicy-tools": FeatureFlags(all_features=True),
            },
        ),
        # no default features
        (
            "fapolicy-analyzer-0.6.8.json",
            FeatureFlags(no_default_features=True),
            {
                "fapolicy-analyzer": FeatureFlags(),
                "fapolicy-daemon": FeatureFlags(),
                "fapolicy-trust": FeatureFlags(),
                "fapolicy-util": FeatureFlags(),
                "fapolicy-rules": FeatureFlags(),
                "fapolicy-app": FeatureFlags(),
                "fapolicy-pyo3": FeatureFlags(no_default_features=True),
                "fapolicy-tools": FeatureFlags(no_default_features=True),
            },
        ),
        # default features
        (
            "libblkio-1.2.2.json",
            FeatureFlags(),
            {
                "libblkio": FeatureFlags(),
                "blkio": FeatureFlags(
                    no_default_features=True,
                    features=[
                        "io_uring",
                        "nvme-io_uring",
                        "virtio-blk-vfio-pci",
                        "virtio-blk-vhost-user",
                        "virtio-blk-vhost-vdpa",
                    ],
                ),
                "virtio-driver": FeatureFlags(
                    no_default_features=True,
                    features=[
                        "pci",
                        "vhost-user",
                        "vhost-vdpa",
                    ],
                ),
            },
        ),
        # all features
        (
            "libblkio-1.2.2.json",
            FeatureFlags(all_features=True),
            {
                "libblkio": FeatureFlags(all_features=True),
                "blkio": FeatureFlags(all_features=True),
                "virtio-driver": FeatureFlags(all_features=True),
            },
        ),
        # no default features
        (
            "libblkio-1.2.2.json",
            FeatureFlags(no_default_features=True),
            {
                "libblkio": FeatureFlags(no_default_features=True),
                "blkio": FeatureFlags(no_default_features=True),
                "virtio-driver": FeatureFlags(no_default_features=True),
            },
        ),
        # default features + _unsafe-op-in-unsafe-fn
        (
            "libblkio-1.2.2.json",
            FeatureFlags(features=["_unsafe-op-in-unsafe-fn"]),
            {
                "libblkio": FeatureFlags(features=["_unsafe-op-in-unsafe-fn"]),
                "blkio": FeatureFlags(
                    no_default_features=True,
                    features=[
                        "_unsafe-op-in-unsafe-fn",
                        "io_uring",
                        "nvme-io_uring",
                        "virtio-blk-vfio-pci",
                        "virtio-blk-vhost-user",
                        "virtio-blk-vhost-vdpa",
                    ],
                ),
                "virtio-driver": FeatureFlags(
                    no_default_features=True,
                    features=[
                        "_unsafe-op-in-unsafe-fn",
                        "pci",
                        "vhost-user",
                        "vhost-vdpa",
                    ],
                ),
            },
        ),
        # no default features + _unsafe-op-in-unsafe-fn
        (
            "libblkio-1.2.2.json",
            FeatureFlags(no_default_features=True, features=["_unsafe-op-in-unsafe-fn"]),
            {
                "libblkio": FeatureFlags(no_default_features=True, features=["_unsafe-op-in-unsafe-fn"]),
                "blkio": FeatureFlags(no_default_features=True, features=["_unsafe-op-in-unsafe-fn"]),
                "virtio-driver": FeatureFlags(no_default_features=True, features=["_unsafe-op-in-unsafe-fn"]),
            },
        ),
        # default features
        (
            "zola-0.16.1.json",
            FeatureFlags(),
            {
                "config": FeatureFlags(),
                "errors": FeatureFlags(),
                "libs": FeatureFlags(features=["rust-tls"]),
                "utils": FeatureFlags(),
                "console": FeatureFlags(),
                "content": FeatureFlags(),
                "markdown": FeatureFlags(),
                "templates": FeatureFlags(),
                "imageproc": FeatureFlags(),
                "link_checker": FeatureFlags(),
                "search": FeatureFlags(),
                "site": FeatureFlags(),
                "zola": FeatureFlags(),
            },
        ),
        # default features + indexing-ja
        (
            "zola-0.16.1.json",
            FeatureFlags(features=["indexing-ja"]),
            {
                "config": FeatureFlags(),
                "errors": FeatureFlags(),
                "libs": FeatureFlags(features=["rust-tls", "indexing-ja"]),
                "utils": FeatureFlags(),
                "console": FeatureFlags(),
                "content": FeatureFlags(),
                "markdown": FeatureFlags(),
                "templates": FeatureFlags(),
                "imageproc": FeatureFlags(),
                "link_checker": FeatureFlags(),
                "search": FeatureFlags(),
                "site": FeatureFlags(),
                "zola": FeatureFlags(features=["indexing-ja"]),
            },
        ),
    ],
    ids=short_repr,
)
def test_get_enabled_features_for_workspace_members(filename: str, flags: FeatureFlags, expected: dict[str, FeatureFlags]):
    data = load_metadata_from_resource(filename)
    assert data.get_feature_flags_for_workspace_members(flags) == expected
