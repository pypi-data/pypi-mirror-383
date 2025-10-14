# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Wrapper for running java 'keytool' CLI commands."""

import os
import shutil
import datetime
import subprocess


def verify_jar(jarpath, fingerprint):
    """Check if a jar file is signed by a cert with given fingerprint."""
    keytool_output = printcert_jar(jarpath)
    cert_fingerprints = [
        cert["SHA256"].lower()
        for signer in keytool_output.values()
        for cert in signer.values()
    ]
    if not any([fp == fingerprint.lower() for fp in cert_fingerprints]):
        raise Exception(
            f"fingerprint {fingerprint.lower()} not in certificate! (jar certificate contains these fingerprints: {' '.join(cert_fingerprints)})"
        )


def printcert_jar(jar_file):
    """Run 'keytool -printcert -jar' and parse output into dict."""
    if not shutil.which("keytool"):
        raise Exception(
            "error: `keytool` not found (e.g. install with `apt install openjdk-17-jre-headless`)"
        )
    cmd = ["keytool", "-printcert", "-jarfile", jar_file]
    env = os.environ.copy().update({"LANG": "C.UTF-8"})
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    if result.returncode:
        print(result.stderr)
        raise Exception(f"error: keytool could not verify '{jar_file}'")

    return _parse_keytool_output(result.stdout)


def _parse_keytool_output(keytool_output):
    r = {}
    current_signer = None
    current_cert = None
    for line in keytool_output.splitlines():
        line = line.strip()
        if line.startswith("Signer #"):
            current_signer = line.rstrip(":")
            r[current_signer] = {}
        elif line.startswith("Certificate #"):
            current_cert = line.rstrip(":")
            r[current_signer][current_cert] = {}
        elif line.startswith("Owner: "):
            r[current_signer][current_cert]["Owner"] = dict(
                [x.split("=") for x in line[7:].split(", ")]
            )
        elif line.startswith("Issuer: "):
            r[current_signer][current_cert]["Issuer"] = dict(
                [x.split("=") for x in line[8:].split(", ")]
            )
        elif line.startswith("Serial number: "):
            r[current_signer][current_cert]["Serial number"] = line[15:]
        elif line.startswith("Valid from: "):
            t = line[12:].split(" until: ")
            r[current_signer][current_cert]["Valid from"] = datetime.datetime.strptime(
                t[0], "%a %b %d %H:%M:%S %Z %Y"
            )
            r[current_signer][current_cert]["Valid until"] = datetime.datetime.strptime(
                t[1], "%a %b %d %H:%M:%S %Z %Y"
            )
        elif line.startswith("SHA1: "):
            r[current_signer][current_cert]["SHA1"] = line[6:].replace(":", "")
        elif line.startswith("SHA256: "):
            r[current_signer][current_cert]["SHA256"] = line[8:].replace(":", "")
        elif line.startswith("Signature algorithm name: "):
            r[current_signer][current_cert]["Signature algorithm name"] = line[26:]
        elif line.startswith("Subject Public Key Algorithm: "):
            r[current_signer][current_cert]["Subject Public Key Algorithm"] = line[30:]
        elif line.startswith("Version: "):
            r[current_signer][current_cert]["Version"] = line[9:]
    return r
