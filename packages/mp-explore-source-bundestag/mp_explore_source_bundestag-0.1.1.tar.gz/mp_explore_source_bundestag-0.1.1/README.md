<!--
SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# MP Explore Bundestag

Part of the [MP Explore](https://git.fsfe.org/mp-explore/mp-explore) project.

Data Source for the Bundestag.

## Where to get it

You can get it through the [Python Package Index (PyPI)](https://pypi.org/project/mp_explore_core/):

```sh
$ pip3 install mp_explore_source_bundestag
```

## Arguments

- (Optional) `display_browser` When enabled, a browser window is opened displaying the actions being performed.
- (Optional) `skip_retired` Skip members who are retired, deceased, or refused mandate.
- (Optional) `url` URL from where the data is extracted.
- (Optional) `infer_email` When enabled, e-mails are inferred based on the pattern they typically follow.
- (Optional) `check_cdu_csu` Obtain e-mails and check information with CDU/CSU sources.
- (Optional) `cdu_csu_url` The URL where the data will be extracted from.
- (Optional) `check_grune` Obtain e-mails and check information with  Bündnis 90/Die Grünen sources.
- (Optional) `grune_url` The URL where the data will be extracted from.
- (Optional) `check_spd` Obtain e-mails and check information with SPD sources.
- (Optional) `spd_url` The URL where the data will be extracted from.