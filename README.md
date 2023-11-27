# Thetadata Python API

The [Thetadata](https://thetadata.net) Python API provides low latency US equities & options data that may be used for
market research or algorithmic trading applications.

Please see this repository's [documentation](https://thetadata-api.github.io/thetadata-python) and [GitHub](https://github.com/ThetaData-API/thetadata-python) for more details.

## Installation

Java 11 or higher is required. If you are on Windows, Java 19 will automatically be installed for you. Python 10 or higher is **highly** recommended.

`pip install thetadata`

Please see our [official installation instructions](https://thetadata-api.github.io/thetadata-python/tutorials/#installation)
to get started.

## FYIs

- Part of our delivery process involves compressing the data sent over the internet to 1/30th of it's actual size. The [Theta Terminal](https://http-docs.thetadata.us/docs/theta-data-rest-api-v2/pmaq5r1wq98zk-introduction) is automatically downloaded / launched by this API.
- This API lacks important features such as concurrent requests, index options greeks, and bulk snapshots. To use those, please use our well maintenance [REST API](https://http-docs.thetadata.us), which can be used in any language.
## Contributing

We welcome all feedback, whether it comes in the form of Github issues, pull requests, or pings in our [Discord](https://discord.thetadata.us)!
