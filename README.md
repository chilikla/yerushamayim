# Yerushamayim
## Unofficial Yerushamayim Home Assistant integration and Lovelace card

### Instructions
- Copy `custom_components/yerushamayim` folder to your `custom_components` Home Assistant foler
- Add to your configuration yaml:
    ```
    sensor:
    - platform: yerushamayim
    ```
- Copy `www/yerushamayim-card.js` to your `www` Home Assistant foler
- Edit your Lovelace dashboard and add to resources `/local/yerushamayim-card.js?v=1` as JavaScript Module
- Add manual card to your dashboard:
    ```
    type: custom:yerushamayim-card
    entity: sensor.yerushamayim
    ```

### License
Apache-2.0. By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.
