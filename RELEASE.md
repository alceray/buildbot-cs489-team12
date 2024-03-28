# Creating a Release (improved version)

This document is documentation intended for Buildbot maintainers with write access.
It documents the release process of Buildbot.

Note: This adapts and automates the release process in [RELEASING.rst](./RELEASING.rst) with GitHub workflows. The results should generally be the same.

## Step 1: Verify that external dependants can be built

Identical to the original step 1. Since this requires manual verification, it is not relevant to the automation improvements and can be skipped.

## Step 2: Release notes PR

Manually dispatch the `Generate Release Notes` workflow under Actions. Pass a new release version `x.y.z` (eg. 3.13.1) as input. This creates a PR titled `Release Notes for Version <x.y.z>` with a commit on a new branch called `release-notes-<x.y.z>`.

## Step 3: Merge release notes PR

(Optional) Check the changes in `master/docs/relnotes/index.rst` for obvious rendering errors. Check `newsfragments/` for any ignored release notes.

Merge the PR created in step 2.

## Step 4: Perform release

The merge in step 3 triggers the `Perform Release` workflow. This creates the tag `v<x.y.z>`, generates documentation, copies it to bbodcs repo, pushes all the changes. 

The following jobs will make tarballs and upload them in a draft release to GitHub Releases. 

## Step 5: Publish release

(Optional) Manually add the release notes to the draft release.

Configure the email settings in `.github/email_config.json` so that step 7 sends to the desired email addresses. 

Publish the release.

## Step 6: Upload release to (Test)PyPI

Publishing the release in step 5 triggers the `Publish Release` workflow, which (tries to) download the release assets and upload them to TestPyPI.

## Step 7: Announce release

While step 6 runs, the same workflow also sends an announcement to the mailing lists specified in `.github/email_config.json`, with the contributors to this release included.

Note: The only steps that require manual action are steps 2, 3, and 5.