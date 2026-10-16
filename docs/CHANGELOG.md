# CHANGELOG


## v0.4.0 (2026-10-16)

### Code Style

- **ui**: Show account name in a box
  ([`064a1be`](https://github.com/omadson/claude-kiosk/commit/064a1befded2a31f229be75d3f771837f8bd7273))

### Documentation

- Document extra Claude accounts
  ([`3e3bfd4`](https://github.com/omadson/claude-kiosk/commit/3e3bfd4e18989fddf0b9273feeed5a568c39cfcb))

### Features

- **cli**: Add --add-account/--remove-account to config
  ([`45c4f42`](https://github.com/omadson/claude-kiosk/commit/45c4f4220db661742d005854cca221906d04bd41))

- **server**: Fetch usage for extra Claude accounts
  ([`c7b461d`](https://github.com/omadson/claude-kiosk/commit/c7b461d271822e35a7d80353a83f8091012355e2))

- **ui**: Add one usage screen per extra account
  ([`ae54728`](https://github.com/omadson/claude-kiosk/commit/ae54728a322e09b6f1e7427dde334d2864ec19b5))


## v0.3.0 (2026-10-11)

### Bug Fixes

- Don't count skipped focus sessions as completed
  ([`e463be1`](https://github.com/omadson/claude-kiosk/commit/e463be1395cb8ef2b90ab13767f8ee864eb2e62d))

### Build System

- Refresh uv.lock on release
  ([`1cdbf6c`](https://github.com/omadson/claude-kiosk/commit/1cdbf6cca4e0c2f5519893c8392568e12061c330))

- Sync uv.lock with package version 0.2.1
  ([`346fc2e`](https://github.com/omadson/claude-kiosk/commit/346fc2e0835a8463d7e7969e5088c593d040a680))

### Documentation

- Mention pomodoro screen
  ([`7330f40`](https://github.com/omadson/claude-kiosk/commit/7330f40c9464c3bc28d12dedf1fc5042734b88f9))

### Features

- Add pomodoro screen
  ([`029df89`](https://github.com/omadson/claude-kiosk/commit/029df89d2e9d2a271f6931a2836d0bdbc76d981d))

- Persist pomodoro state and alert on phase end
  ([`5ca0672`](https://github.com/omadson/claude-kiosk/commit/5ca06729431607f55384049f226c1cdc6b6bcba3))


## v0.2.1 (2026-10-01)

### Bug Fixes

- Zero expired usage windows when serving cached data
  ([`b13aa45`](https://github.com/omadson/claude-kiosk/commit/b13aa45ff5634e69cfb8beb7d7658915967b2f61))


## v0.2.0 (2026-09-27)

### Continuous Integration

- Add docs deployment workflow
  ([`effe39b`](https://github.com/omadson/claude-kiosk/commit/effe39ba07f3382a5514465919e41a545e0b18af))

### Documentation

- Fix downloads badge and remove CI/coverage badges
  ([`b0703c3`](https://github.com/omadson/claude-kiosk/commit/b0703c31723f2a6076a3f0dd1d154cb8f42f4f6f))

- Reorder README badges, PyPI before docs
  ([`390aa26`](https://github.com/omadson/claude-kiosk/commit/390aa26daf3563289462f168e954895b19668516))

### Features

- Show reverse-geocoded location instead of hardcoded city
  ([`16363e6`](https://github.com/omadson/claude-kiosk/commit/16363e6510ad7bf9abbeebe92beb0e64893a5768))


## v0.1.0 (2026-09-19)

### Features

- Add claude-kiosk CLI
  ([`6b2d317`](https://github.com/omadson/claude-kiosk/commit/6b2d317bfa4b6dabe599bdb696a37371a2c165fa))
