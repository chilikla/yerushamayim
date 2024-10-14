# Yerushamayim
## Unofficial Yerushamayim Home Assistant integration and Lovelace card

### :hammer_and_wrench: Version: v1.0.19
<br/>
![screenshot](https://raw.githubusercontent.com/chilikla/yerushamayim/main/screenshot.png)

### Instructions
- Add this repo to HACS' Custom repositories: `https://github.com/chilikla/yerushamayim`
- Restart Home Assistant
- Add card to your dashboard

### Old Instructions
- Copy `dist/custom_components/yerushamayim` folder to your `custom_components` Home Assistant folder
- Restart Home Assistant
- Add to your configuration yaml:
    ```
    sensor:
    - platform: yerushamayim
    ```
- Restart Home Assistant
- Copy `dist/www/yerushamayim-card.js` or `dist/www/yerushamayim-card-local.js` to your `www` Home Assistant folder
- Edit your Lovelace dashboard and add to resources `/local/yerushamayim-card.js?v=1.0.0.` as JavaScript Module
- Add manual card to your dashboard:
    ```
    type: custom:yerushamayim-card
    entity: sensor.yerushamayim
    ```

### License
Apache-2.0. By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.
