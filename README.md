# NRC Exporter

## Summary

Download your runs from Nike Run Club and convert them to GPX format that can be imported in other running apps.

## Introduction

There was a time when I was a huge fan of Nike Run Club. It was the first running application I got hooked on when I started this sport. Later on down the road I realized that most of my new running friends were using Strava. I wanted to move my old runs from NRC to Strava but couldn't find a way to do it. Nike had recently removed the option to extract your data so I was stuck.

I did what any programmer would do. I spent a weekend trying to whip up a Nike Run Club data exporter. This program extracts all of your runs which have associated GPS data and converts them into the GPX format that can be imported to Strava.

I have made this program in a modular way with helpful docstrings for all functions. You are more than welcome to add extra features you need in this program. If you aren't tech-savy and/or want my help please open up an issue and we can figure it out from there.

## Installation

You can either install the package from [PyPI](https://pypi.org/project/nrc-exporter/) or [source](https://github.com/yasoob/nrc-exporter).

### Using pip

The PyPI method is the easiest as it installs the dependencies as well (other than geckodriver). Run the following command to install from PyPI:

```
$ pip install nrc-exporter
```

If everything goes well, you should be able to run this command:

```
$ nrc-exporter --help

  _   _ ____   ____                              _
 | \ | |  _ \ / ___|   _____  ___ __   ___  _ __| |_ ___ _ __
 |  \| | |_) | |      / _ \ \/ / '_ \ / _ \| '__| __/ _ \ '__|
 | |\  |  _ <| |___  |  __/>  <| |_) | (_) | |  | ||  __/ |
 |_| \_|_| \_\____|  \___/_/\_\ .__/ \___/|_|   \__\___|_|
                               |_|

                                            ~ Yasoob Khalid
                                              https://yasoob.me


usage: nrc-exporter [-h] [-e EMAIL] [-p PASSWORD] [-v] [-t TOKEN] [-i INPUT]

Login to Nike Run Club and download activity data in GPX format

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        your nrc email
  -p PASSWORD, --password PASSWORD
                        your nrc password
  -v, --verbose         print verbose output
  -t TOKEN, --token TOKEN
                        your nrc token
  -i INPUT, --input INPUT
                        A directory containing NRC activities in JSON format
```

### From Source

Just clone the repo, install the dependencies and run it.

- Clone it:

```
$ git clone git@github.com:yasoob/nrc-exporter.git
```

- Install dependencies:

```
$ cd nrc-exporter
$ pip install -r requirements.txt
```

- Add Geckodriver in path

The automated access token extraction makes use of selenium and geckodriver. I used geckodriver instead of Chrome because Chrome (selenium) was being blocked by Nike (Akamai Bot Manager) but geckodriver was not. This is an optional step. If you want to try automated extraction make sure you have downloaded the geckodriver from [here](https://github.com/mozilla/geckodriver/releases) and the binary is in your PATH.

- Run it:

```
python nrc_exporter.py --help
```

If everything goes well you will see the following text:

```
  _   _ ____   ____                              _
 | \ | |  _ \ / ___|   _____  ___ __   ___  _ __| |_ ___ _ __
 |  \| | |_) | |      / _ \ \/ / '_ \ / _ \| '__| __/ _ \ '__|
 | |\  |  _ <| |___  |  __/>  <| |_) | (_) | |  | ||  __/ |
 |_| \_|_| \_\____|  \___/_/\_\ .__/ \___/|_|   \__\___|_|
                               |_|

                                            ~ Yasoob Khalid
                                              https://yasoob.me


usage: __main__.py [-h] [-e EMAIL] [-p PASSWORD] [-v] [-t TOKEN] [-i INPUT]

Login to Nike Run Club and download activity data in GPX format

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        your nrc email
  -p PASSWORD, --password PASSWORD
                        your nrc password
  -v, --verbose         print verbose output
  -t TOKEN, --token TOKEN
                        your nrc token
  -i INPUT, --input INPUT
                        A directory containing NRC activities in JSON format
```

## Usage:

You have multiple ways to run this application. You can either provide an email password combination, access tokens for Nike or a directory containing NRC activities in JSON format.

- Email/Password

This is probably the easiest way to run the application. The program will try to automatically extract the access_tokens for NRC by logging you in using Selenium and intercepting the requests. You will have to run nrc_exporter like this:

```
$ nrc-exporter -e yasoob@example.com -p sample_password
```

This method will probably be blocked by Nike in the near future. If it doesn't work use the access tokens method described below.

- Access Tokens

This is useful for when the program is unable to extract the tokens automatically. You will have to manually provide the access tokens to the program. If you don't know where to get the access tokens from, just run the program without any arguments and it should automatically open the URL where you can log in. For extracting the tokens from that page check out [these instructions](#extracting-access-tokens). Once you have the tokens, you can run nrc_extractor like this:

```
$ nrc-exporter -i <access_token>
```

- Activities folder

Some of you might have already downloaded your NRC runs data using [this script](https://gist.github.com/niw/858c1ecaef89858893681e46db63db66) and are now wondering how to convert that JSON data to GPX data. Put all of those activity JSON files in a folder and pass that folder's name to nrc_extractor. Let's suppose you put all of those files in the `activities` folder. It should look something like this:

```
$ tree activities
activities
├── 0019f189-d32f-437f-a4d4-ef4f15304324.json
├── 0069911c-2cc8-489b-8335-8e613a81124s.json
├── 01a09869-0a95-49f2-bd84-75065b701c33.json
└── 07e1fa42-a9a9-4626-bbef-60269dc4a111.json
```

Now you can run `nrc_extractor` like this:

```
$ nrc-exporter -i activities
```

## Extracting access tokens

Nike uses Akamai Bot Manager which doesn't allow scripts to automatically log users in and extract the access tokens. Sometimes you might be lucky and automated token extraction works but mostly you will find the automated token extraction to be broken. Luckily, manually extracting the access token isn't too hard.

Just open up your favorite browser and head over to this [login url](https://unite.nike.com/s3/unite/mobile.html?androidSDKVersion=3.1.0&corsoverride=https://unite.nike.com&uxid=com.nike.sport.running.droid.3.8&locale=en_US&backendEnvironment=identity&view=login&clientId=WLr1eIG5JSNNcBJM3npVa6L76MK8OBTt&facebookAppId=84697719333&wechatAppId=wxde7d0246cfaf32f7) and log in.

Submitting the form will not do much. You will just have a blank page in front of you but you will be logged in. Now in order to extract the access tokens, open up developer tools. You can search online about how to open the developer tools for your specific browser. Once the developer tools are open, click on the `Console` and type this:

```
JSON.parse(window.localStorage.getItem('com.nike.commerce.snkrs.web.credential')).access_token
```

This should print your access tokens on screen. If this doesn't work and/or gives you errors, just click on storage and check out local storage. You should be able to `access_tokens` as part of the value for a particular key. It should look something like this:

![Extract key](https://raw.githubusercontent.com/yasoob/nrc-exporter/master/screenshots/token_extraction.png)

Now copy these `access_tokens` and provide them to the program.

## Limitations

This was a weekend project so there are definitely a lot of rough edges to this script. Try it at your own risk. I have extracted my runs successfully with this program so I am hopeful that it will work for you too. In case it fails please open up an issue and I will take a look.

For now, one major isssue is that the script does not correctly add elevation data to the GPX file. NRC provides us with the ascent and descent data of different runs but I am not sure of the math that is required to convert that into actual elevation data. This data wasn't particularly important for me to maintain for historic runs so I did not spend a lot of time on it. You are more than welcome to open up a PR if you know how to do it.


## Screenshots

Who doesn't love screenshots?

- Initial run

![help message](https://raw.githubusercontent.com/yasoob/nrc-exporter/master/screenshots/help.png)

## Release

This is for my own documentation. There are three steps involved with releasing a new version to PyPI after updating the code.

- Increment the version number in `setup.py`
- Build the distribution package

```
python setup.py sdist bdist_wheel
```

- Upload to PyPI:

```
python -m twine upload --skip-existing --repository pypi dist/*
```

## License

This program is distributed under the MIT license. You are more than welcome to take a look, modify and redistribute it (even for commercial purposes). Just make sure that the LICENSE file stays intact and you redistribute it under the same license.

```
MIT License

Copyright (c) 2020 M.Yasoob Ullah Khalid ☺

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
