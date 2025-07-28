"""Utils for all related to downloading presets, updates and files"""

import os, requests, logging
from pathlib import Path
#from config import load_config

logging.basicConfig(level=logging.INFO)

def download_file(url, output_path):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(response.content)
    logging.info(f"Downloaded {url} → {output_path}")

# TODO: Realizar uma verifição se o arquivo existe ou não
def download_from_github(repo_owner, repo_name, resource, selected_preset, download_dir):
    try:
        presets = [p for p in selected_preset if p and p.strip()]
        if not presets:
            logging.error("Nenhum preset selecionado!")
            raise ValueError("Please select at least one preset before downloading!")

        if not download_dir:
            download_dir = Path(__file__).parent / resource / "Presets"
        download_dir = Path(download_dir)

        resource = resource.rstrip("/\\")

        for preset_name in selected_preset:
            remote = f"{resource}/Presets/{preset_name}"
            local = download_dir / preset_name
            local_remote = [(remote, local)]

            while local_remote:
                remote_path, local_path = local_remote.pop()
                api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{remote_path}"
                headers = {'Accept': 'application/vnd.github.v3+json'}
                logging.info(f"Acessing: {api_url}")
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()

                for item in response.json():
                    if item["type"] == "file":
                        relative_path = os.path.relpath(item["path"], remote)
                        output_file = local_path / relative_path
                        download_file(item["download_url"], str(output_file))
                    elif item["type"] == "dir":
                        local_remote.append((item["path"], local_path))
        
            logging.info(f"Preset '{preset_name}' completed at {local}")

        logging.info("All selected presets have been downloaded successfully!")
        return {
            "status": True,
            "message": "All selected presets have been downloaded successfully!"
        }
    
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return {
            "status": False,
            "message": str(e)
        }


# Test
"""config = load_config()
download_from_github(
    config['Account']['github_name'],
    config['Account']['repository_name'],
    config['Account']['preset_resource'],
    config['Packages']['selected'],
    config['Packages'].get('download_dir', '')
)
"""
#download_from_github("Dimitri-Matheus", "Snake", "assets/icon", os.getcwd())
