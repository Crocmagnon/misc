import base64, requests, sys, os


def main():
    s = requests.Session()
    token = os.getenv("GITEA_TOKEN")
    if not token:
        print("please specify a token")
        sys.exit(1)
    s.headers = {
        "Authorization": f"token {token}",
        "Accept": "application/json",
    }
    res = s.get("https://git.augendre.info/api/v1/repos/search?limit=100")
    res.raise_for_status()
    repos = res.json()
    with open("UNLICENSE", "rb") as f:
        unlicense = base64.b64encode(f.read()).decode("utf-8")
    for repo in repos["data"]:
        full_name = repo["full_name"]
        url = repo["html_url"]
        license_url = f"https://git.augendre.info/api/v1/repos/{full_name}/contents/LICENSE"
        res = s.get(license_url)
        if res.status_code != 200:
            print(f"No LICENSE -> Public domain : {url}")
            res = s.post(license_url, json={"content": unlicense})
            if res.status_code != 201:
                print("issue creating license")
            continue
        license_json = res.json()
        license = base64.b64decode(license_json["content"]).decode("utf-8")
        should_change = True
        if "GNU" in license:
            print(f"GPL -> Public domain : {url}")
        elif "MIT" in license:
            print(f"MIT -> Public domain : {url}")
        elif "DO WHAT THE FUCK YOU WANT TO" in license:
            print(f"WTFPL -> Public domain : {url}")
        elif "public domain" in license:
            print(f"Public domain : {url}")
            should_change = False
        else:
            print(f"UNKNOWN : {url}")
            should_change = False

        if should_change:
            current_sha = license_json["sha"]
            res = s.put(license_url, json={"content": unlicense, "sha": current_sha})
            if res.status_code != 200:
                print("issue updating license")


if __name__ == "__main__":
    main()
