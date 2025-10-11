# Changelog

## 0.1.0-alpha.8 (2025-10-11)

Full Changelog: [v0.1.0-alpha.7...v0.1.0-alpha.8](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.7...v0.1.0-alpha.8)

### Features

* **client:** support file upload requests ([b20d895](https://github.com/phoebe-bird/phoebe-python/commit/b20d8957f1bbfab5db47747bc82a34e6ed5f028c))
* improve future compat with pydantic v3 ([c799621](https://github.com/phoebe-bird/phoebe-python/commit/c79962151cd552ec1ae0c600d1cf0fbc9933a176))
* **types:** replace List[str] with SequenceNotStr in params ([a143e6d](https://github.com/phoebe-bird/phoebe-python/commit/a143e6d3d0d650afbdd6aae1c1f35c28c3913630))


### Bug Fixes

* avoid newer type syntax ([69c9cec](https://github.com/phoebe-bird/phoebe-python/commit/69c9cec780efe75f887a414a1200d52f166db3f6))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([fa1600e](https://github.com/phoebe-bird/phoebe-python/commit/fa1600e31f2d04dec0391596d283c0c4c7089eb8))
* **internal:** add Sequence related utils ([0d00726](https://github.com/phoebe-bird/phoebe-python/commit/0d007266246990b4b926c3d7add57de4ce00e5c3))
* **internal:** change ci workflow machines ([285826b](https://github.com/phoebe-bird/phoebe-python/commit/285826b21effbd7fc87f4cc3b7bee9136142b4d6))
* **internal:** codegen related update ([9f76e15](https://github.com/phoebe-bird/phoebe-python/commit/9f76e15354a093ba15323dc3a43cef11829c2763))
* **internal:** fix ruff target version ([14df2d4](https://github.com/phoebe-bird/phoebe-python/commit/14df2d48ef970d81574c293412e09915d234ffc0))
* **internal:** move mypy configurations to `pyproject.toml` file ([77626c2](https://github.com/phoebe-bird/phoebe-python/commit/77626c296eb865b38c268837a164cac9afe176e1))
* **internal:** update comment in script ([4f945b5](https://github.com/phoebe-bird/phoebe-python/commit/4f945b50e4416e3c0c8e466cbcf22d8cfea567d4))
* **internal:** update pydantic dependency ([b4a4165](https://github.com/phoebe-bird/phoebe-python/commit/b4a4165e116c5f79fbe9e630a6ae759e4e62838a))
* **internal:** update pyright exclude list ([c14df63](https://github.com/phoebe-bird/phoebe-python/commit/c14df63e11f28cea3260e50130c38b04baf44ae8))
* **tests:** simplify `get_platform` test ([10cecd2](https://github.com/phoebe-bird/phoebe-python/commit/10cecd210d6dce9c4a121b214fab7d6ec721aa5a))
* **types:** change optional parameter type from NotGiven to Omit ([204278a](https://github.com/phoebe-bird/phoebe-python/commit/204278a2e911ea4f05b07780eb3555bd4744d4c8))
* update @stainless-api/prism-cli to v5.15.0 ([3e66e95](https://github.com/phoebe-bird/phoebe-python/commit/3e66e953ae105d45a0573034f941a16aadd3c665))
* update github action ([6102421](https://github.com/phoebe-bird/phoebe-python/commit/6102421c15a4b6bb8b1b5241ad85ab6870bea9fa))

## 0.1.0-alpha.7 (2025-07-25)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* clean up environment call outs ([a24346a](https://github.com/phoebe-bird/phoebe-python/commit/a24346a18361ff45ecf74aec4259ed1e637de11b))


### Bug Fixes

* **client:** don't send Content-Type header on GET requests ([f205945](https://github.com/phoebe-bird/phoebe-python/commit/f205945db67cc14d75069aaf789b1cbc02001fef))
* **parsing:** ignore empty metadata ([e6beeb3](https://github.com/phoebe-bird/phoebe-python/commit/e6beeb3f0626a73da5a7ac1edd4aa2da2646d22e))
* **parsing:** parse extra field types ([38b4177](https://github.com/phoebe-bird/phoebe-python/commit/38b417781bdae4b7b780f9f1b6971ff3f36aaf2c))


### Chores

* **project:** add settings file for vscode ([130cd95](https://github.com/phoebe-bird/phoebe-python/commit/130cd95b99ad33f20727b082daac5aabe8832c17))

## 0.1.0-alpha.6 (2025-07-11)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* **client:** add follow_redirects request option ([087f081](https://github.com/phoebe-bird/phoebe-python/commit/087f081dca8727864403f32a66448300933cfa9a))
* **client:** add support for aiohttp ([6968740](https://github.com/phoebe-bird/phoebe-python/commit/6968740ccb8830e39d3c32e3a05061da3f90e73f))


### Bug Fixes

* **ci:** correct conditional ([927b67c](https://github.com/phoebe-bird/phoebe-python/commit/927b67cfcb1d972b4fbb4ebed0e76fddf3995e33))
* **ci:** release-doctor — report correct token name ([19345ea](https://github.com/phoebe-bird/phoebe-python/commit/19345ea980544dd5933dacc6ceba41919ba56910))
* **client:** correctly parse binary response | stream ([5d4527c](https://github.com/phoebe-bird/phoebe-python/commit/5d4527c7ac682a6026e8a625e9d9149b1438131c))
* **parsing:** correctly handle nested discriminated unions ([cbe0682](https://github.com/phoebe-bird/phoebe-python/commit/cbe068244ccd8fffc63d6e8f776b4579fb2a5fd4))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([9dc8f8a](https://github.com/phoebe-bird/phoebe-python/commit/9dc8f8afa0b95505a5dcf5a1cc03aa78f653f698))


### Chores

* **ci:** change upload type ([97fbc28](https://github.com/phoebe-bird/phoebe-python/commit/97fbc281dd030bbf7173b86c1c91fdf6e6aa3c65))
* **ci:** enable for pull requests ([32c375f](https://github.com/phoebe-bird/phoebe-python/commit/32c375f982631b09b3e44bdd265771824a943285))
* **ci:** only run for pushes and fork pull requests ([76c815c](https://github.com/phoebe-bird/phoebe-python/commit/76c815ce62d931b02594bae35a9664f167a830ee))
* **docs:** grammar improvements ([d1ec6eb](https://github.com/phoebe-bird/phoebe-python/commit/d1ec6eb429b9c77e73e213df4e6e27855c57c231))
* **docs:** remove reference to rye shell ([e225dac](https://github.com/phoebe-bird/phoebe-python/commit/e225dac79e67526aac19dac460bedb121635bd47))
* **internal:** bump pinned h11 dep ([c233db7](https://github.com/phoebe-bird/phoebe-python/commit/c233db706a43c51418dd64a60a430b1bf54e05d3))
* **internal:** codegen related update ([c0a4171](https://github.com/phoebe-bird/phoebe-python/commit/c0a4171e29de8e93d1719c90c90252028a0d53ea))
* **internal:** update conftest.py ([60ae0b4](https://github.com/phoebe-bird/phoebe-python/commit/60ae0b4d07b5f054b097bea0479f0e02c3f4100b))
* **package:** mark python 3.13 as supported ([07a5943](https://github.com/phoebe-bird/phoebe-python/commit/07a594361df34ce72d645cf9b1685ed6586518a3))
* **readme:** fix version rendering on pypi ([79c3875](https://github.com/phoebe-bird/phoebe-python/commit/79c3875c67216eff4f8e0b221f493d5488c03f98))
* **readme:** update badges ([b1638a4](https://github.com/phoebe-bird/phoebe-python/commit/b1638a4b300645fdf0c9b4508cf9a5de51ac5f72))
* **tests:** add tests for httpx client instantiation & proxies ([c66c20c](https://github.com/phoebe-bird/phoebe-python/commit/c66c20c146fe24e887df79295be8eaffcbc1274e))
* **tests:** run tests in parallel ([65f275c](https://github.com/phoebe-bird/phoebe-python/commit/65f275c3a6e663f8d13b23ca478c8609def10435))
* **tests:** skip some failing tests on the latest python versions ([24b9862](https://github.com/phoebe-bird/phoebe-python/commit/24b98626f885d4675d8feeb7cedc49315bce6014))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([ba57bf0](https://github.com/phoebe-bird/phoebe-python/commit/ba57bf076c4d84398fa9b6d85c5aca32c521732f))

## 0.1.0-alpha.5 (2025-05-21)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Bug Fixes

* **package:** support direct resource imports ([1f09273](https://github.com/phoebe-bird/phoebe-python/commit/1f092739a3e083b74dbf2818651f1041006352c9))


### Chores

* **ci:** fix installation instructions ([9e43bb2](https://github.com/phoebe-bird/phoebe-python/commit/9e43bb2ac1576e9ef7ff11347210285f532306ef))
* **ci:** upload sdks to package manager ([6987440](https://github.com/phoebe-bird/phoebe-python/commit/6987440d75a9bca885132c0dacda6f9dc40ee1ec))
* **internal:** avoid errors for isinstance checks on proxies ([4aadfa7](https://github.com/phoebe-bird/phoebe-python/commit/4aadfa71f18713661a1dfc22f9efb2e715dfef32))
* **internal:** codegen related update ([c39bf22](https://github.com/phoebe-bird/phoebe-python/commit/c39bf22263c57bb85b99de208e45c70c1e57de81))
* **internal:** codegen related update ([c7ae911](https://github.com/phoebe-bird/phoebe-python/commit/c7ae9114d719331086f4a275111890dd882c8edf))

## 0.1.0-alpha.4 (2025-05-07)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### ⚠ BREAKING CHANGES

* **api:** upgrade SDK version to match new Typescript features

### Features

* **api:** upgrade SDK version to match new Typescript features ([83f1a29](https://github.com/phoebe-bird/phoebe-python/commit/83f1a295b0fbcda5d6914777ede4ecaddc8b602c))


### Bug Fixes

* **client:** only call .close() when needed ([#44](https://github.com/phoebe-bird/phoebe-python/issues/44)) ([484e3ae](https://github.com/phoebe-bird/phoebe-python/commit/484e3ae08c20157cbb81a235daf18aa53bca9eac))
* correctly handle deserialising `cls` fields ([#47](https://github.com/phoebe-bird/phoebe-python/issues/47)) ([56166e4](https://github.com/phoebe-bird/phoebe-python/commit/56166e431ac07307d0f7e4d25a5905511971fd5d))
* **tests:** make test_get_platform less flaky ([#50](https://github.com/phoebe-bird/phoebe-python/issues/50)) ([f7e04e6](https://github.com/phoebe-bird/phoebe-python/commit/f7e04e608f687f58ecbb621619deee5fc9a6f5c6))


### Chores

* add missing isclass check ([#42](https://github.com/phoebe-bird/phoebe-python/issues/42)) ([bb0e4dc](https://github.com/phoebe-bird/phoebe-python/commit/bb0e4dc7361b229ca908892d9e697b4849b58298))
* **internal:** add support for TypeAliasType ([#32](https://github.com/phoebe-bird/phoebe-python/issues/32)) ([74c00eb](https://github.com/phoebe-bird/phoebe-python/commit/74c00eb5f16b7d2c6cf91c210a7992132100c9ff))
* **internal:** avoid pytest-asyncio deprecation warning ([#51](https://github.com/phoebe-bird/phoebe-python/issues/51)) ([317cc73](https://github.com/phoebe-bird/phoebe-python/commit/317cc73943e8a3f16d3f3f5acc27f7c471c609ff))
* **internal:** bump httpx dependency ([#43](https://github.com/phoebe-bird/phoebe-python/issues/43)) ([7873621](https://github.com/phoebe-bird/phoebe-python/commit/78736215148315e67d9021f7252aa654cb4fe477))
* **internal:** bump pyright ([#31](https://github.com/phoebe-bird/phoebe-python/issues/31)) ([56fc9f6](https://github.com/phoebe-bird/phoebe-python/commit/56fc9f6d8e376ad59a310e5ee5477d1cef6e9755))
* **internal:** codegen related update ([#30](https://github.com/phoebe-bird/phoebe-python/issues/30)) ([ee29c81](https://github.com/phoebe-bird/phoebe-python/commit/ee29c817ae3bea67a36ca602e686a8e47ce01e43))
* **internal:** codegen related update ([#33](https://github.com/phoebe-bird/phoebe-python/issues/33)) ([e640d95](https://github.com/phoebe-bird/phoebe-python/commit/e640d9539985b248ef3b508c93343dd06b89f562))
* **internal:** codegen related update ([#34](https://github.com/phoebe-bird/phoebe-python/issues/34)) ([cccec95](https://github.com/phoebe-bird/phoebe-python/commit/cccec954d6dfdb94d4aee374f77b68b63c463db4))
* **internal:** codegen related update ([#35](https://github.com/phoebe-bird/phoebe-python/issues/35)) ([194b3b4](https://github.com/phoebe-bird/phoebe-python/commit/194b3b46be481eef30374a76cc4829acc17f036b))
* **internal:** codegen related update ([#36](https://github.com/phoebe-bird/phoebe-python/issues/36)) ([eb98a76](https://github.com/phoebe-bird/phoebe-python/commit/eb98a764095034b4bd8da2bde59340ca1f26d3f5))
* **internal:** codegen related update ([#41](https://github.com/phoebe-bird/phoebe-python/issues/41)) ([4287a29](https://github.com/phoebe-bird/phoebe-python/commit/4287a29895de379a38cc3ca5c506e2b579e3d05c))
* **internal:** codegen related update ([#46](https://github.com/phoebe-bird/phoebe-python/issues/46)) ([c437ad1](https://github.com/phoebe-bird/phoebe-python/commit/c437ad152220653915c1c4a49ef6e3c7f099fbcc))
* **internal:** codegen related update ([#48](https://github.com/phoebe-bird/phoebe-python/issues/48)) ([b96bf78](https://github.com/phoebe-bird/phoebe-python/commit/b96bf78ce97afb67421dc3f89ade6acc5c97b3e7))
* **internal:** codegen related update ([#52](https://github.com/phoebe-bird/phoebe-python/issues/52)) ([bdbf52a](https://github.com/phoebe-bird/phoebe-python/commit/bdbf52a0ad97c6afbb00178e7582b7594487da04))
* **internal:** fix some typos ([#40](https://github.com/phoebe-bird/phoebe-python/issues/40)) ([5fc44b6](https://github.com/phoebe-bird/phoebe-python/commit/5fc44b6ce5160daa48d6178f9b221f2a3214664a))
* **internal:** minor formatting changes ([#53](https://github.com/phoebe-bird/phoebe-python/issues/53)) ([65176ce](https://github.com/phoebe-bird/phoebe-python/commit/65176ce9ad9fb2068dd447297967dd6d866f6d55))
* **internal:** remove some duplicated imports ([#37](https://github.com/phoebe-bird/phoebe-python/issues/37)) ([eb66b37](https://github.com/phoebe-bird/phoebe-python/commit/eb66b377b34fb1a423aaf3b93ca578064601dfb1))
* **internal:** updated imports ([#38](https://github.com/phoebe-bird/phoebe-python/issues/38)) ([8d95da3](https://github.com/phoebe-bird/phoebe-python/commit/8d95da3455ca86cc236967c84ef261fe1047adb4))
* make the `Omit` type public ([#28](https://github.com/phoebe-bird/phoebe-python/issues/28)) ([3c28c9b](https://github.com/phoebe-bird/phoebe-python/commit/3c28c9b459c968964d3d57a179cc5a46e4cfc2fb))


### Documentation

* fix typos ([#45](https://github.com/phoebe-bird/phoebe-python/issues/45)) ([0a19122](https://github.com/phoebe-bird/phoebe-python/commit/0a191228b8969524f011c2a0dedeecd7d94154e3))
* **raw responses:** fix duplicate `the` ([#49](https://github.com/phoebe-bird/phoebe-python/issues/49)) ([b2244bb](https://github.com/phoebe-bird/phoebe-python/commit/b2244bb5675273bb3308fb7806a239456b8f4e46))
* **readme:** example snippet for client context manager ([#39](https://github.com/phoebe-bird/phoebe-python/issues/39)) ([ac62abe](https://github.com/phoebe-bird/phoebe-python/commit/ac62abeecbe5fc5204ff449a0dae14c8222fe743))

## 0.1.0-alpha.3 (2024-12-03)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Bug Fixes

* **api:** get repo clean ([#14](https://github.com/phoebe-bird/phoebe-python/issues/14)) ([28470b8](https://github.com/phoebe-bird/phoebe-python/commit/28470b8579956fe39e92b6aa55a89d34fffd5ff4))
* **client:** compat with new httpx 0.28.0 release ([#25](https://github.com/phoebe-bird/phoebe-python/issues/25)) ([10748d0](https://github.com/phoebe-bird/phoebe-python/commit/10748d06f5154bfc9fd7bffb9a035aff449189b5))


### Chores

* **internal:** bump pyright ([#26](https://github.com/phoebe-bird/phoebe-python/issues/26)) ([b6362e9](https://github.com/phoebe-bird/phoebe-python/commit/b6362e9376aa5ceb958970682459e906727a4a45))
* **internal:** exclude mypy from running on tests ([#24](https://github.com/phoebe-bird/phoebe-python/issues/24)) ([2ab77ee](https://github.com/phoebe-bird/phoebe-python/commit/2ab77ee42f02eba645742b4eacab7b10581ead61))
* **internal:** fix compat model_dump method when warnings are passed ([#21](https://github.com/phoebe-bird/phoebe-python/issues/21)) ([7897301](https://github.com/phoebe-bird/phoebe-python/commit/7897301d160007df9e843c97f60481536bd07293))
* rebuild project due to codegen change ([#16](https://github.com/phoebe-bird/phoebe-python/issues/16)) ([19478a7](https://github.com/phoebe-bird/phoebe-python/commit/19478a7560434c8c2a1fa0b1680a6bbdd8307552))
* rebuild project due to codegen change ([#17](https://github.com/phoebe-bird/phoebe-python/issues/17)) ([698aecb](https://github.com/phoebe-bird/phoebe-python/commit/698aecbd81367cbfd331f0c78bbfc85f3cfcc012))
* rebuild project due to codegen change ([#18](https://github.com/phoebe-bird/phoebe-python/issues/18)) ([766d1a8](https://github.com/phoebe-bird/phoebe-python/commit/766d1a82564c074073e51bae85da72a069ede68f))
* rebuild project due to codegen change ([#19](https://github.com/phoebe-bird/phoebe-python/issues/19)) ([59ef073](https://github.com/phoebe-bird/phoebe-python/commit/59ef073731a6377866f9c6bc00e2fe53f4ce150e))
* rebuild project due to codegen change ([#20](https://github.com/phoebe-bird/phoebe-python/issues/20)) ([26413bd](https://github.com/phoebe-bird/phoebe-python/commit/26413bdf5fb60322d22a22cac4f0ac01d6029a0a))
* remove now unused `cached-property` dep ([#23](https://github.com/phoebe-bird/phoebe-python/issues/23)) ([5eba39b](https://github.com/phoebe-bird/phoebe-python/commit/5eba39bc3dab9ad10e8b82ed8c5cc875b688df42))


### Documentation

* add info log level to readme ([#22](https://github.com/phoebe-bird/phoebe-python/issues/22)) ([e37a2fc](https://github.com/phoebe-bird/phoebe-python/commit/e37a2fc11b65f4e975262a766f2d6d08545e14b5))

## 0.1.0-alpha.2 (2024-07-07)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/phoebe-bird/phoebe-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **docs:** update contact email ([#12](https://github.com/phoebe-bird/phoebe-python/issues/12)) ([1cadb56](https://github.com/phoebe-bird/phoebe-python/commit/1cadb564708531b50fc1d49a683b044e94708ab4))

## 0.1.0-alpha.1 (2024-07-07)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/phoebe-bird/phoebe-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** add docs to openapi spec ([#6](https://github.com/phoebe-bird/phoebe-python/issues/6)) ([48a914e](https://github.com/phoebe-bird/phoebe-python/commit/48a914ed6c19b308129b6ddb87b47600772b12f7))
* **api:** add python ([#1](https://github.com/phoebe-bird/phoebe-python/issues/1)) ([32d688d](https://github.com/phoebe-bird/phoebe-python/commit/32d688d87fe45ec05fe15306d48632eb246eaacf))
* **api:** fix adjacent region ([#5](https://github.com/phoebe-bird/phoebe-python/issues/5)) ([2eb594d](https://github.com/phoebe-bird/phoebe-python/commit/2eb594db27e90b97532c0fb52ebf12b93cf3e297))
* **api:** manual updates ([#3](https://github.com/phoebe-bird/phoebe-python/issues/3)) ([13a0146](https://github.com/phoebe-bird/phoebe-python/commit/13a0146de8696542ad5631252ff10851f85b06ba))


### Chores

* configure new SDK language ([0c39913](https://github.com/phoebe-bird/phoebe-python/commit/0c39913d143536aa1d7e096e79a74ad2ab8d973e))
* update SDK settings ([4174038](https://github.com/phoebe-bird/phoebe-python/commit/4174038355ba0b0c5ef9777709a00c5478925eaf))
* update SDK settings ([#4](https://github.com/phoebe-bird/phoebe-python/issues/4)) ([738803c](https://github.com/phoebe-bird/phoebe-python/commit/738803cff82bd54b44b8746f4b0fd5162c27ec1b))
* update SDK settings ([#7](https://github.com/phoebe-bird/phoebe-python/issues/7)) ([ee04119](https://github.com/phoebe-bird/phoebe-python/commit/ee041194307a44b0e723e7441a1e778e34495e5e))
