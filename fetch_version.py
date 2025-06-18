import httpx
import semver


async def fetch_latest_tag(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        tags = response.json()

    valid_tags = []

    for tag in tags:
        tag_name = tag["name"]
        try:
            # Check if the tag name follows semver and is not a pre-release
            version = semver.VersionInfo.parse(tag_name)
            if not version.prerelease:
                valid_tags.append(tag_name)
        except ValueError:
            # Ignore tags that are not valid semver
            pass

    if not valid_tags:
        return "Unknown"

    # Sort the valid tags based on semantic versioning
    valid_tags.sort(key=lambda v: semver.VersionInfo.parse(v), reverse=True)

    return valid_tags[0]
