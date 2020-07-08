#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    nrc_exporter
    ~~~~~~~~~~~~
    A program to export and convert NRC activities to GPX.
    :copyright: (c) 2020 by Yasoob Khalid.
    :license: MIT, see LICENSE for more details.
"""
import os
from xml.etree import ElementTree
import sys
import time
import requests
import argparse
import webbrowser
import logging
import gpxpy.gpx
import json
from json.decoder import JSONDecodeError
import datetime
from colorama import Fore, Style
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

__version__ = "0.0.1"
__author__ = "Yasoob Khalid"
__license__ = "MIT"

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "activities")
GPX_FOLDER = os.path.join(os.getcwd(), "gpx_output")
LOGIN_URL = "https://www.nike.com/in/launch?s=in-stock"
MOBILE_LOGIN_URL = (
    "https://unite.nike.com/s3/unite/mobile.html?androidSDKVersion=3.1.0"
    "&corsoverride=https://unite.nike.com&uxid=com.nike.sport.running.droid.3.8"
    "&locale=en_US&backendEnvironment=identity&view=login"
    "&clientId=WLr1eIG5JSNNcBJM3npVa6L76MK8OBTt&facebookAppId=84697719333"
    "&wechatAppId=wxde7d0246cfaf32f7"
)
ACTIVITY_LIST_URL = "https://api.nike.com/sport/v3/me/activities/after_time/0"
ACTIVITY_LIST_PAGINATION = (
    "https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
)
ACTIVITY_DETAILS_URL = (
    "https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"
)

LOGIN_BTN_CSS = (
    "button.join-log-in.text-color-grey.prl3-sm.pt2-sm.pb2-sm.fs12-sm.d-sm-b"
)
EMAIL_INPUT_CSS = "input[data-componentname='emailAddress']"
PASSWORD_INPUT_CSS = "input[data-componentname='password']"
LOGIN_DIALOG_CSS = "div[class='d-md-tc u-full-width u-full-height va-sm-m']"
SUBMIT_BTN_CSS = (
    "div.nike-unite-submit-button.loginSubmit.nike-unite-component input[type='button']"
)


LOGO = """
  _   _ ____   ____                              _            
 | \ | |  _ \ / ___|   _____  ___ __   ___  _ __| |_ ___ _ __ 
 |  \| | |_) | |      / _ \ \/ / '_ \ / _ \| '__| __/ _ \ '__|
 | |\  |  _ <| |___  |  __/>  <| |_) | (_) | |  | ||  __/ |   
 |_| \_|_| \_\\____|  \___/_/\_\ .__/ \___/|_|   \__\___|_|   
                               |_|                            

                                            ~ Yasoob Khalid
                                              https://yasoob.me

"""


def f_message(msg, level="info"):
    """
    Format a message using colors

    Args:
        msg: a msg string
    Returns:
        msg: a colored msg string
    """

    color_map = {
        "info": Style.BRIGHT + Fore.CYAN,
        "error": Fore.RED,
        "debug": Fore.BLUE,
        "logo": Fore.YELLOW,
    }

    return color_map[level] + msg + Style.RESET_ALL


def info(message):
    """
    A simple utility class for formatting and logging info messages

    Args:
        message: the log string
    """
    logger = logging.getLogger(__name__)
    logger.info(f_message(f"[+] {message}", level="info"))


def error(message):
    """
    A simple utility class for formatting and logging info messages

    Args:
        message: the log string
    """
    logger = logging.getLogger(__name__)
    logger.error(f_message(f"[-] ⚠️   {message}", level="error"))


def debug(message):
    """
    A simple utility class for formatting and logging debug messages

    Args:
        message: the log string
    """
    logger = logging.getLogger(__name__)
    logger.debug(f_message(f"[-] 🐛 {message}", level="debug"))


def warning(message):
    """
    A simple utility class for formatting and logging warning messages

    Args:
        message: the log string
    """
    logger = logging.getLogger(__name__)
    logger.warning(f_message(f"[-] ⚠️  {message}", level="error"))


def login(driver, email, password):
    """
    Open the login Page and sign in

    Args:
        driver: a Webdriver instance
        email: the email for nike website
        password: the password associated with the email

    Returns:
        Returns a boolean for whether the login was successful or not
    """

    info("Trying to log in")
    debug("Opening the login page")
    driver.get(LOGIN_URL)
    debug("login page opened")

    login_btn = driver.find_element_by_css_selector(LOGIN_BTN_CSS)
    login_btn.click()

    email_input = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, EMAIL_INPUT_CSS)
        )
    )
    email_input.send_keys(email)

    password_input = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, PASSWORD_INPUT_CSS)
        )
    )
    password_input.send_keys(password)

    submit_btn = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, SUBMIT_BTN_CSS,)
        )
    )
    submit_btn.click()

    debug("Submitted email and password")

    try:
        login_dialog = WebDriverWait(driver, 5).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, LOGIN_DIALOG_CSS)
            )
        )
        info("Seems like login was successful")
        return True

    except:
        warning(
            f"Seems like automated login wasn't successful. You will have to manually provide access tokens"
        )
        return False


def extract_token(driver):
    """
    Extracts access token from the login request

    Args:
        driver: the webdriver instance that was used to do the login

    Returns:
        access_token: the token extracted from request
    """
    for request in driver.requests:
        if "login" in request.path:
            resp_body = request.response.body

    try:
        access_token = json.loads(resp_body)["access_token"]
        info(f"💉 Successfully extracted access token")
        debug(f"Access Token: {access_token}")
    except:
        error(f"Unable to extract access token. You will have to manually pass it in")
    return access_token


def get_access_token(options):
    """
    This function opens the login page and extracts access tokens

    Args:
        options: the options dict which contains login info

    Returns:
        access_token: the bearer token that will be used to extract activities
    """

    login_success = False

    if options["gecko_path"] and not options["manual"]:
        info(f"🚗 Starting gecko webdriver")
        driver = webdriver.Firefox(executable_path=options["gecko_path"])
        driver.scopes = [
            ".*nike.*",
        ]
        login_success = login(driver, options["email"], options["password"])

        if options["debug"]:
            debug(f"Saving screenshot from after login")
            with open("website.png", "wb") as f:
                f.write(driver.get_screenshot_as_png())

    if login_success:
        access_token = extract_token(driver)
    else:
        info(
            f"I will open your web browser and you will have to manually intercept the access tokens.\n"
            f"    You can find more details on how to do this over here: https://git.io/nrc-exporter\n"
            f"    Press 'y' to open up the login url"
        )
        accept = input()
        if not accept == "y":
            info("You didn't want to continue. Exiting")
            sys.exit(0)

        webbrowser.open_new_tab(MOBILE_LOGIN_URL)
        info(f"Please paste access tokens here: \n")
        access_token = input()
        debug(f"Manually entered access token: {access_token}")
        if len(access_token) < 5:
            error(
                f"You didn't paste access tokens. Please provide them using -t or --token argument"
            )
            sys.exit(1)

    info(
        f"Closing the webdriver. From here on we will be using requests library instead"
    )
    driver.quit()
    return access_token


def get_activities_list(options):
    """
    Gets the list of activity IDs from Nike. For now it only saves the runs and not other activities

    Args:
        options: the options dict which contains the access token

    Returns:
        activity_ids: a list of running activity ids
    """

    info("🏃‍♀️  Getting activities list")
    headers = {
        "Authorization": f"Bearer {options['access_token']}",
    }
    debug(f"headers: {headers}")
    activity_ids = []
    page_num = 1
    next_page = ACTIVITY_LIST_URL
    more = True
    while more:
        info(f"📃  opening page {page_num} of activities")
        debug(f"\tActivities page url: {next_page}")
        activity_list = requests.get(next_page, headers=headers)
        if "error_id" in activity_list.json().keys():
            error("Are you sure you provided the correct access token?")
            sys.exit()
        for activity in activity_list.json()["activities"]:
            debug(f"Entry type: {activity['tags'].get('com.nike.running.runtype', '')}")
            if (
                activity["type"] == "run"
                and activity["tags"].get("com.nike.running.runtype", "") != "manual"
            ):
                # activity["tags"]["location"].lower() == "outdoors":
                activity_ids.append(activity.get("id"))

        if activity_list.json()["paging"].get("after_id"):
            page_num += 1
            next_page = ACTIVITY_LIST_PAGINATION.format(
                after_id=activity_list.json()["paging"]["after_id"]
            )
            continue
        break

    info(
        f"🏃‍♀️  Successfully extracted {len(activity_ids)} running activities from {page_num} pages"
    )
    debug(f"ID List: {activity_ids}")
    return activity_ids


def get_activity_details(activity_id, options):
    """
    Extracts details for a specific activity
    """

    info(f"Getting activity details for {activity_id}")
    headers = {
        "Authorization": f"Bearer {options['access_token']}",
    }
    html = requests.get(
        ACTIVITY_DETAILS_URL.format(activity_id=activity_id), headers=headers
    )
    return html.json()


def save_activity(activity_json, activity_id):
    debug(f"Saving {activity_id}.json to disk")
    title = activity_json.get("tags").get("com.nike.name")
    json_path = os.path.join(ACTIVITY_FOLDER, f"{activity_id}.json")
    with open(json_path, "w") as f:
        f.write(json.dumps(activity_json))


def generate_gpx(title, latitude_data, longitude_data, elevation_data, heart_rate_data):
    """
    Parses the latitude, longitude and elevation data to generate a GPX document

    Args:
        title: the title of the GXP document
        latitude_data: A list of dictionaries containing latitude data
        longitude_data: A list of dictionaries containing longitude data
        elevation_data: A list of dictionaries containing elevation data

    Returns:
        gpx: The GPX XML document
    """

    gpx = gpxpy.gpx.GPX()
    gpx.nsmap["gpxtpx"] = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = title
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    points_dict_list = []

    def update_points(points, update_data, update_name):
        """
        Update the points dict list so that can easy create GPXTrackPoint

        Args:
            points: basic points list
            update_data: attr to update points which is a list
            update_name: attr name

        Returns:
            None (just update the points list)
        """
        counter = 0
        for p in points:
            while p["start_time"] >= update_data[counter]["end_epoch_ms"]:
                if counter == len(update_data) - 1:
                    break
                p[update_name] = update_data[counter]["value"]
                counter += 1


    for lat, lon in zip(latitude_data, longitude_data):
        if lat["start_epoch_ms"] != lon["start_epoch_ms"]:
            error(f"\tThe latitude and longitude data is out of order")

        points_dict_list.append({
            "latitude": lat["value"],
            "longitude": lon["value"],
            "start_time":  lat["start_epoch_ms"],
            "time": datetime.datetime.utcfromtimestamp(lat["start_epoch_ms"] / 1000)
            })

    if elevation_data:
        update_points(points_dict_list, elevation_data, "elevation")
    if heart_rate_data:
        update_points(points_dict_list, heart_rate_data, "heart_rate")

    for p in points_dict_list:
        # delete useless attr
        del p["start_time"]
        if p.get("heart_rate") is None:
           point = gpxpy.gpx.GPXTrackPoint(**p)
        else:
            heart_rate_num = p.pop("heart_rate")
            point = gpxpy.gpx.GPXTrackPoint(**p)
            gpx_extension_hr = ElementTree.fromstring(f"""<gpxtpx:TrackPointExtension xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
                <gpxtpx:hr>{heart_rate_num}</gpxtpx:hr>
                </gpxtpx:TrackPointExtension>
            """)
            point.extensions.append(gpx_extension_hr)
        gpx_segment.points.append(point)

    return gpx.to_xml()


def parse_activity_data(activity):
    """
    Parses a NRC activity and returns GPX XML

    Args:
        activity: a json document for a NRC activity

    Returns:
        gpx: the GPX XML doc for the input activity
    """

    debug(f"Parsing activity: {activity.keys()}")
    lat_index = None
    lon_index = None
    ascent_index = None
    heart_rate_index = None
    for i, metric in enumerate(activity["metrics"]):
        if metric["type"] == "latitude":
            lat_index = i
        if metric["type"] == "longitude":
            lon_index = i
        if metric["type"] == "ascent":
            ascent_index = i
        if metric["type"] == "heart_rate":
            heart_rate_index = i

    debug(
        f"\tActivity {activity['id']} contains the following metrics: {activity['metric_types']}"
    )
    if not any([lat_index, lon_index]):
        warning(
            f"\tThe activity {activity['id']} doesn't contain latitude/longitude information"
        )
        return None

    latitude_data = activity["metrics"][lat_index]["values"]
    longitude_data = activity["metrics"][lon_index]["values"]
    elevation_data = None
    heart_rate_data = None
    if ascent_index:
        elevation_data = activity["metrics"][ascent_index]["values"]
    if heart_rate_index:
        heart_rate_data = activity["metrics"][heart_rate_index]["values"]

    title = activity["tags"].get("com.nike.name")

    gpx_doc = generate_gpx(title, latitude_data, longitude_data, elevation_data, heart_rate_data)
    info(f"✔ Activity {activity['id']} successfully parsed")
    return gpx_doc


def save_gpx(gpx_data, activity_id):
    """
    Saves the GPX data to a file on disk

    Args:
        gpx_data: the GPX XML doc
        activity_id: the name of the file
    """

    file_path = os.path.join(GPX_FOLDER, activity_id + ".gpx")
    with open(file_path, "w") as f:
        f.write(gpx_data)


def get_gecko_path():
    """
    Check if geckodriver exists in the code directory. If it does, return
    the absolute path. If not, exit program with an error

    Returns:
        path: the absolute path to geckodriver
    """
    debug(f"Checking if geckodriver is in path or not")
    if os.path.exists("geckodriver"):
        return os.path.join(os.getcwd(), "geckodriver")
    else:
        error(
            "Gecko driver doesn't exist. I will not try to automatically extract access tokens"
        )
        return None


def arg_parser():
    """
    Parses the input arguments

    Returns:
        options: A dictionary containing either the bearer token or email and password
    """

    ap = argparse.ArgumentParser(
        description="Login to Nike Run Club and download activity data in GPX format"
    )
    ap.add_argument("-e", "--email", help="your nrc email")
    ap.add_argument("-p", "--password", help="your nrc password")
    ap.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
    ap.add_argument("-t", "--token", help="your nrc token", required=False)
    ap.add_argument(
        "-i", "--input", nargs='+', help="A directory or directories containing NRC activities in JSON format."
        "You can also provide individual NRC JSON files"
    )
    args = ap.parse_args()

    if args.verbose:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

    debug(f"Passed in arguments:")
    debug(f"\t\tEmail: {args.email}")
    debug(f"\t\tPassword: {args.password}")
    debug(f"\t\tToken: {args.token}")

    options = {}
    options["debug"] = args.verbose
    options["manual"] = False
    if args.input:
        if all([os.path.exists(i) for i in args.input]):
            options["activities_dirs"] = args.input
        if all([i.endswith(".json") for i in args.input]):
            options["activities_files"] = args.input
    elif args.token:
        options["access_token"] = args.token
    elif args.email and args.password:
        options["email"] = args.email
        options["password"] = args.password
    else:
        options["manual"] = True
        info(
            "You will have to manually provide the access tokens in a later step because you\n"
            "     did not provide email/password or access tokens while running the program."
        )

    return options


def init_logger():
    """
    Initializes the logger

    Returns:
        logger: A logging object
    """

    if not os.path.exists(GPX_FOLDER):
        debug("Created a folder for GPX data: {GPX_FOLDER}")
        os.mkdir(GPX_FOLDER)
    if not os.path.exists(ACTIVITY_FOLDER):
        debug("Created a folder for activity data: {ACTIVITY_FOLDER}")
        os.mkdir(ACTIVITY_FOLDER)

    logging.basicConfig(
        format="%(message)s", level=logging.INFO,
    )
    # Set this to True if you want to see the actual requests captured by seleniumwire
    logging.getLogger("seleniumwire").propagate = False

    print(f_message(LOGO, level="logo"))


def main():
    """
    Main will be called if the script is run directly
    """

    init_logger()
    options = arg_parser()

    info("Starting NRC Exporter")

    start_time = time.time()

    if options.get("email") or options.get("manual"):
        info("💉  Email and password provided so will try to extract access tokens")
        options["gecko_path"] = get_gecko_path()
        options["access_token"] = get_access_token(options)

    if options.get("access_token"):
        activity_ids = get_activities_list(options)
        for activity in activity_ids:
            activity_details = get_activity_details(activity, options)
            save_activity(activity_details, activity_details["id"])

    activity_folders = options.get("activities_dirs", [ACTIVITY_FOLDER])
    activity_files = options.get("activities_files", [])
    if not activity_files:
        for folder in activity_folders:
            # add path to every file in folder
            activity_files.extend([os.path.join(folder, f) for f in os.listdir(folder)])
        info(f"Parsing activity JSON files from the {','.join(activity_folders)} folders")

    total_parsed_count = 0
    for file in activity_files:
        with open(file, "r") as f:
            try:
                json_data = json.loads(f.read())
            except JSONDecodeError:
                error(f"Error occured while parsing file {file_location}")
        parsed_data = parse_activity_data(json_data)
        if parsed_data:
            total_parsed_count += 1
            save_gpx(parsed_data, json_data["id"])

    info(
        f"Parsed {total_parsed_count} activities successfully out of {len(activity_files)} total run activities"
    )
    info(
        f"Total time taken: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}"
    )


if __name__ == "__main__":
    main()
