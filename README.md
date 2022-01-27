# Yerushamayim
## Unofficial Yerushamayim Home Assistant integration and Lovelace card

### :hammer_and_wrench: Integration version: 0.0.13
### :camping: Card version: 0.0.80
<br/>

### Instructions
- Copy `custom_components/yerushamayim` folder to your `custom_components` Home Assistant foler
- Restart Home Assistant
- Add to your configuration yaml:
    ```
    sensor:
    - platform: yerushamayim
    ```
- Restart Home Assistant
- Copy `www/yerushamayim-card.js` to your `www` Home Assistant foler
- Edit your Lovelace dashboard and add to resources `/local/yerushamayim-card.js?v=0.0.79` as JavaScript Module
- Add manual card to your dashboard:
    ```
    type: custom:yerushamayim-card
    entity: sensor.yerushamayim
    ```

### License
Apache-2.0. By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.
