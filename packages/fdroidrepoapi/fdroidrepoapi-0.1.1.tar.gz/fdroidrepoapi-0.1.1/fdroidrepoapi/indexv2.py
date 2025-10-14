# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""F-Droid IndexV2 API dataclasses and parsers.

typical usage: IndexV2.from_dict(json.load(...))
"""

from typing import Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime


T = TypeVar("T")


@dataclass
class Translated(Generic[T]):
    """Hold translated data of any type, by locale string."""

    translations: Dict[str, T]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            k: v.to_dict() if hasattr(v, "to_dict") else v
            for k, v in self.translations.items()
        }

    @staticmethod
    def from_dict(d: Dict[str, T]) -> "Translated[T]":
        """Wrap data from a dictionary into a instance of Translated."""
        return Translated(translations=d)

    def __getitem__(self, locale: str) -> T:
        """Retrieve translated value."""
        return self.translations[locale]

    def __setitem__(self, locale: str, value: T):
        """Set translated value."""
        self.translations[locale] = value

    def get(self, locale: str) -> Optional[T]:
        """Retrieve translated value.

        This function also searched for lose translations matches by gardually
        relaxing matching rules.
        """
        nlocale = locale.lower().replace("_", "-")
        nlocalemap = {
            loc.lower().replace("_", "-"): loc for loc in self.translations.keys()
        }
        if nlocale in nlocalemap:
            # case insensitive exact match: 'en_US' == 'en-us'
            return self.translations.get(nlocalemap[nlocale])
        slocale = nlocale.split("-")[0]
        if slocale in nlocalemap:
            # abbreviated match: 'en' == 'en-US'
            return self.translations[nlocalemap[slocale]]
        slocalemap = {loc.split("-")[0]: o for loc, o in nlocalemap.items()}
        if slocale in slocalemap:
            # reverse abbreviated match: 'en-US' == 'en', 'en-US' == 'en_GB'
            return self.translations[slocalemap[slocale]]
        return None

        # trimnlocalemap = {l: l.slipt()}
        # if nlocale in nlocalemap.values():
        #     return self.translations[nlocalemap[]]
        # return self.translations[locale] if locale in self.translations else None


@dataclass
class File:
    """Infos about a file in the repository."""

    name: Optional[str]
    sha256: Optional[str]
    size: Optional[int]
    ipfs_CIDv1: Optional[str]

    @staticmethod
    def from_dict(d) -> Optional["File"]:
        """Wrap data from a dictionary into a new File object."""
        return (
            File(
                name=d.get("name"),
                sha256=d.get("sha256"),
                size=int(d.get("size", 0)),
                ipfs_CIDv1=d.get("ipfsCIDv1"),
            )
            if d
            else None
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d: Dict = {}
        if self.name is not None:
            d["name"] = self.name
        if self.sha256 is not None:
            d["sha256"] = self.sha256
        if self.size is not None:
            d["size"] = self.size
        if self.ipfs_CIDv1 is not None:
            d["ipfsCIDv1"] = self.ipfs_CIDv1
        return d


@dataclass
class Mirror:
    """List of official mirror web addresses for a repo."""

    is_primary: Optional[bool]
    url: Optional[str]
    country_code: Optional[str]

    @staticmethod
    def from_dict(d) -> Optional["Mirror"]:
        """Wrap data from a dictionary into a new Mirror object."""
        return (
            Mirror(
                is_primary=bool(d.get("isPrimary")) if "isPrimary" in d else None,
                url=str(d.get("url")),
                country_code=d.get("countryCode"),
            )
            if d
            else None
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d: Dict = {}
        if self.is_primary is not None:
            d["isPrimary"] = self.is_primary
        if self.url is not None:
            d["url"] = self.url
        if self.country_code is not None:
            d["countryCode"] = self.country_code
        return d


@dataclass
class Category:
    """Classification-categories for apps in a repo."""

    icon: Optional[Translated[File]]
    name: Optional[Translated[str]]

    @staticmethod
    def from_dict(d) -> Optional["Category"]:
        """Wrap data from a dictionary into a new Category object."""
        icons_raw: Dict[str, Optional[File]] = {
            k: File.from_dict(v) for k, v in d.get("icon", {}).items()
        }
        icons: Dict[str, File] = {k: v for k, v in icons_raw.items() if v is not None}
        return (
            Category(
                name=Translated.from_dict(d.get("name", {})),
                icon=Translated.from_dict(icons),
            )
            if d
            else None
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        d = {}
        if self.icon:
            d["icon"] = self.icon.to_dict()
        if self.name:
            d["name"] = self.name.to_dict()
        return d


@dataclass
class ReleaseChannel:
    """Release channels for apps in a repo.

    e.g. a repo can provide beta releases in a separate release channel.
    """

    description: Dict[str, str]
    name: Dict[str, str]

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Category object."""
        return ReleaseChannel(
            description=d.get("description", {}),
            name=d.get("name", {}),
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d: Dict = {}
        if self.name:
            d["name"] = {}
            for k, v in self.name.items():
                self.name
        return d


@dataclass
class AntiFeature:
    """Anti-Feature annotations for apps in a repo."""

    name: Translated[str]
    description: Translated[str]
    icon: Translated[File]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name.to_dict(),
            "description": self.description.to_dict(),
            "icon": self.icon.to_dict(),
        }

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Category object."""
        return AntiFeature(
            name=Translated.from_dict(d.get("name", {})),
            description=Translated.from_dict(d.get("description", {})),
            icon=Translated.from_dict(
                {k: File.from_dict(v) for k, v in d.get("icon", {}).items()}
            ),
        )


@dataclass
class Repo:
    """General informations about a repository."""

    name: Translated[str]
    description: Translated[str]
    icon: Translated[File]
    address: str
    mirrors: List[Mirror]
    web_base_url: str
    timestamp: datetime
    categories: Dict[str, Category]
    release_channels: Optional[Dict[str, ReleaseChannel]]
    anti_features: Dict[str, AntiFeature]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = {
            "name": self.name.to_dict(),
            "description": self.description.to_dict(),
            "icon": self.icon.to_dict(),
            "address": self.address,
            "mirrors": [m.to_dict() for m in self.mirrors],
            "webBaseUrl": self.web_base_url,
            "timestamp": int(self.timestamp.timestamp() * 1000),
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "antiFeatures": {k: v.to_dict() for k, v in self.anti_features.items()},
        }
        if self.release_channels is not None:
            d["releaseChannels"] = {
                k: v.to_dict() for k, v in self.release_channels.items()
            }
        return d

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Category object."""
        return (
            Repo(
                name=Translated(d.get("name", {})),
                description=Translated(d.get("description", {})),
                icon=Translated(
                    {k: File.from_dict(v) for k, v in d.get("icon", {}).items()}
                ),
                address=d.get("address"),
                mirrors=[Mirror.from_dict(x) for x in d.get("mirrors", [])],
                web_base_url=d.get("webBaseUrl"),
                timestamp=datetime.fromtimestamp(d.get("timestamp", 0) / 1000.0),
                categories={
                    k: Category.from_dict(v) for k, v in d.get("categories", {}).items()
                },
                release_channels={
                    k: ReleaseChannel.from_dict(v)
                    for k, v in d.get("releaseChannels", {}).items()
                }
                if "releaseChannels" in d
                else None,
                anti_features={
                    k: AntiFeature.from_dict(v)
                    for k, v in d.get("antiFeatures", {}).items()
                },
            )
            if d
            else None
        )


@dataclass
class Metadata:
    """Gernal infos about a specific app or package."""

    added: datetime
    categories: List[str]
    issue_tracker: str
    last_updated: datetime
    license: Optional[str]
    source_code: str
    translation: str
    website: str
    feature_graphic: Translated[File]
    screenshots: Dict[str, Translated[List[File]]]
    name: Translated[str]
    summary: Translated[str]
    description: Translated[str]
    icon: Translated[File]
    preferred_signer: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = {
            "categories": [x for x in self.categories],
            "issueTracker": self.issue_tracker,
            "lastUpdated": int(self.last_updated.timestamp() * 1000),
            "sourceCode": self.source_code,
            "translation": self.translation,
            "website": self.website,
            "featureGraphic": {
                k: v.to_dict() for k, v in self.feature_graphic.translations.items()
            },
            "icon": self.icon.to_dict(),
            "screenshots": {
                shot_k: {
                    k: [t.to_dict() for t in v] for k, v in shot_v.translations.items()
                }
                for shot_k, shot_v in self.screenshots.items()
                if shot_v
            },
            "name": self.name.to_dict(),
            "summary": self.summary.to_dict(),
            "description": self.description.to_dict(),
            "preferredSigner": self.preferred_signer,
        }
        if self.added:
            d["added"] = int(self.added.timestamp() * 1000)
        if self.license:
            d["license"] = self.license
        return d

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Metadata object."""
        return Metadata(
            added=datetime.fromtimestamp(d.get("added", 0) / 1000.0),
            categories=d.get("categories", []),
            issue_tracker=d.get("issueTracker"),
            last_updated=datetime.fromtimestamp(d.get("lastUpdated", 0) / 1000.0),
            license=d.get("license"),
            source_code=d.get("sourceCode"),
            translation=d.get("translation"),
            website=d.get("website"),
            feature_graphic=Translated(
                {k: File.from_dict(v) for k, v in d.get("featureGraphic", {}).items()}
            ),
            screenshots={
                # shot_k: e.g. 'phone'
                shot_k: Translated.from_dict(
                    {
                        # loc_k: e.g. 'en-US'
                        loc_k: [File.from_dict(x) for x in loc_v]
                        for loc_k, loc_v in shot_v.items()
                    }
                )
                for shot_k, shot_v in d.get("screenshots", {}).items()
            },
            name=Translated.from_dict(d.get("name", {})),
            summary=Translated.from_dict(d.get("summary", {})),
            description=Translated.from_dict(d.get("description", {})),
            icon=Translated.from_dict(
                {k: File.from_dict(v) for k, v in d.get("icon", {}).items()}
            ),
            preferred_signer=d.get("preferredSigner"),
        )


@dataclass
class UsesPermission:
    """Android Permission identifiers, apps can request from the OS."""

    name: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
        }

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new UsesPermission object."""
        return UsesPermission(
            name=str(d.get("name")),
        )


@dataclass
class UsesSdk:
    """Android compatibility information."""

    min_sdk_version: int
    target_sdk_version: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "minSdkVersion": self.min_sdk_version,
            "targetSdkVersion": self.target_sdk_version,
        }

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new UsesSdk object."""
        return (
            UsesSdk(
                min_sdk_version=int(d.get("minSdkVersion", 0)),
                target_sdk_version=int(d.get("targetSdkVersion", 0)),
            )
            if d
            else None
        )


@dataclass
class Signer:
    """List of signing key fingerprints for this app."""

    sha256: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "sha256": [x for x in self.sha256],
        }

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Signer object."""
        return Signer(sha256=[str(x) for x in d.get("sha256", [])]) if d else None


@dataclass
class Manifest:
    """General infos about a specific version of an app."""

    version_name: str
    version_code: int
    uses_sdk: Optional[UsesSdk]
    signer: Optional[Signer]
    uses_permission: List[UsesPermission]
    nativecode: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = {
            "versionName": self.version_name,
            "versionCode": self.version_code,
            "usesPermission": [x.to_dict() for x in self.uses_permission],
            "nativecode": [x for x in self.nativecode],
        }
        if self.uses_sdk:
            d["usesSdk"] = self.uses_sdk.to_dict()
        if self.signer:
            d["signer"] = self.signer.to_dict()
        return d

    @staticmethod
    def from_dict(d):
        """Wrap data from a dictionary into a new Manifest object."""
        return Manifest(
            version_name=str(d.get("versionName")),
            version_code=int(d.get("versionCode", 0)),
            uses_sdk=UsesSdk.from_dict(d.get("usesSdk")),
            signer=Signer.from_dict(d.get("signer")),
            uses_permission=[
                UsesPermission.from_dict(p) for p in d.get("usesPermission", [])
            ],
            nativecode=d.get("nativecode", []),
        )


@dataclass
class Version:
    """Infos about a individual version of an app."""

    added: datetime
    file: Optional[File]
    src: Optional[File]
    manifest: Manifest
    whats_new: Translated[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = {
            "manifest": self.manifest.to_dict(),
            "added": int(self.added.timestamp() * 1000),
            "whatsNew": self.whats_new.to_dict(),
        }
        if self.file is not None:
            d["file"] = self.file.to_dict()
        if self.src is not None:
            d["src"] = self.src.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict):
        """Wrap data from a dictionary into a new Version object."""
        return Version(
            added=datetime.fromtimestamp(d.get("added", 0) / 1000.0),
            file=File.from_dict(d.get("file")),
            src=File.from_dict(d.get("src")),
            manifest=Manifest.from_dict(d.get("manifest")),
            whats_new=Translated.from_dict(d.get("whatsNew", {})),
        )


@dataclass
class Package:
    """Infos about a Package in the repo.

    Usually a package is an app.
    """

    metadata: Metadata
    versions: Dict[str, Version]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "versions": {k: v.to_dict() for k, v in self.versions.items()},
        }

    @staticmethod
    def from_dict(d: Dict):
        """Wrap data from a dictionary into a new Package object."""
        return Package(
            metadata=Metadata.from_dict(d.get("metadata")),
            versions={
                k: Version.from_dict(v) for k, v in d.get("versions", {}).items()
            },
        )


@dataclass
class IndexV2:
    """F-Droid V2 Index.

    Data in and F-Droid V2 index holds 2 kinds of data. General information
    about the repository and a list of packages stored in a repository.
    """

    repo: Repo
    packages: Dict[str, Package]

    @staticmethod
    def from_dict(d: Dict):
        """Wrap data from a dictionary into a new IndexV2 object."""
        return IndexV2(
            repo=Repo.from_dict(d.get("repo")),
            packages={
                k: Package.from_dict(v) for k, v in d.get("packages", {}).items()
            },
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "repo": self.repo.to_dict(),
            "packages": {k: v.to_dict() for k, v in self.packages.items()},
        }
