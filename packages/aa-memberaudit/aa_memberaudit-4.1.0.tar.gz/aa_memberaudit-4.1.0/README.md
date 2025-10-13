# Member Audit

An Alliance Auth app that provides full access to Eve characters and related reports for auditing, vetting and monitoring.

[![release](https://img.shields.io/pypi/v/aa-memberaudit?label=release)](https://pypi.org/project/aa-memberaudit/)
[![python](https://img.shields.io/pypi/pyversions/aa-memberaudit)](https://pypi.org/project/aa-memberaudit/)
[![django](https://img.shields.io/pypi/djversions/aa-memberaudit?label=django)](https://pypi.org/project/aa-memberaudit/)
[![pipeline](https://gitlab.com/ErikKalkoken/aa-memberaudit/badges/master/pipeline.svg)](https://gitlab.com/ErikKalkoken/aa-memberaudit/-/pipelines)
[![codecov](https://codecov.io/gl/ErikKalkoken/aa-memberaudit/branch/master/graph/badge.svg?token=QHMCUAFZBV)](https://codecov.io/gl/ErikKalkoken/aa-memberaudit)
[![Documentation Status](https://readthedocs.org/projects/aa-memberaudit/badge/?version=latest)](https://aa-memberaudit.readthedocs.io/en/stable/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://gitlab.com/ErikKalkoken/aa-memberaudit/-/blob/master/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![chat](https://img.shields.io/discord/790364535294132234)](https://discord.gg/zmh52wnfvM)

## Contents

- [Overview](#overview)
- [Features](#features)
- [Highlights](#highlights)
- [Documentation](#documentation)

## Overview

Member Audit is an Alliance Auth app that provides full access to Eve characters and related reports.

Users can monitor their characters, recruiters can vet the characters of applicants and leadership can audit the characters of their members to ensure compliance and find spies.

In addition character based reports gives leadership another valuable tool for managing their respective organization.

## Features

Member Audit adds the following features to Auth:

- Users can see an overview of all their characters with key information like their current location and wallet balance
- Users can get full access to their characters to monitor them without having to open the Eve client (similar to the classic Eve ap "EveMon").
- Applicants can temporarily share their characters with recruiters for vetting
- Leadership can get full access to characters of their members for auditing (e.g. to check suspicious members)
- Full access to characters currently includes the following information:
  - Assets
  - Bio
  - Contacts
  - Contracts
  - Corporation history
  - Corporation roles (NEW)
  - Faction Warfare statistics
  - Implants
  - Jump clones
  - Mails
  - Mining ledger
  - Loyalty points
  - Skill queue
  - Skill sets
  - Skills
  - Wallet (journal and transactions)

- Leadership can define Skill Sets, which are a way of defining skills needed to perform a specific activity or fly a doctrine ship. They allow recruiters and leadership to see at a glance what a character can do (e.g. which doctrine ships he/she can fly)
- Skill Sets can be generated from imported fittings
- Leadership can see reports and analytics about their members. Those currently include:
  - Compliance: if users have added all their characters
  - Skill Sets: which character has which skill sets

- Admins can use the flexible permission system to grant access levels for different roles (e.g. corp leadership may only have access to reports about their own corp members)
- Admins can customize and configure Member Audit to fit their needs. e.g. change the app's name and define how often which type of data is updated from the Eve server

- Ensure that only users who have registered all their characters have access to services (see also [Compliance Groups](https://aa-memberaudit.readthedocs.io/en/stable/user.html#compliance-groups))
- Get notifications when a user removes a character that they had previously registered.
- Designed to work efficiently with large number of characters
- Data retention policy allows managing storage capacity needs
- Data can be exported for processing it with third party apps like Google Sheets (currently wallet journal only)
- Language support for Chinese :cn:, English :us:, German :de:, Russian :ru: and Ukrainian 🇺🇦

A few noteworthy community apps that are build on Member Audit:

- [aa-ma-securegroups](https://apps.allianceauth.org/apps/detail/aa-ma-securegroups): Secure Groups integration with Member Audit
- [Inactivity](https://apps.allianceauth.org/apps/detail/aa-inactivity): Activity monitoring app
- [Mail Relay](https://apps.allianceauth.org/apps/detail/aa-mailrelay): An app for relaying Eve mails to Discord

See [here](https://apps.allianceauth.org/apps/detail/aa-memberaudit) for a full list of community apps that use Member Audit.

## Highlights

### Character Launcher

The main page for users to register their characters and get a key infos of all registered characters.

![launcher](https://i.imgur.com/v9AU3Gr.jpg)

### Character Viewer

The page for displaying all details about a character.

![viewer](https://i.imgur.com/vo1N3kg.jpg)

### Skill Sets

Skill sets are a way of defining both required and recommended skills for a specific activity or ship.

This tab on the character view allows you to view what skill sets a character has. For skill sets they don't have or are missing parts of, it also shows what skills are missing.

![skill-plans](https://i.imgur.com/cKNy5vz.png)

Requirements can be customized per skill set in the administration panel. Recommended skill levels can be added in addition to requirements.

![skill-set-admin](https://i.imgur.com/ef2cCd9.png)

### Character Finder

On this page recruiters and leadership can look for other characters to view (assuming they have been given permission).

![finder](https://i.imgur.com/4sDnBcz.png)

## Documentation

Link to [documentation](https://aa-memberaudit.readthedocs.io/en/stable/).
