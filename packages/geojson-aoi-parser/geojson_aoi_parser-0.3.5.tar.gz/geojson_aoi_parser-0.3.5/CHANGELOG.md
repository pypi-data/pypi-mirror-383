# Changelog

## 0.3.5 (2025-10-11)

### Fix

- cleanup code, fix test cases
- add __all__ to package root for exports

### Refactor

- run pre-commit hooks on all code

## 0.3.4 (2025-09-01)

- Fix Async parser using Sync postgis

## 0.3.3 (2025-09-01)

- Fix not using AsyncConnection in async parser

## 0.3.2 (2025-09-01)

- Fix bytes type not parsing

## 0.3.1 (2025-08-27)

- Fix a defect that was preventing some geojson files from parsing

## 0.3.0 (2025-07-14)

- Use parse_aoi() to turn geojson input into standardizes featcol ouput
- Warn user when invalid CRS is in use
- Add DbConfig class for easy database help
- Create async implementation on sync code
- Add a whole slew of tests

## 0.1.0 (2025-01-07)

### Feat

- first commit, functional code, add license

### Fix

- add check for correct type of geojson input
