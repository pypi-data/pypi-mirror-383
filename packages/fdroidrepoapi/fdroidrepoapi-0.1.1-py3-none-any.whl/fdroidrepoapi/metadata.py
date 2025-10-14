# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: AGPL-3.0-or-later


from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, List


"""F-Droid YAML-Metadata dataclasses and parers."""


def _optput(d, key, val):
    """Put values into dicts only if value is not None/empty."""
    if val:
        d[key] = val


@dataclass
class Build:
    version_name: str = ""
    version_code: int = 0
    disable: Optional[str] = None
    commit: str = ""
    timeout: Optional[int] = None
    subdir: Optional[str] = None
    submodules: bool = False
    sudo: List[str] = field(default_factory=list)
    init: List[str] = field(default_factory=list)
    patch: List[str] = field(default_factory=list)
    gradle: List[str] = field(default_factory=list)
    maven: Optional[str] = None
    output: Optional[str] = None
    binary: Optional[str] = None
    srclibs: List[str] = field(default_factory=list)
    oldsdkloc: bool = False
    encoding: Optional[str] = None
    forceversion: bool = False
    forcevercode: bool = False
    rm: List[str] = field(default_factory=list)
    extlibs: List[str] = field(default_factory=list)
    prebuild: List[str] = field(default_factory=list)
    androidupdate: List[str] = field(default_factory=list)
    target: Optional[str] = None
    scanignore: List[str] = field(default_factory=list)
    scandelete: List[str] = field(default_factory=list)
    build: List[str] = field(default_factory=list)
    buildjni: List[str] = field(default_factory=list)
    ndk: Optional[str] = None
    preassemble: List[str] = field(default_factory=list)
    gradleprops: List[str] = field(default_factory=list)
    antcommands: List[str] = field(default_factory=list)
    postbuild: List[str] = field(default_factory=list)
    novcheck: bool = False
    antifeatures: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        d: Dict = {
            "versionName": self.version_name,
            "versionCode": self.version_code,
            "commit": self.commit,
        }
        _optput(d, "disable", self.disable)
        _optput(d, "timeout", self.timeout)
        _optput(d, "subdir", self.subdir)
        _optput(d, "submodules", self.submodules)
        _optput(d, "sudo", self.sudo)
        _optput(d, "init", self.init)
        _optput(d, "patch", self.patch)
        _optput(d, "gradle", self.gradle)
        _optput(d, "maven", self.maven)
        _optput(d, "output", self.output)
        _optput(d, "binary", self.binary)
        _optput(d, "srclibs", self.srclibs)
        _optput(d, "oldsdkloc", self.oldsdkloc)
        _optput(d, "encoding", self.encoding)
        _optput(d, "forceversion", self.forceversion)
        _optput(d, "forcevercode", self.forcevercode)
        _optput(d, "rm", self.rm)
        _optput(d, "extlibs", self.extlibs)
        _optput(d, "prebuild", self.prebuild)
        _optput(d, "androidupdate", self.androidupdate)
        _optput(d, "target", self.target)
        _optput(d, "scanignore", self.scanignore)
        _optput(d, "scandelete", self.scandelete)
        _optput(d, "build", self.build)
        _optput(d, "buildjni", self.buildjni)
        _optput(d, "ndk", self.ndk)
        _optput(d, "preassemble", self.preassemble)
        _optput(d, "gradleprops", self.gradleprops)
        _optput(d, "antcommands", self.antcommands)
        _optput(d, "postbuild", self.postbuild)
        _optput(d, "novcheck", self.novcheck)
        _optput(d, "antifeatures", self.antifeatures)
        return d

    @staticmethod
    def from_dict(d) -> "Build":
        return Build(
            version_name=d["versionName"],
            version_code=d["versionCode"],
            commit=d["commit"],
            disable=d.get("disable"),
            timeout=d.get("timeout"),
            subdir=d.get("subdir"),
            submodules=d.get("submodules"),
            sudo=d.get("sudo"),
            init=d.get("init"),
            patch=d.get("patch"),
            gradle=d.get("gradle"),
            maven=d.get("maven"),
            output=d.get("output"),
            binary=d.get("binary"),
            srclibs=d.get("srclibs"),
            oldsdkloc=d.get("oldsdkloc"),
            encoding=d.get("encoding"),
            forceversion=d.get("forceversion"),
            forcevercode=d.get("forcevercode"),
            rm=d.get("rm"),
            extlibs=d.get("extlibs"),
            prebuild=d.get("prebuild"),
            androidupdate=d.get("androidupdate"),
            target=d.get("target"),
            scanignore=d.get("scanignore"),
            scandelete=d.get("scandelete"),
            build=d.get("build"),
            buildjni=d.get("buildjni"),
            ndk=d.get("ndk"),
            preassemble=d.get("preassemble"),
            gradleprops=d.get("gradleprops"),
            antcommands=d.get("antcommands"),
            postbuild=d.get("postbuild"),
            novcheck=d.get("novcheck"),
            antifeatures=d.get("antifeatures"),
        )


@dataclass
class Metadata:
    disabled: Optional[bool] = None
    anti_features: Dict[str, str] = field(default_factory=dict)
    # Provides = None  # deprecated, so we're just ignoring it here
    categories: List[str] = field(default_factory=list)
    license: str = field(default_factory="Unknown")
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    author_website: Optional[str] = None
    website: Optional[str] = None
    source_code: Optional[str] = None
    issue_tracker: Optional[str] = None
    translation: Optional[str] = None
    changelog: Optional[str] = None
    donate: Optional[str] = None
    liberapay: Optional[str] = None
    open_collective: Optional[str] = None
    bitcoin: Optional[str] = None
    litecoin: Optional[str] = None
    name: Optional[str] = None
    auto_name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    requires_root: bool = False
    repo_type: Optional[str] = None
    repo: Optional[str] = None
    binaries: Optional[str] = None
    builds: List[Build] = field(default_factory=list)
    allowed_apk_signing_keys: Optional[str] = None
    maintainer_notes: Optional[str] = None
    archive_policy: Optional[str] = None
    auto_update_mode: Optional[str] = None
    update_check_mode: Optional[str] = None
    update_check_ignore: Optional[str] = None
    vercode_operation: List[str] = field(default_factory=list)
    update_check_name: Optional[str] = None
    update_check_data: Optional[str] = None
    current_version: Optional[str] = None
    current_version_code: Optional[str] = None
    no_source_since: Optional[str] = None

    @staticmethod
    def from_dict(d) -> "Metadata":
        """Wrap data from a dictionary into a new Metadata object."""
        anti_features = {}
        if "AntiFeatures" in d:
            if isinstance(d["AntiFeatures"], list):
                anti_features.update(dict([(i, None) for i in d["AntiFeatures"]]))
            else:
                anti_features = d["AntiFeatures"]
        return Metadata(
            disabled=d.get("Disabled"),
            anti_features=anti_features,
            categories=d.get("Categories", []),
            license=d.get("License", "Unknown"),
            author_name=d.get("AuthorName"),
            author_email=d.get("AuthorEmail"),
            author_website=d.get("AuthorWebSite"),
            website=d.get("WebSite"),
            source_code=d.get("SourceCode"),
            issue_tracker=d.get("IssueTracker"),
            translation=d.get("Translation"),
            changelog=d.get("Changelog"),
            donate=d.get("Donate"),
            liberapay=d.get("Liberapay"),
            open_collective=d.get("OpenCollective"),
            bitcoin=d.get("Bitcoin"),
            litecoin=d.get("Litecoin"),
            name=d.get("Name"),
            auto_name=d.get("AutoName"),
            summary=d.get("Summary"),
            description=d.get("Description"),
            requires_root=d.get("RequiresRoot", False),
            repo_type=d.get("RepoType"),
            repo=d.get("Repo"),
            binaries=d.get("Binaries"),
            builds=[Build.from_dict(x) for x in d.get("Builds", [])],
            allowed_apk_signing_keys=d.get("AllowedAPKSigningKeys"),
            maintainer_notes=d.get("MaintainerNotes"),
            archive_policy=d.get("ArchivePolicy"),
            auto_update_mode=d.get("AutoUpdateMode"),
            update_check_mode=d.get("UpdateCheckMode"),
            update_check_ignore=d.get("UpdateCheckIgnore"),
            vercode_operation=d.get("VercodeOperation", []),
            update_check_name=d.get("UpdateCheckName"),
            update_check_data=d.get("UpdateCheckData"),
            current_version=d.get("CurrentVersion"),
            current_version_code=d.get("CurrentVersionCode"),
            no_source_since=d.get("NoSourceSince"),
        )

    def to_dict(self) -> Dict:
        d: Dict = {}
        _optput(d, "Disabled", self.disabled)
        _optput(d, "AntiFeatures", self.anti_features)
        _optput(d, "Categories", self.categories)
        _optput(d, "License", self.license),
        _optput(d, "AuthorName", self.author_name)
        _optput(d, "AuthorEmail", self.author_email)
        _optput(d, "AuthorWebSite", self.author_website)
        _optput(d, "WebSite", self.website)
        _optput(d, "SourceCode", self.source_code)
        _optput(d, "IssueTracker", self.issue_tracker)
        _optput(d, "Translation", self.translation)
        _optput(d, "Changelog", self.changelog)
        _optput(d, "Donate", self.donate)
        _optput(d, "Liberapay", self.liberapay)
        _optput(d, "OpenCollective", self.open_collective)
        _optput(d, "Bitcoin", self.bitcoin)
        _optput(d, "Litecoin", self.litecoin)
        _optput(d, "Name", self.name)
        _optput(d, "AutoName", self.auto_name)
        _optput(d, "Summary", self.summary)
        _optput(d, "Description", self.description)
        _optput(d, "RequiresRoot", self.requires_root)
        _optput(d, "RepoType", self.repo_type)
        _optput(d, "Repo", self.repo)
        _optput(d, "Binaries", self.binaries)
        _optput(d, "Builds", [x.to_dict() for x in self.builds])
        _optput(d, "AllowedAPKSigningKeys", self.allowed_apk_signing_keys)
        _optput(d, "MaintainerNotes", self.maintainer_notes)
        _optput(d, "ArchivePolicy", self.archive_policy)
        _optput(d, "AutoUpdateMode", self.auto_update_mode)
        _optput(d, "UpdateCheckMode", self.update_check_mode)
        _optput(d, "UpdateCheckIgnore", self.update_check_ignore)
        _optput(d, "VercodeOperation", self.vercode_operation),
        _optput(d, "UpdateCheckName", self.update_check_name),
        _optput(d, "UpdateCheckData", self.update_check_data),
        _optput(d, "CurrentVersion", self.current_version),
        _optput(d, "CurrentVersionCode", self.current_version_code),
        _optput(d, "NoSourceSince", self.no_source_since),
        return d
