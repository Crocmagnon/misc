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
        print()
        full_name = repo["full_name"]
        url = repo["html_url"]
        base_url = f"https://git.augendre.info/api/v1/repos/{full_name}/contents"
        license_url = f"{base_url}/LICENSE"
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
        should_add_readme_mention = True
        if "GNU" in license:
            print(f"GPL -> Public domain : {url}")
        elif "public domain" in license or "Unlicense" in license:
            print(f"Public domain : {url}")
            should_change = False
        elif "MIT" in license:
            print(f"MIT -> Public domain : {url}")
        elif "DO WHAT THE FUCK YOU WANT TO" in license:
            print(f"WTFPL -> Public domain : {url}")
        else:
            print(f"UNKNOWN : {url}")
            should_change = False
            should_add_readme_mention = False

        if should_change:
            current_sha = license_json["sha"]
            res = s.put(license_url, json={"content": unlicense, "sha": current_sha})
            if res.status_code != 200:
                print("issue updating license")
        if should_add_readme_mention:
            readme_url = f"{base_url}/README.md"
            res = s.get(readme_url)
            if res.status_code != 200:
                print("No readme")
                continue
            readme_json = res.json()
            readme = base64.b64decode(readme_json["content"].encode("utf-8")).decode("utf-8")
            readme += "\n# Reuse\nIf you do reuse my work, please consider linking back to this repository 🙂"
            readme = base64.b64encode(readme.encode("utf-8")).decode("utf-8")
            current_sha = readme_json["sha"]
            res = s.put(readme_url, json={"content": readme, "sha": current_sha})
            if res.status_code != 200:
                print("issue updating readme")


if __name__ == "__main__":
    main()
