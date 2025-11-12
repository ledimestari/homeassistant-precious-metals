# Precious Metal Prices for Homeassistant

I didn't find a similar integration or any easier way to get metal prices into homeassistant, so I wrote this. 

This integration provides the same combinations of metal/weight/currency as BullioByPost does with their website live charts.

### Example card
<img width="524" height="695" alt="image" src="https://github.com/user-attachments/assets/8a0d3a30-d087-4fb4-9baa-30fe16af3688" />


## Features

- Provides sensors for gold, silver, platinum and palladium spot prices.
- Each metal has its value in grams, troy ounces and kilograms.
- Each of these is also provided in EUR, USD and GBP.

In total the integration provides 36 sensors.

If there is a need for other currencies, they are easy to add too.

## Setup

### HACS (Recommended)

Click the button below to install via HACS.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ledimestari&repository=homeassistant-precious-metals&category=integration)

### Manual

Copy the "homeassistant-precious-metals" directory into the "custom_components" directory of your homeassistant install.

> [!TIP]
This integration has nothing you need to configure or set up. After adding the integration you have all the sensors available by default.

## Backend

Please note: All data is provided without any guarantee.

- Price data is fetched from gold.de API: https://www.gold.de/chartgenerator/#api
- Currency conversion rates are fetched using this great project: https://github.com/fawazahmed0/exchange-api
