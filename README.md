bitcoin-talk-crawler
====================

This is a simple crawler of the [BitcoinTalk online forum](https://bitcointalk.org/) based on Scrapy.

It collects all messages from all topics in predefined forum categories.

Dependencies
------------

From an activated virtual environment, install the crawler and parser dependencies:

```sh
python -m pip install -r requirements.txt
```

For the optional Tor proxy middleware, install the base dependencies plus Tor support:

```sh
python -m pip install -r requirements_tor.txt
```

The proxy middleware is disabled by default in `bitcoin_talk_crawler/settings.py`.
Using it also requires separately configured Tor and Privoxy services, as described
in the [TorIpChanger documentation](https://pypi.org/project/toripchanger/).

License
-------

This project is licensed under the terms of the Apache License, Version 2.0.
