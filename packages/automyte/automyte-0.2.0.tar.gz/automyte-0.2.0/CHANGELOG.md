# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] 2025-10-10

### Added

 - v0.2.0 Add support for argv as config overrides (5c55eda)
 - v0.2.0 Set AUTOMYTE_CLI_MODE flag when called as automyte cli (3836ff2)
 - v0.2.0 Add feature to create new file in tasks (af2f028)
 - v0.2.0 Add support for setting config via environment variables (980aa33)
 - v0.2.0 Setup basic CI/CD pipeline with tests (c9d4038)
 - v0.2.0 Add support for .cfg file as config overrides (a88205b)
 - v0.2.0 Add support for parsing config fields through command line (ba93b1d)

### Changed

 - v0.2.0 Refactor config setup (b42241d)
 - v0.2.0 Shift supported python by +1 (497a827)
 - v0.2.0 Move main cli to root folder (7a51b07)

### Removed

 - v0.2.0 Remove config_overrides in automaton.run (7e62b36)

## [0.1.13] 2025-04-06

### Added

- v0.1.13 Add setup & validation phase to automaton (fc7dcb3)
- v0.1.13 Add separate config file for pyright (0bf7025)

### Changed

- v0.1.13 Shift supported python by +1 (497a827)
- v0.1.13 Move main cli to root folder (7a51b07)

### Fixed

- v0.1.13 Fix tests (3868a99)

## [0.1.12] 2025-03-13

### Added

- v0.1.12 Add IgnoreResult flow tasks (5ce60d2)

### Changed

- v0.1.12 Combine RunIf and RunOn conditionals into one flow.If (0ed11d4)
- v0.1.12 Set all vcs tasks to fail if bash.execute fails (8934250)
- v0.1.12 Use mixin for adding .flags functionality to vcs tasks (a2010fa)

### Fixed

- v0.1.12 Generate default random project_id if it is not passed (df966a8)

## [0.1.11] 2025-03-11

### Added

- v0.1.11 Add PathFilter for filtering files by folder or name (90772c3)

### Changed

- v0.1.11 Add validation for project dirs + allow passing "~/" (bde4649)

## [0.1.10] 2025-03-11

### Changed

- v0.1.10 Allow passing plain folder URIs to projects section for automaton (27551b9)

## [0.1.9] 2025-03-11

### Added

- v0.1.9 Add `ignorable_locations` to local files explorer (3d9511e)
- v0.1.9 Add initial simplest example test (5e444ae)
- v0.1.9 Add `fs.flush()` util task (811e0b8)

## [0.1.8] 2025-03-07

### Changed

- v0.1.8 Update Breakpoint implementation

## [0.1.7] 2025-03-07

### Added

- v0.1.7 Setup basic conditionals for flow control (d0f41d7)
- v0.1.7 Add execute_tasks_sequence() util for proper calling multiple tasks in a row (d0f41d7)

### Changed

- v0.1.7 Move guards to flow controllers and fix implementation (ccc75cb)
- v0.1.7 Extract task execution logic into execute_task() func (4d819ee)

## [0.1.6] 2025-03-06

### Changed

- v0.1.6 Allow passing plain tasks list to automaton (daa6883)
- v0.1.6 Use vcs config .get_default() for Config.get_default() (68cdb2c)
- v0.1.6 Move explorers into separate subdir (67c83cf)

### Fixed

- v0.1.6  Fix automaton targetting for "new" projects (f0e2ff2)

## [0.1.5] 2025-03-05

### Added

- v0.1.5 Add logs to bash.execute util
- v0.1.5 Add util vcs tasks for performing vcs cli commands from automaton (58d7208)

### Changed

- v0.1.5 Rewire VCS interface and update Git implementation (96b246b)

## [0.1.4] 2025-03-03

### Added

- v0.1.4 Add InFileHistory implementation (f51d2dc)

### Changed

- v0.1.4 Update history interface to support per-automaton history (84a3b36)

## [0.1.3] 2025-02-28

### Added

- v0.1.3 Update ContainsFilter to support regexp (c95caa4)
- v0.1.3 Update Filter base class to handle logical (& | ~) operations (61f38a9)

## [0.1.2] 2025-02-28

### Changed

- v0.1.2 Fix OSFile implementation to properly process all operations (cfc7842)

## [0.1.1] 2025-02-28

### Added

- v0.1.1 Add basic readme + move updates plans to a separate file (a2076de)

### Changed

- v0.1.1 Update bash.execute util to return obj with output & status fields and capture stderr as well (3974b80)

## [0.1.0] 2025-02-28

### Added

- v0.1.0 Add a list of tasks, notes for the lib development (3503961)
- v0.1.0 Split prototype into proper folders structure (44fe56b)
- v0.1.0 Setup pure library prototype in one file with all core functionality (8fe89ab)

### Removed

- v0.0.1 Remove previous implementations of ProjectExplorer and OSFile classes (44fe56b)

## [0.0.2] 2025-02-06

### Added
- v0.0.2 Add project explorer util for interacting with all files in the project

### Changed
- v0.0.2 Only run previously failed test on test reruns to speed them up (19e04db)

## [0.0.1] 2023-05-07

### Added
- v0.0.1 Go back to hatch default build/test envs and setup automyte script (1bcdf8b)
- v0.0.1 Add changelog file + projects classifiers (c7fbe16)
- v0.0.1 Setup basic main entrypoint with smoke tests (3ae3040)
- v0.0.1 Setup basic tools + gitignore (70f1259)

### Changed
- v0.0.1 Rename package pygrate -> automyte (41e1966)
