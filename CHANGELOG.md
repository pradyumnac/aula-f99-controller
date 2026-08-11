# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Initial project scaffold (mise + uv + pyproject.toml).
- Sinowealth wireless protocol port: model query, solid-color control.
- `aula-f99` CLI (`color`, `model` subcommands).

### Known issues

- Wired-mode (`VID_258A:PID_010C`, usage page `0xff00`) writes fail — report
  structure differs from the wireless dongle's and hasn't been captured yet.
- Per-key RGB, lighting effects, brightness/speed, and macro programming are
  not yet implemented.
