# CHANGELOG

<!-- version list -->

## v1.6.1 (2025-10-10)

### Bug Fixes

- Fix python version in CI
  ([`9a1f92f`](https://github.com/sildur/fretsonfire/commit/9a1f92fcc3722d202d885574118bcb01e341d995))


## v1.6.0 (2025-10-10)

### Bug Fixes

- Require skia
  ([`cbb18a0`](https://github.com/sildur/fretsonfire/commit/cbb18a0b36f0727c9e648b153c89a31fdca47ffa))

### Chores

- Fix screenshot taking github action
  ([`05d63ce`](https://github.com/sildur/fretsonfire/commit/05d63ce4be204f94391e1cab5e12c7ad3fbe6f6e))

- **assets**: Re-export svg data with inkscape 1.4
  ([`6aa68f1`](https://github.com/sildur/fretsonfire/commit/6aa68f1c6bf9a9231b75e3444bd7675f10181da5))

- **data**: Drop legacy launch scripts and fix file permissions
  ([`0b1839e`](https://github.com/sildur/fretsonfire/commit/0b1839e12ebb83cb2d8190254f1a9e929b084923))

### Continuous Integration

- Quote PR screenshot release title ([#16](https://github.com/sildur/fretsonfire/pull/16),
  [`d9b82fc`](https://github.com/sildur/fretsonfire/commit/d9b82fc71049b459736cbdb02202955bcd432936))

### Features

- Restore SVG rendering with skia backend
  ([`6a8c97d`](https://github.com/sildur/fretsonfire/commit/6a8c97dd65001a344b8fb565e1acdfe247e37136))


## v1.5.8 (2025-10-05)

### Bug Fixes

- Apply fretsonfire icons for window and bundles
  ([`6806cb1`](https://github.com/sildur/fretsonfire/commit/6806cb14da11c953e2077713708f97b13b9c0a9d))

### Build System

- Drop legacy helper scripts
  ([`11e5c55`](https://github.com/sildur/fretsonfire/commit/11e5c55f4a022f35c68fbb9016dfebb2083241dc))

### Refactoring

- Replace Collada parser with lightweight loader
  ([`0d3f943`](https://github.com/sildur/fretsonfire/commit/0d3f9438434cacc6baee704dc476d50dba7d24bc))


## v1.5.7 (2025-10-05)

### Build System

- Disable rofiles fuse when packaging flatpak
  ([`2ef6f5d`](https://github.com/sildur/fretsonfire/commit/2ef6f5d7c499d2ded5092ad868d53959c8897ae9))

### Performance Improvements

- Lazily import glColor4f in theme color setters
  ([`7cd6a1c`](https://github.com/sildur/fretsonfire/commit/7cd6a1cab505e71d28b84cea3e07f3e371d507d4))


## v1.5.6 (2025-10-04)

### Bug Fixes

- Restore integer division in timing and input code
  ([`c86a776`](https://github.com/sildur/fretsonfire/commit/c86a77631a8ef4a6a44733f04b0cbdc443459b3c))

### Chores

- Add agent guide and markdown install docs
  ([`c69e472`](https://github.com/sildur/fretsonfire/commit/c69e4729d9a5837fedfd3f6ffe53c951d3da8323))

### Documentation

- Update todo
  ([`9282860`](https://github.com/sildur/fretsonfire/commit/9282860af6c048422bad0c7c15e5ba47f161e38c))

### Refactoring

- Use explicit relative imports
  ([`7c2a197`](https://github.com/sildur/fretsonfire/commit/7c2a1977faf7f32ef1d3935216041c1672e42258))

- Use explicit relative imports
  ([`088513f`](https://github.com/sildur/fretsonfire/commit/088513ff36a7a7895688b2511855db7a6b10b673))


## v1.5.5 (2025-10-03)

### Bug Fixes

- Harden logging and network framing
  ([`b445031`](https://github.com/sildur/fretsonfire/commit/b445031f5d8d04551f5b9b6cc08d4c36990644a5))

### Build System

- **deps**: Bump actions/download-artifact from 4 to 5
  ([`c538347`](https://github.com/sildur/fretsonfire/commit/c53834776a028945c71e7456dc136d2a45fa3366))

- **deps**: Bump actions/setup-python from 5 to 6
  ([`7ca87f3`](https://github.com/sildur/fretsonfire/commit/7ca87f3ae137755e57e568951c59a46d6132dbf0))

### Continuous Integration

- Run tests on pull requests before release
  ([`6fc8e88`](https://github.com/sildur/fretsonfire/commit/6fc8e888f33a8a336356a57621a4ed3ac1f72b3b))

### Testing

- Replace legacy tests with headless pytest suites
  ([`62dec4f`](https://github.com/sildur/fretsonfire/commit/62dec4f150863b930a81f8fe74594b2e346509c9))


## v1.5.4 (2025-09-28)

### Bug Fixes

- **ci**: Force shell to bash
  ([`5d12823`](https://github.com/sildur/fretsonfire/commit/5d128236028e00c9cc394aa3ed5fbd276b4b28e0))


## v1.5.3 (2025-09-28)

### Bug Fixes

- **ci**: Remove test param in pipeline
  ([`e40c44f`](https://github.com/sildur/fretsonfire/commit/e40c44f9fc58fd680b056a54f9341021fd085d6d))


## v1.5.2 (2025-09-28)

### Bug Fixes

- **ci**: Fix backslash in pipeline
  ([`658718f`](https://github.com/sildur/fretsonfire/commit/658718f0e56e9ac16fe4c4778a9d39f96383616e))


## v1.5.1 (2025-09-28)

### Bug Fixes

- Resume gameplay when closing pause menu
  ([`ab051a2`](https://github.com/sildur/fretsonfire/commit/ab051a2bf055f4e2123c65ef3fc458395e64d2d5))

### Continuous Integration

- Fix packaging
  ([`d833ffa`](https://github.com/sildur/fretsonfire/commit/d833ffaedb404ab42269bf5079f2f24a79d54727))


## v1.5.0 (2025-09-28)

### Bug Fixes

- Clean pyflakes warnings
  ([`2cae1af`](https://github.com/sildur/fretsonfire/commit/2cae1af0674208d918095ac7440f869ecb66ccc7))

- Pause countdown when menu is open
  ([`2e09ac1`](https://github.com/sildur/fretsonfire/commit/2e09ac16fe75e751f482103485e95f11e2bc4c31))

### Features

- Enhance continuous delivery workflow with desktop asset publishing
  ([`004712c`](https://github.com/sildur/fretsonfire/commit/004712cb641cc9fcab717602160b6d76c7e32236))


## v1.4.8 (2025-09-28)

### Bug Fixes

- Fix gcDump printing for Python 3
  ([`7cb5332`](https://github.com/sildur/fretsonfire/commit/7cb533292c1ae8e8f898411f7b70bed25e237de9))

### Continuous Integration

- Filter non-python artifacts before publish
  ([`d2aea60`](https://github.com/sildur/fretsonfire/commit/d2aea60a23cab431afc623bbfbd004f13c8b83b0))

- Publish all artifacts
  ([`2983dc0`](https://github.com/sildur/fretsonfire/commit/2983dc024f23ba45e3628c4fb307d8cbcbffb12b))


## v1.4.7 (2025-09-28)

### Bug Fixes

- Specify exception class in MidiInfoReader
  ([`ffb3b01`](https://github.com/sildur/fretsonfire/commit/ffb3b01c4c2d993d231372d1f4e0d4668eea1adb))

### Documentation

- **ci**: Document linux packaging steps
  ([`a63b1f4`](https://github.com/sildur/fretsonfire/commit/a63b1f4670684ef0c0ab7e4988c040b967ef4bcc))


## v1.4.6 (2025-09-28)

### Bug Fixes

- **ci**: Conditionally upload distribution artifacts based on release status
  ([`22770c6`](https://github.com/sildur/fretsonfire/commit/22770c604b6f7f3a75f89e852cb2069db75b7abb))

### Documentation

- Merge legacy changelog into markdown
  ([`e7f8065`](https://github.com/sildur/fretsonfire/commit/e7f806545e1de4d472a5e51c0a47d1d38c3a4b52))


## v1.4.5 (2025-09-28)

### Bug Fixes

- **translations**: Make update script Python 3 compatible
  ([`6d305df`](https://github.com/sildur/fretsonfire/commit/6d305df8e8bbaacf995d775e17e6b277f1b2e49a))

### Build System

- **ci**: Fix PSR config
  ([`ccced37`](https://github.com/sildur/fretsonfire/commit/ccced37a3e113012b8ff4002bb7ed52264edcce8))


## v1.4.4 (2025-09-28)

### Bug Fixes

- Change Python shebang to use env for Python 3
  ([`5258d81`](https://github.com/sildur/fretsonfire/commit/5258d819d812e5af4365cd4307bd9b9fe4c15734))


## v1.4.3 (2025-09-28)

### Bug Fixes

- Replace os.system with subprocess for svg2png
  ([`9122aea`](https://github.com/sildur/fretsonfire/commit/9122aeae56f6abde3bf0c5fe627864baced5ebc4))


## v1.4.2 (2025-09-28)

### Bug Fixes

- **config**: Parse upload URL host safely
  ([`4f3f109`](https://github.com/sildur/fretsonfire/commit/4f3f10944c231d5739f8df20038cba3b8af675f6))

### Build System

- **ci**: Enable manual release runs and full semantic-release build
  ([`5eb56ab`](https://github.com/sildur/fretsonfire/commit/5eb56abc9feb8a5af5aa36a181e2d11e9372e1ef))

- **ci**: Fix build command
  ([`809c2d2`](https://github.com/sildur/fretsonfire/commit/809c2d267f4817a4f274a6512d3b3d9f83e5bead))


## v1.4.1 (2025-09-28)

### Bug Fixes

- Drop accidental highscores from songs.ini
  ([`1e2e65a`](https://github.com/sildur/fretsonfire/commit/1e2e65ab63e31b97c8462e9082cbe8b86369607f))

- **gameplay**: Keep pause menu from ending song early
  ([`2cef1ca`](https://github.com/sildur/fretsonfire/commit/2cef1ca2c5360c35a07a39557c98dd2f7860cb81))

### Build System

- Repair distributable targets
  ([`72e7e06`](https://github.com/sildur/fretsonfire/commit/72e7e0638a26b120103d44900a7d1a390eff5c04))

- **ci**: Add semantic-release workflow and config
  ([`957e31b`](https://github.com/sildur/fretsonfire/commit/957e31bdb2d8fc927d5305841320d6302ab4fc46))

- **ci**: Fix branch name in github action
  ([`5185069`](https://github.com/sildur/fretsonfire/commit/51850696b82873befc720b3b234cbe5223a70afc))

### Chores

- Add dependabot configuration
  ([`246ff99`](https://github.com/sildur/fretsonfire/commit/246ff9906e84beaa76dec66b7f2ba7894b387609))

### Refactoring

- **audio**: Drop unused pyglet backend
  ([`217d1bb`](https://github.com/sildur/fretsonfire/commit/217d1bbcab6b8fc962cf45251940956966dea65d))


## v1.4.0 (2025-09-27)
- Repackaged project with pyproject.toml + setuptools build hooks.
- Moved game assets under src/fretsonfire/data for wheel installs.
- Added automatic gettext compilation during builds.
- Declared dependencies for async networking and runtime assets.

## v1.3.110
* Wrote concise instructions for building and installing the game.
* Removed runtime SVG support. All images must be pre-rasterized as PNG graphics now. This also removes the dependency on Amanith, making the game simpler to build and package.
* Reworked the build system. Now an installation package can be created with a single command for Windows and Mac OS X.
* Added textured fretboard strings and bars.
* Updated the translations.

## v1.2.512
* Effects optimization
* Font rendering optimization
* Miscellaneous bug fixes
* Added import support for Guitar Hero 80s
* Translation updates
* World Charts standing is now reported after each game

## v1.2.451
* Fixed some bugs with the tapping implementation
* Audio performance and stability fixes
* Song chooser filter enhanced
* Introduced new World Charts
* Linux packaging fixes

## v1.2.438
* Added custom fretboard and background support
* Volume control
* Song folder support
* Fixed screw-up volume
* Align notes to beat lines again
* Fixed missing encoding error on linux
* Dual core performance improvements
* Fixed crash with strangely named joysticks
* Fixed backspace etc. on mac
* Delete rhythm file after importing each song
* Improved importer encoding quality
* Made notes disappear when they are hit
* Fixed volume saturation issue with GH2 tracks
* Fixed performance issue with note effect
* Move the multiplier text upwards
* Pause the song while the menu is shown
* Implement playing multiple streaming OGG files simultaneously
* Fixed the timer skew and add a high priority mode
* Fixed the priority of the loading screens to improve loading time
* Made the fret color configurable with the theme
* Hit counter
* Type-ahead find for song chooser
* Fix Numeric memory leak
* Fix importing two missing songs on GH1 and GH2 disks
* Tapping support, aka hammer-ons and pull-ofs
* PPC Mac fixes

## v1.1.324
* Support for importing Guitar Hero(TM) II songs
* Support for game modifications
* Widescreen support
* Added the submitted translations to the game. Thanks to everyone who sent theirs in!
* Many bugfixes related to configuration settings, song creation, etc.
* Mac OS X fixes

## v1.0.263

* Mac OS X support. Okay, it's experimental, but it's there. Many thanks to Tero Pihlajakoski for his work on the Mac
  package!
* Windows installer
* Localization support
* Improvements to the song editor
* Fixed a major memory leak
* Lefty mode
* Support for cassette labels and colors
* General performance tuning

## v1.0.225

* Added a Guitar Hero(tm) song importer.
* Fixed the key-release bug for long notes introduced by the previous version.
* Added support for joystick axes and hats.
* Added adjustable song delay in the editor.
* Improved song chooser to remember last played song.
* SDL_mixer and SDL_ttf added to Linux package to ease running on e.g. FreeBSD.
* Added custom color scheme support.
* Score multiplier now resets when notes are missed.
* Added new difficulty level and support for songs with varying tempo.

## v1.0.192

* Added joystick support.
* Added support for two different pick keys.
* Only show the available difficulty levels for songs.
* Fixed the startup problems on video cards that do not support antialiasing.
* Fixed the red screen of death.
* Added the missing DLL to the Window version.
