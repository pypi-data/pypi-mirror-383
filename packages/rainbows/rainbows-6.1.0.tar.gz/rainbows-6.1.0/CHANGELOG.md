# Changelog

## 6.1.0 (2025-10-12)

Full Changelog: [v6.0.0...v6.1.0](https://github.com/pilfo/rainbows/compare/v6.0.0...v6.1.0)

### Features

* **api:** manual updates ([1dae4fb](https://github.com/pilfo/rainbows/commit/1dae4fb6a9d6409f866db4c66ecf2b5a7d10cfed))


### Chores

* **internal:** detect missing future annotations with ruff ([f2fa2b6](https://github.com/pilfo/rainbows/commit/f2fa2b6a78222f62ff46ad60d19574aa60e70c9a))

## 6.0.0 (2025-10-01)

Full Changelog: [v5.1.0...v6.0.0](https://github.com/pilfo/rainbows/compare/v5.1.0...v6.0.0)

### ⚠ BREAKING CHANGES

* **client:** rename `Jsonl` to `JSONL` ([#35](https://github.com/pilfo/rainbows/issues/35))

### Features

* **api:** manual updates ([61a90ac](https://github.com/pilfo/rainbows/commit/61a90ac93a24c1d92cf5a23d06dc64a2d2e41d48))
* **client:** send `X-Stainless-Read-Timeout` header ([#40](https://github.com/pilfo/rainbows/issues/40)) ([2815555](https://github.com/pilfo/rainbows/commit/28155557c85a2851759962721cbbe624137dd990))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#44](https://github.com/pilfo/rainbows/issues/44)) ([8103072](https://github.com/pilfo/rainbows/commit/8103072b0f77847a4fcd5b7be21eb8e1f776f8e0))
* correctly handle deserialising `cls` fields ([#32](https://github.com/pilfo/rainbows/issues/32)) ([eae02d6](https://github.com/pilfo/rainbows/commit/eae02d6f8f0c8348ca2e3b7cf6ab1dcbbc56b383))


### Chores

* add missing isclass check ([#28](https://github.com/pilfo/rainbows/issues/28)) ([0b9a806](https://github.com/pilfo/rainbows/commit/0b9a8060e838268b0891e0583798a8f661b853c3))
* **client:** rename `Jsonl` to `JSONL` ([#35](https://github.com/pilfo/rainbows/issues/35)) ([7839213](https://github.com/pilfo/rainbows/commit/78392133ed67ea99aa90b07554fdc5a755df829c))
* **internal:** bummp ruff dependency ([#39](https://github.com/pilfo/rainbows/issues/39)) ([2330fc2](https://github.com/pilfo/rainbows/commit/2330fc2310613a1703632b3b3a032b68c72d7226))
* **internal:** change default timeout to an int ([#38](https://github.com/pilfo/rainbows/issues/38)) ([32b5f18](https://github.com/pilfo/rainbows/commit/32b5f180b772d80da104885bc5c1a84b7be3b75d))
* **internal:** codegen related update ([#26](https://github.com/pilfo/rainbows/issues/26)) ([acbc1c1](https://github.com/pilfo/rainbows/commit/acbc1c18024b6e9cf297d6ccf1c899303e74824a))
* **internal:** codegen related update ([#29](https://github.com/pilfo/rainbows/issues/29)) ([4906171](https://github.com/pilfo/rainbows/commit/49061718e25e305d0b66ca10a6b709a228a52c03))
* **internal:** codegen related update ([#31](https://github.com/pilfo/rainbows/issues/31)) ([8aabfb1](https://github.com/pilfo/rainbows/commit/8aabfb11dbea24ba8338d0628397f5f096920b17))
* **internal:** codegen related update ([#33](https://github.com/pilfo/rainbows/issues/33)) ([66ecd00](https://github.com/pilfo/rainbows/commit/66ecd00192145d7b7ee3f481891deebd81f6f065))
* **internal:** codegen related update ([#34](https://github.com/pilfo/rainbows/issues/34)) ([3103a0e](https://github.com/pilfo/rainbows/commit/3103a0e3a253a345462868b60c0de8ddb33619a0))
* **internal:** fix type traversing dictionary params ([#41](https://github.com/pilfo/rainbows/issues/41)) ([2a90925](https://github.com/pilfo/rainbows/commit/2a90925334e7d61fe801dfed97ad17653753b6d7))
* **internal:** minor formatting changes ([#37](https://github.com/pilfo/rainbows/issues/37)) ([bd25d39](https://github.com/pilfo/rainbows/commit/bd25d39266537d6a678cda9d8be84a2c18a10153))
* **internal:** minor style changes ([#36](https://github.com/pilfo/rainbows/issues/36)) ([96be9c7](https://github.com/pilfo/rainbows/commit/96be9c7e6a4f78f6dfd26cbf5f3e9deca1d310cb))
* **internal:** minor type handling changes ([#42](https://github.com/pilfo/rainbows/issues/42)) ([849ad31](https://github.com/pilfo/rainbows/commit/849ad3160e791e9474f60219bc088cffc90ec23f))
* **internal:** update client tests ([#43](https://github.com/pilfo/rainbows/issues/43)) ([57173c4](https://github.com/pilfo/rainbows/commit/57173c485c3da7a579849182e90fda1383ce4781))


### Documentation

* fix typos ([#30](https://github.com/pilfo/rainbows/issues/30)) ([9d650af](https://github.com/pilfo/rainbows/commit/9d650af0cf999ddd0833a498542b3e19620e67d7))

## 5.1.0 (2024-12-18)

Full Changelog: [v5.0.0...v5.1.0](https://github.com/pilfo/rainbows/compare/v5.0.0...v5.1.0)

### Features

* **api:** update via SDK Studio ([#24](https://github.com/pilfo/rainbows/issues/24)) ([7e2f75d](https://github.com/pilfo/rainbows/commit/7e2f75ded2d921866d4ec8e8ed91ed67b46c3b1d))


### Chores

* **internal:** fix some typos ([#22](https://github.com/pilfo/rainbows/issues/22)) ([20d1725](https://github.com/pilfo/rainbows/commit/20d172593a98310b606adb3fb9cfceca5eada88b))

## 5.0.0 (2024-12-17)

Full Changelog: [v4.1.1...v5.0.0](https://github.com/pilfo/rainbows/compare/v4.1.1...v5.0.0)

### Features

* **api:** update via SDK Studio ([#19](https://github.com/pilfo/rainbows/issues/19)) ([d254e26](https://github.com/pilfo/rainbows/commit/d254e26af17992c78458171208f5027f3d803159))

## 4.1.1 (2024-12-17)

Full Changelog: [v4.1.0...v4.1.1](https://github.com/pilfo/rainbows/compare/v4.1.0...v4.1.1)

### Chores

* **internal:** add support for TypeAliasType ([#13](https://github.com/pilfo/rainbows/issues/13)) ([a541f9e](https://github.com/pilfo/rainbows/commit/a541f9e3da92ca6f0cd20b9a26172e6a0dd93553))
* **internal:** bump pydantic dependency ([#10](https://github.com/pilfo/rainbows/issues/10)) ([91cbc85](https://github.com/pilfo/rainbows/commit/91cbc855e81c17dd5725b816e741fcbf30b0e22e))
* **internal:** bump pyright ([#12](https://github.com/pilfo/rainbows/issues/12)) ([4c293f7](https://github.com/pilfo/rainbows/commit/4c293f7af24556f23533e9ba1f7287b73b6dd60e))
* **internal:** codegen related update ([#14](https://github.com/pilfo/rainbows/issues/14)) ([3f92edd](https://github.com/pilfo/rainbows/commit/3f92eddf4c2bc4d52e74b78eb2bd900f9ef4c799))
* **internal:** codegen related update ([#15](https://github.com/pilfo/rainbows/issues/15)) ([638dd77](https://github.com/pilfo/rainbows/commit/638dd77f6d3f0414e8a4e4807b1f8b1cb94cf07b))
* **internal:** codegen related update ([#7](https://github.com/pilfo/rainbows/issues/7)) ([c064e3d](https://github.com/pilfo/rainbows/commit/c064e3d3cf462f692d5b863a6b46eacc36497b2b))
* **internal:** updated imports ([#16](https://github.com/pilfo/rainbows/issues/16)) ([7071fde](https://github.com/pilfo/rainbows/commit/7071fde0f17b87b38833190e99bcf1428361ee19))
* make the `Omit` type public ([#9](https://github.com/pilfo/rainbows/issues/9)) ([8a8b515](https://github.com/pilfo/rainbows/commit/8a8b515efff013bc80145825930d69f4203f6d4a))


### Documentation

* **readme:** example snippet for client context manager ([#17](https://github.com/pilfo/rainbows/issues/17)) ([151a687](https://github.com/pilfo/rainbows/commit/151a6878635020c503ed697a145811a3c4f7ac86))
* **readme:** fix http client proxies example ([#11](https://github.com/pilfo/rainbows/issues/11)) ([d7dd5bc](https://github.com/pilfo/rainbows/commit/d7dd5bc265b210f9128560548938394bd5b0e442))

## 4.1.0 (2024-12-06)

Full Changelog: [v4.0.0...v4.1.0](https://github.com/pilfo/rainbows/compare/v4.0.0...v4.1.0)

### Features

* **api:** update via SDK Studio ([#4](https://github.com/pilfo/rainbows/issues/4)) ([0751e67](https://github.com/pilfo/rainbows/commit/0751e67566f4d80c606a27beb7109275eccb5197))

## 4.0.0 (2024-12-06)

Full Changelog: [v3.0.0...v4.0.0](https://github.com/pilfo/rainbows/compare/v3.0.0...v4.0.0)

### Features

* **api:** update via SDK Studio ([eef5ee6](https://github.com/pilfo/rainbows/commit/eef5ee6b3738745897b6737a84004620d60cbfd0))
* **api:** update via SDK Studio ([085b462](https://github.com/pilfo/rainbows/commit/085b46261f3f662f1f355e8d49fbaf8557c166b4))
* **api:** update via SDK Studio ([454aa3e](https://github.com/pilfo/rainbows/commit/454aa3e8ec9f5297dc1c26218e9a7eac8f28d807))
* **api:** update via SDK Studio ([3e5ee1e](https://github.com/pilfo/rainbows/commit/3e5ee1ebc964eb8e81e1611871e6a294624beb72))
* **api:** update via SDK Studio ([#25](https://github.com/pilfo/rainbows/issues/25)) ([f48ad1c](https://github.com/pilfo/rainbows/commit/f48ad1c751059196e07cd3d0161bbd855bbc69ed))
* **api:** update via SDK Studio ([#26](https://github.com/pilfo/rainbows/issues/26)) ([2f720cc](https://github.com/pilfo/rainbows/commit/2f720cc6b71f5ec97f477a288db243609978035a))
* **api:** update via SDK Studio ([#28](https://github.com/pilfo/rainbows/issues/28)) ([741df9d](https://github.com/pilfo/rainbows/commit/741df9dce5f2da19aa29bc8698de2eaad73bc4f6))
* **api:** update via SDK Studio ([#29](https://github.com/pilfo/rainbows/issues/29)) ([648fac2](https://github.com/pilfo/rainbows/commit/648fac2b7546ecf4a7db5d463ed2b72a37e3ca9f))


### Bug Fixes

* **client:** compat with new httpx 0.28.0 release ([#21](https://github.com/pilfo/rainbows/issues/21)) ([afb2abd](https://github.com/pilfo/rainbows/commit/afb2abd3253742b46b0dea59578ac0bd6c8be8c2))


### Chores

* go live ([#2](https://github.com/pilfo/rainbows/issues/2)) ([13a14bc](https://github.com/pilfo/rainbows/commit/13a14bce87d695e747b9deecbcc962763c62dd7d))
* go live ([#22](https://github.com/pilfo/rainbows/issues/22)) ([1177b69](https://github.com/pilfo/rainbows/commit/1177b696942a9cb78be2aee7482d9c22b6198f33))
* **internal:** codegen related update ([#19](https://github.com/pilfo/rainbows/issues/19)) ([d95a538](https://github.com/pilfo/rainbows/commit/d95a538217baa7521413615973dad90dd4313ea4))
* **internal:** exclude mypy from running on tests ([#20](https://github.com/pilfo/rainbows/issues/20)) ([66e0b10](https://github.com/pilfo/rainbows/commit/66e0b10083f4dc74a7e96b0af309589e96c33d03))
* **internal:** fix compat model_dump method when warnings are passed ([#17](https://github.com/pilfo/rainbows/issues/17)) ([ea30ea1](https://github.com/pilfo/rainbows/commit/ea30ea1765d516025d7f8a113f314e023a0d488b))
* rebuild project due to codegen change ([#12](https://github.com/pilfo/rainbows/issues/12)) ([657d05f](https://github.com/pilfo/rainbows/commit/657d05f4da1d9df2c3de7bc6f8d53fb4da085744))
* rebuild project due to codegen change ([#14](https://github.com/pilfo/rainbows/issues/14)) ([f6b59c3](https://github.com/pilfo/rainbows/commit/f6b59c3b36a18de2ca63f7bb44437cf0aa28ae45))
* rebuild project due to codegen change ([#15](https://github.com/pilfo/rainbows/issues/15)) ([e378f2c](https://github.com/pilfo/rainbows/commit/e378f2c155255230d874c67adee2ddb29b7590ea))
* rebuild project due to codegen change ([#16](https://github.com/pilfo/rainbows/issues/16)) ([f0b9f97](https://github.com/pilfo/rainbows/commit/f0b9f9715fa4859174aed4543315b6b68eb9700e))
* update SDK settings ([8889782](https://github.com/pilfo/rainbows/commit/888978214d75579dde54f49c57dfa66e7ec8546e))


### Documentation

* add info log level to readme ([#18](https://github.com/pilfo/rainbows/issues/18)) ([7a3a24f](https://github.com/pilfo/rainbows/commit/7a3a24ffa2557d42354afc18f06b8efbf8d3579d))

## 3.0.0 (2024-09-18)

Full Changelog: [v2.0.0...v3.0.0](https://github.com/pilfo/rainbows/compare/v2.0.0...v3.0.0)

### Features

* **api:** update via SDK Studio ([801f471](https://github.com/pilfo/rainbows/commit/801f4715d5d4b53d3a5c6606d69fc806dfa2bf34))
* **api:** update via SDK Studio ([2ef1f5a](https://github.com/pilfo/rainbows/commit/2ef1f5a0ba9cf9993d7b933a00083d3ac81e6cbe))


### Chores

* go live ([#8](https://github.com/pilfo/rainbows/issues/8)) ([db4f167](https://github.com/pilfo/rainbows/commit/db4f167dd2593e08d687f18e66d98c7d6966e2cf))
* update SDK settings ([#10](https://github.com/pilfo/rainbows/issues/10)) ([133f843](https://github.com/pilfo/rainbows/commit/133f843e3e1c1bc242ef4bdc5c14044eaae7f6e1))

## 2.0.0 (2024-09-18)

Full Changelog: [v0.0.1-alpha.0...v2.0.0](https://github.com/pilfo/rainbows/compare/v0.0.1-alpha.0...v2.0.0)

### Chores

* go live ([#4](https://github.com/pilfo/rainbows/issues/4)) ([93cd5cd](https://github.com/pilfo/rainbows/commit/93cd5cd6ca0e8aa4d7dc46e25a8a59a3e3cb061a))
* update SDK settings ([#6](https://github.com/pilfo/rainbows/issues/6)) ([89c8d53](https://github.com/pilfo/rainbows/commit/89c8d53c10207c04b30a38352207e304da837b58))
