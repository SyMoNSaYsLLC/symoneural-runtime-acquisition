# Apple and Android — what is actually on this machine

Read from disk 2026-09-13. Written because *"I should have everything here"* is
not the case for these two, and finding that out during a build is expensive.

---

## Android — NOT buildable

| Present | |
|---|---|
| `/usr/lib/android-sdk/platform-tools` | `adb` only |
| Debian packages | `adb`, `android-libbase`, `android-libcutils`, `android-liblog`, `android-libziparchive`, `android-libboringssl`, `android-udev-rules`, `scrcpy` |

**Absent — and these are the ones that matter:**

- **No NDK.** Nothing under `android-sdk/ndk`, no `android-ndk*` anywhere on the
  filesystem, no `aarch64-linux-android-clang` on `PATH`.
- **No SDK platforms**, no `sdkmanager`, no `gradle`.

Those Debian `android-lib*` packages are **host-side libraries that let `adb` and
`scrcpy` talk to a device**. They are not a cross-compilation toolchain and
cannot produce an Android binary.

**Verdict: there is no Android source or toolchain to bring into the estate.**
Android native builds need the NDK, which is a separate ~1-3 GB acquisition with
its own licence characterisation.

---

## Apple — present, but not usable

### Swift SDK — installed, populated, blocked

`~/.swiftpm/swift-sdks/darwin.artifactbundle`, 3.2 GB, five target triples:
`x86_64-apple-macosx`, `arm64-apple-macosx`, `arm64-apple-ios`,
`x86_64-apple-ios-simulator`, `arm64-apple-ios-simulator`.

Two defects, detail in `docs/handbook/00-INDEX.md`:

1. **Host-triple mismatch — fixed.** Bundle claimed `x86_64-unknown-linux-gnu`,
   host reports `x86_64-pc-linux-gnu`.
2. **Compiler generation mismatch — NOT fixable by configuration.** Host Swift
   6.0.3 vs an Xcode 26.5 SDK; `swift-frontend` aborts on an LLVM assertion. Needs
   a Swift matched to the SDK generation.

### OSXCross — planned, never executed

`~/FakeDesktop/adddarwinsdk.md` is a 12-target plan for building OSXCross. Its own
opening states the position plainly:

> *"Your current machine is Debian 13 x86_64 with Swift 6.0.3, CMake and Ninja
> already present, but **no Xcode/`xcrun`, Apple Clang, or OSXCross**."*

`~/FakeDesktop/applesdkpatch` (66 KB) accompanies it. Neither has been run.

The plan also requires **downloading Xcode as a `.xip`**, which carries Apple's
licence terms — a licence characterisation before it can enter the estate, not
just a download.

---

## What this means for the platform matrix

The stated target is installers and build-from-source for **x86 and arm**, with
Apple and Android beyond that.

| Target | Toolchain state |
|---|---|
| Linux x86-64 | **working** — this is what everything builds with today |
| Linux arm64 | OE cross-compilation available; multiconfig **not set up** (`DECISIONS.md` §2 defers it to Phase 19) |
| macOS x86-64 / arm64 | SDK present, **compiler mismatch blocks it** |
| iOS / simulator | same SDK, same block |
| Android | **nothing present** |

**None of this is on the critical path right now.** RavenCalc is 4 of 6 on Linux
x86-64; scipy and scikit-learn are the gap. A second platform cannot be
meaningful before the first one completes.

Recorded so the gap is known rather than assumed away.
