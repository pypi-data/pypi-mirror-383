# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Fetch F-Droid repo data over the internet."""

import json
import hashlib
import pathlib
import zipfile
import tempfile
import urllib.request

from fdroidrepoapi import keytool, indexv2


def _sha256_of_file(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        # read in junks for less memory useage
        for byte_block in iter(lambda: f.read(16384), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def fetch_index_v2(repo_url, repo_fingerprint):
    """Download index (+entry.jar) and verify."""
    with tempfile.TemporaryDirectory() as tmpdir:
        jarpath = pathlib.Path(tmpdir) / "entry.jar"
        urllib.request.urlretrieve(repo_url.rstrip("/") + "/entry.jar", jarpath)
        keytool.verify_jar(jarpath, repo_fingerprint)

        idx_sha256 = None
        with zipfile.ZipFile(jarpath, "r") as zf:
            with zf.open("entry.json") as e:
                idx_sha256 = json.load(e).get("index", {}).get("sha256")

        if not idx_sha256:
            raise Exception("sha256 checksum missing in entry.jar")

        idxpath = pathlib.Path(tmpdir) / "index-v2.json"
        urllib.request.urlretrieve(repo_url.rstrip("/") + "/index-v2.json", idxpath)
        dl_idx_sha256 = _sha256_of_file(idxpath)
        if not idx_sha256 == dl_idx_sha256:
            raise Exception(
                f"expected index-v2.json checksum according entry.jar: '{idx_sha256}' missmatched with downloaded index-v2.json checksum: '{dl_idx_sha256}'"
            )

        with open(idxpath, "r") as f:
            return indexv2.IndexV2.from_dict(json.load(f))


# idx = fetch_index_v2(
#     # "https://guardianproject.info/fdroid/repo",
#     # "b7c2eefd8dac7806af67dfcd92eb18126bc08312a7f2d6f3862e46013c7a6135",
#     "https://f-droid.org/repo",
#     "43238D512C1E5EB2D6569F4A3AFBF5523418B82E0A3ED1552770ABB9A9C9CCAB",
# )
# print(json.dumps(idx.to_dict(), indent=2))
