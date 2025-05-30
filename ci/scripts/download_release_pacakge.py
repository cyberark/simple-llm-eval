import requests
import os

def download_latest_release_assets(owner, repo, download_dir='release_package'):
    api_url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'

    # Get latest release data
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f'Failed to fetch release info: {response.status_code}')

    release_data = response.json()
    assets = release_data.get('assets', [])

    # Filter for .whl files only
    whl_assets = [asset for asset in assets if asset['name'].endswith('.whl')]

    if not whl_assets:
        raise Exception('No .whl assets found in the latest release.')
    if len(whl_assets) > 1:
        raise Exception(f'Expected exactly one .whl asset, found {len(whl_assets)}.')

    os.makedirs(download_dir, exist_ok=True)

    asset = whl_assets[0]
    asset_url = asset['browser_download_url']
    asset_name = asset['name']
    asset_path = os.path.join(download_dir, asset_name)

    print(f'Downloading {asset_name}...')
    asset_response = requests.get(asset_url, stream=True)
    if asset_response.status_code == 200:
        with open(asset_path, 'wb', encoding='utf-8') as f:
            for chunk in asset_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Downloaded: {asset_path}')
    else:
        raise Exception(f'Failed to download {asset_name}: {asset_response.status_code}')

if __name__ == '__main__':
    download_latest_release_assets('cyberark', 'simple-llm-eval')
    print('Download completed successfully.')
