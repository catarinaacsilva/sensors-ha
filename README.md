# Sensors simulation to use on Home Assistant

Source of dataset: [Kaggle](https://www.kaggle.com/garystafford/environmental-sensor-data-132k)

## Requirements


## Configurations

Due to the version 2 of Mosquitto it is necessary to add the following lines on Mosquitto configurations.

1. In `mosquitto/mosquittoconf/mosquitto.conf` add:

    1.1 `listener 1883`
    1.2 `allow_anonymous true`

## Authors

* **Catarina Silva** - [catarinaacsilva](https://github.com/catarinaacsilva)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details