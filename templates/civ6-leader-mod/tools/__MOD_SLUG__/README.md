# __MOD_NAME__ Tooling

`assets/__MOD_SLUG__/mod-build.toml` is the single source for release version,
asset revision, paths, and BLP package names. Add the Mod-specific image build,
Cook plan, and static contracts here; reuse `tools/common/` for TOML, DDS,
Asset Cooker, and generic static validation helpers.
