# SmartCocoon Python API

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![logo](logo.png)

This Python library allows you to control [SmartCocoon fans](https://mysmartcocoon.com/).

## Status

This is not an official API from SmartCocoon and is in the the very early stages of developement.

This API is built for the main purpose of integrating into Home Assistant but can be used independently.

### Supported devices

- SmartCocoon Smart Vents

## Features

The following feature are supported:

- Connect to the SmartCocoon cloud service
- Obtain configuration data as it has been set up through the SmartCocoon mobile app
- Ability to control fans
  - Turn on/off
  - Set speed
  - Set Auto mode
  - Set Eco mode

## Examples

You can refer to the tests/test_integration.py to see an example of integration with the
SmartCocoon API

Copy the tests/template.env* to \_tests/.env* file and update the account information with your your SmartCocoon account information:

```python
USERNAME="user@domain.com"
PASSWORD="mypassword"
FAN_ID="abc123"
```

## Work to do

- The fans are using MQTT but this is not being leveraged yet
- Discovery has not been implemented, not sure if this is possible
- Fan status will currently require polling if the fan is changed directly in the app

[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/davepearce
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/davecpearce/pysmartcocoon.svg?style=for-the-badge
[commits]: https://github.com/davecpearce/pymywatertoronto/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/davecpearce/pysmartcocoon.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40davecpearce-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/davecpearce/pysmartcocoon.svg?style=for-the-badge
[releases]: https://github.com/davecpearce/pysmartcocoon/releases
[user_profile]: https://github.com/davecpearce
