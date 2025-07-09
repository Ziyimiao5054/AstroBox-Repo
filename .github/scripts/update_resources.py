import os
import json
import csv
import requests
from urllib.parse import urlparse

JSDELIVR_PREFIX = 'https://purge.jsdelivr.net/gh/AstralSightStudios/AstroBox-Repo@master/'
CDN_TARGETS = ['banner.json', 'devices.json5', 'index.csv']
RESOURCES_DIR = 'resources'

def purge_jsdelivr(file_path):
    url = JSDELIVR_PREFIX + file_path
    print(f"Purging {url}")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error purging {url}: {e}")

def download_and_purge_repo_files(repo_url):
    """
    访问 repo_url，下载 manifest 和其中引用的资源，然后刷新对应 CDN。
    """
    try:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            print(f"Invalid repo URL: {repo_url}")
            return
        owner, repo = parts[:2]
        base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/"

        manifest_url = base_url + "manifest.json"
        r = requests.get(manifest_url)
        r.raise_for_status()
        manifest = r.json()
        purge_jsdelivr_path = f"{repo}/master/manifest.json"
        purge_jsdelivr(purge_jsdelivr_path)

        references = []
        for key in ['icon', 'cover', 'preview']:
            if key in manifest:
                references.append(manifest[key])
        if 'files' in manifest and isinstance(manifest['files'], list):
            references.extend(manifest['files'])

        for ref in references:
            purge_path = f"{repo}/master/{ref}"
            purge_jsdelivr(purge_path)

    except Exception as e:
        print(f"Failed to process repo {repo_url}: {e}")

def process_resources():
    for filename in os.listdir(RESOURCES_DIR):
        if filename.endswith('.json'):
            path = os.path.join(RESOURCES_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    repo_url = data.get('repo_url')
                    if repo_url:
                        download_and_purge_repo_files(repo_url)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

def main():
    for f in CDN_TARGETS:
        purge_jsdelivr(f)

    process_resources()

if __name__ == '__main__':
    main()