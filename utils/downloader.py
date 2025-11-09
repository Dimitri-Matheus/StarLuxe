"""Utils for all related to downloading presets, updates and files"""

import os, requests, logging, boto3, zipfile
from botocore.exceptions import ClientError, EndpointConnectionError
from pathlib import Path
from utils.path import resource_path
from utils import _env
# from config import load_config

logging.basicConfig(level=logging.INFO)

def download_file(url, output_path):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(response.content)
    logging.info(f"Downloaded {url} → {output_path}")


def download_from_github(repo_owner, repo_name, resource, selected_preset, download_dir, result_queue):
    try:
        presets = [p for p in selected_preset if p and p.strip()]
        if not presets:
            logging.error("You haven't selected a preset!")
            raise ValueError("Select a preset before downloading!")

        if not download_dir:
            download_dir = resource_path(Path(__file__).parent / resource / "Presets")
        
        download_dir = Path(resource_path(download_dir))
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
        response =  {
            "status": True,
            "message": "Download completed successfully!"
        }
    
    except Exception as e:
        logging.error(f"Error during download: {e}")
        response =  {
            "status": False,
            "message": str(e)
        }
    
    result_queue.put(response)


def download_r2_dependencies(directory, progress_callback=None):
    bucket_name = _env.PRIVATE_BUCKET_NAME
    key_name = _env.NAME_FILE
    
    progress_callback = progress_callback or (lambda x: None) # Use the given callback or an empty function

    validation_items = {
        ClientError: "Server Connection Failed!",
        EndpointConnectionError: "No Internet Connection Detected!",
        zipfile.BadZipFile: "Downloaded File Corrupted!",
    }

    try:
        download_dir = Path(directory).parent
        if not all([_env.KEY_ID_RO, _env.APPLICATION_KEY_PRIVATE_RO]):
            raise ValueError("R2 credentials not configured!")
        logging.info(f"Connecting to R2...")

        progress_callback(0.1)

        r2 = boto3.resource(
            service_name='s3',
            endpoint_url=_env.ENDPOINT,
            aws_access_key_id=_env.KEY_ID_RO,
            aws_secret_access_key=_env.APPLICATION_KEY_PRIVATE_RO
        )

        file_path = download_dir / key_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Downloading {key_name}...")
        progress_callback(0.3)

        r2.Bucket(bucket_name).download_file(key_name, str(file_path))
        progress_callback(0.7)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(download_dir)
        logging.info(f"Extracted files to the folder {download_dir}/")
        progress_callback(0.9)

        file_path.unlink()
        logging.info(f"Deleted {key_name}")
        progress_callback(1.0)

        logging.info("All dependencies have been downloaded successfully!")
        return {
            "status": True
        }

    except tuple(validation_items.keys()) as e:
        error_type = type(e)
        message = validation_items.get(error_type, str(e))
        logging.error(f"{error_type.__name__}: {message}")
        progress_callback(0.0)
        return {
            "status": False,
            "message": message
        }
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        progress_callback(0.0)
        return {
            "status": False,
            "message": "An unexpected error occurred",
        }


#! Test functions
# config = load_config()
"""
download_from_github(
    config['Account']['github_name'],
    config['Account']['repository_name'],
    config['Account']['preset_folder'],
    config['Packages']['selected'],
    config['Packages'].get('download_dir', '')
)
"""
# download_from_github("Dimitri-Matheus", "Snake", "assets/icon", os.getcwd())
# download_r2_dependencies(config["Packages"]["download_dir"])
