# Precious Metal Prices for Homeassistant

I didn't find a similar integartion or any easier way to get metal prices into homeassistant so I wrote this. 

This integration provides the same combinations of metal/weight/currency as BullioByPost does with their live charts.

### Example card

## Features

- Provides sensors for gold, silver, platinum and palladium spot prices.
- Each metal has its value in grams, troy ounces and kilograms.
- Each of these is also provided in EUR, USD and GBP.

In total the integration provides 36 sensors.

If there is a need for other currencies, they are easy to add too.

## Setup

### HACS (Recommended)

### Manual

## Backend

Please note: All data is provided without any guarantee.

- Price data is fetched from gold.de API: https://www.gold.de/chartgenerator/#api
- Currency conversion rates are fetched using this great project: https://github.com/fawazahmed0/exchange-api
