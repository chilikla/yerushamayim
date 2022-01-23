import {
  LitElement,
  html,
  css
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

function loadCSS(url) {
  const link = document.createElement("link");
  link.type = "text/css";
  link.rel = "stylesheet";
  link.href = url;
  document.head.appendChild(link);
}

loadCSS("https://fonts.googleapis.com/css2?family=Rubik&display=swap");

class YerushamayimCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {}
    };
  }

  render() {    
    console.log(this.hass);
    const entityId = this.config.entity;
    const state = this.hass.states[entityId];
    const stateStr = state ? state.state : 'unavailable';
    const logUrl = this.hass.states['sun.sun'].state === 'below_horizon' ? 'https://www.02ws.co.il/img/logo_night.png' : 'https://www.02ws.co.il/img/logo.png';

    return html`
      <ha-card>
        <div class="container">
        ${ (stateStr !== 'unavailable' && state.attributes.current_temp !== null)
            ? html`
              <div id="left">
                <div>
                  <img class="icon" src="${state.attributes.status_icon}" title="${state.attributes.status_icon_info}">
                </div>
                <div id="icon-info" dir="rtl">
                  <bdi>${state.attributes.status_title}</bdi>
                </div>
                <div>
                  <div class="forecast-icon">
                    <img src="https://www.02ws.co.il/img/night_icon_night.png">
                    <img src="https://www.02ws.co.il/img/noon_icon_night.png">
                    <img src="https://www.02ws.co.il/img/morning_icon_night.png">
                  </div>
                  <div class="forecast-icon">
                    <bdi>${state.attributes.night_temp} °C</bdi>
                    <bdi>${state.attributes.noon_temp} °C</bdi>
                    <bdi>${state.attributes.morning_temp} °C</bdi>
                  </div>
                  <div class="forecast-icon">
                    <img src="${state.attributes.night_cloth_icon}" title="${state.attributes.night_cloth_info}">
                    <img src="${state.attributes.noon_cloth_icon}" title="${state.attributes.noon_cloth_info}">
                    <img src="${state.attributes.morning_cloth_icon}" title="${state.attributes.morning_cloth_info}">
                  </div>
                </div>
              </div>
              <div id="right" dir="rtl">
                <img class="logo" src="${logUrl}">
                <div class="block" id="current-temp">
                  <bdi>
                    ${state.attributes.current_temp}
                    <span>°C </span>
                  </bdi>
                </div>
                ${state.attributes.feels_like_temp
                  ? html`<div class="block">
                    <span>מרגיש כמו: </span>
                    <bdi>${state.attributes.feels_like_temp} °C</bdi>
                  </div>`
                  : html`<div class="block">
                    <span>מרגיש כמו: </span>
                    <bdi>${state.attributes.current_temp} °C</bdi>
                  </div>`
                }
                <div>
                  <bdi>${state.attributes.forecast_text}</bdi>
                </div>
              </div>
            `
            : html`No data to show`
        }
        </div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  static get styles() {
    return css`
      :host {
        font-family: "Rubik", "Open Sans", cursive;
      }
      .container {
        background: linear-gradient(180deg, #3b4d5b 0%, #5e6d97 100%);
        border-radius: var(--ha-card-border-radius, 4px);
        box-shadow: var( --ha-card-box-shadow, 0px 2px 1px -1px rgba(0, 0, 0, 0.2), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12) );
        padding: 16px;
        font-size: 16px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
      }
      #left {
        display: flex;
        flex-direction: column;
        flex-basis: 45%;
      }
      img.icon {
        height: 60px;
        padding-bottom: 5px;
      }
      #icon-info {
        text-align: left;
        margin-bottom: 15px;
      }
      #forecast-icons {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
      }
      .forecast-icon {
        flex-direction: row;
        justify-content: space-between;
        display: flex;
        align-items: center;
      }
      .forecast-icon:not(:last-child) {
        margin-bottom: 5px;
      }
      img.logo {
        width: 50px;
        margin-bottom: 10px;
        filter: brightness(0) invert(1);
      }
      #right {
        flex-basis: 55%;
      }
      .block {
        margin-bottom: 10px;
      }
      #current-temp {
        font-size: 24px;
      }
    `;
  }
}

customElements.define('yerushamayim-card', YerushamayimCard);