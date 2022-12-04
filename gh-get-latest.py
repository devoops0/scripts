#!/usr/bin/env python3

import requests as req
import sys
from simple_term_menu import TerminalMenu
import shutil
import urllib.request

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    usage_str = f"""
========== Usage: ==========
{sys.argv[0]} <github_repo_url>
example:
    {sys.argv[0]} https://github.com/derailed/k9s
    """

    eprint(usage_str)
    sys.exit(1)


def select_asset(owner='', repo=''):
    download_url = ""
    file_name = ""
    assets = {}

    if owner == "" or repo == "":
        eprint(f"We need owner and repo to grab the latest release. Got owner={owner} and repo={repo}")
        return download_url

    assets = grab_latest_from_gh_api(owner, repo)

    asset_names = list(assets.keys())
    if len(asset_names) > 0:
        tmenu = TerminalMenu(asset_names, title="Select Asset to Dwonload", search_case_sensitive=False, show_search_hint=True, clear_screen=True)
        selection = tmenu.show()
        file_name = asset_names[selection]
        download_url = assets[file_name]

    return file_name, download_url
    

def grab_latest_from_gh_api(owner='', repo=''):
    github_api_url_base = "https://api.github.com/repos"
    github_api_url_latest_path = "releases/latest"
    assets = {}

    if owner == "" or repo == "":
        eprint(f"We need owner and repo to grab the latest release. Got owner={owner} and repo={repo}")

    latest_release_url = f"{github_api_url_base}/{owner}/{repo}/{github_api_url_latest_path}"

    res = req.get(latest_release_url)
    if res.status_code != 200:
        eprint(f"Error grabbing latest version info from Github. Got {res.status_code}")
        return ""

    asset_list = res.json()
    for asset in asset_list["assets"]:
        if asset['name'] and asset['name'] != "" and asset['browser_download_url'] and asset['browser_download_url'] != "":
            assets[asset['name']] = asset['browser_download_url']

    return assets


def download_latest_from_gh(file_name='', download_url=''):
    if file_name == "" or download_url == "":
        eprint(f"Need filename (got: {file_name}) and download_url (got: {download_url})")
        sys.exit(1)

    print(f"Downloading {download_url}")
    with urllib.request.urlopen(download_url) as res, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(res, out_file)

def split_gh_url(repo_url=''):
    split_url = repo_url.split("/")
    repo = split_url[-1]
    owner = split_url[-2]
    if repo == "/":
        repo = split_url[-2]
        owner = split_url[-3]

    return owner, repo

def main():

    if len(sys.argv) <= 1:
        usage()

    repo_url = sys.argv[1]

    owner, repo = split_gh_url(repo_url)

    file_name, download_url = select_asset(owner, repo)
    if file_name =="" or download_url == "":
        eprint(f"Couldn't find a suitable download_url for latest release from Github.")
        sys.exit(1)

    download_latest_from_gh(file_name, download_url)


if __name__ == "__main__":
    main()
