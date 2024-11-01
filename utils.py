import datetime
import json
import pytz
import requests


BASE_URL = "https://pypi.org/pypi"

DEPRECATED_PACKAGES = {
    "BeautifulSoup",
    "bs4",
    "distribute",
    "django-social-auth",
    "nose",
    "pep8",
    "pycrypto",
    "pypular",
    "sklearn",
}

SESSION = requests.Session()


def get_json_url(package_name):
    return BASE_URL + "/" + package_name + "/json"


def annotate_wheels(packages):
    print("Getting wheel data...")
    num_packages = len(packages)
    for index, package in enumerate(packages):
        has_arm = False
        has_win_bin = False
        has_any = False
        print(index + 1, num_packages, package["name"])
        has_wheel = False
        url = get_json_url(package["name"])
        response = SESSION.get(url)
        if response.status_code != 200:
            print(" ! Skipping " + package["name"])
            continue
        data = response.json()
        #package["anyfile"] = ""
        #package["armfile"] = ""
        #package["winfile"] = ""          
        for download in data["urls"]:
            if download["packagetype"] == "bdist_wheel":
                has_wheel = True
                parts = download['filename'].split('-')
                if parts:
                    platform = parts[-1].split('.')[0]
                    if platform == 'any':
                        #package["anyfile"] = download['filename']
                        has_any = True
                    elif platform in ['win_amd64', 'win_ia64']:
                        #package["winfile"] = download['filename']
                        has_win_bin = True
                    elif platform == 'win_arm64':
                        #package["armfile"] = download['filename']
                        has_arm = has_win_bin = True               
                #break
        package["wheel"] = has_wheel
        package["complete"] = has_arm or (has_any and not has_win_bin)     
        package["usable"] = has_arm or has_any              
        # Display logic. I know, I'm sorry.
        package["value"] = 1
        package["icon"] = "\u2713"  # Check mark  
        if has_wheel:
            if has_arm:
                package["css_class"] = "primary"
                package["title"] = "This package provides a WinARM64 binary wheel."                  
            elif has_win_bin:
                if has_any:
                    package["css_class"] = "warning"
                    package["title"] = "This package provides pure-Python and Windows binary wheels but not for WinARM64."
                else:
                    package["css_class"] = "danger"
                    package["title"] = "This package provides only binary wheels but none for WinARM64."
                    package["icon"] = "\u2717"  # Ballot X
            else:
                package["css_class"] = "success"
                package["title"] = "This package is pure Python and provides a wheel."                
        else:
            package["css_class"] = "default"
            package["icon"] = "\u2717"  # Ballot X
            package["title"] = "This package has no wheel archives uploaded " "(yet!)."


def get_top_packages():
    print("Getting packages...")

    with open("top-pypi-packages.json") as data_file:
        packages = json.load(data_file)["rows"]

    # Rename keys
    for package in packages:
        package["downloads"] = package.pop("download_count")
        package["name"] = package.pop("project")

    return packages


def not_deprecated(package):
    return package["name"] not in DEPRECATED_PACKAGES


def remove_irrelevant_packages(packages, limit):
    print("Removing cruft...")
    active_packages = list(filter(not_deprecated, packages))
    return active_packages[:limit]


def save_to_file(packages, file_name):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    with open(file_name, "w") as f:
        f.write(
            json.dumps(
                {
                    "data": packages,
                    "last_update": now.strftime("%A, %d %B %Y, %X %Z"),
                },
                indent=1,
            )
        )
