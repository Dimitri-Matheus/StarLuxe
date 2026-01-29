"""Utils for all related to downloading presets, updates and files"""

import os, requests, logging, boto3, zipfile, sys, tempfile, subprocess, json
from botocore.exceptions import ClientError, EndpointConnectionError
from pathlib import Path
from utils.path import resource_path
from packaging import version
from win32api import GetFileVersionInfo, LOWORD, HIWORD
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


def get_version(size=4):
    if "__compiled__" in globals() or getattr(sys, "frozen", False):
        exe = Path(sys.argv[0]).resolve()
        logging.debug(f"Path: {exe}")
        try:
            info_parse = GetFileVersionInfo(str(exe), "\\")
            ms_file = info_parse["FileVersionMS"]
            ls_file = info_parse["FileVersionLS"]
            version = [str(HIWORD(ms_file)), str(LOWORD(ms_file)),
            str(HIWORD(ls_file)), str(LOWORD(ls_file))]
            return ".".join(version[:size])
        except Exception as e:
            logging.error(f"Failed to read version: {e}")
    else:
        return "0.0.0"


def sync_metadata(repo_owner, repo_name):
    remote_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/refs/heads/main/script/Presets/metadata.json"
    local_metadata = resource_path("script/Presets/metadata.json")

    try:
        local_data = {}
        if os.path.exists(local_metadata):
            try:
                with open(local_metadata, "r", encoding="utf-8") as file:
                    local_data = json.load(file)
            except Exception:
                local_data = {}

        response = requests.get(remote_url, timeout=3)
        response.raise_for_status()
        remote_data = response.json()

        if local_data == remote_data:
            logging.info("Metadata is already up to date!")
            return

        download_file(remote_url, local_metadata)
        logging.info(f"Metadata synchronized successfully!")
    
    except Exception as e:
        logging.warning(f"Sync failed: {e}")


def download_from_github(repo_owner, repo_name, resource, selected_preset, download_dir, result_queue, progress_callback=None):
    progress_callback = progress_callback or (lambda x: None)

    validation_items = {
        requests.ConnectionError: "Failed to connect to server!",
        requests.Timeout: "The server took too long to respond.",
        requests.HTTPError: "Connection error with the server."
    }

    try:
        presets = [p for p in selected_preset if p and p.strip()]
        if not download_dir:
            download_dir = resource_path(Path(__file__).parent / resource / "Presets")
        
        download_dir = Path(resource_path(download_dir))
        resource = resource.rstrip("/\\")
        total_presets = len(presets)
        progress_callback(0.0)
        logging.info("Progress: 0.0%")

        for preset_index, preset_name in enumerate(selected_preset):
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

                items = response.json()
                file_count = sum(1 for item in items if item["type"] == "file")
                for file_index, item in enumerate(items):
                    if item["type"] == "file":
                        relative_path = os.path.relpath(item["path"], remote)
                        output_file = local_path / relative_path
                        download_file(item["download_url"], str(output_file))
                        if progress_callback:
                            progress = ((preset_index + (file_index + 1) / file_count) / total_presets)
                            progress_callback(progress)
                            logging.info(f"Progress: {progress * 100:.1f}%")
                        
                    elif item["type"] == "dir":
                        local_remote.append((item["path"], local_path))
        
            logging.info(f"Preset '{preset_name}' completed at {local}")

        logging.info("All selected presets have been downloaded successfully!")
        response =  {
            "status": True,
            "message": "Download completed successfully!"
        }
    
    except tuple(validation_items.keys()) as e:
        error_type = type(e)
        message = validation_items.get(error_type, str(e))
        status_code = getattr(e.response, 'status_code', 'N/A') if hasattr(e, 'response') else 'N/A'
        reason = getattr(e.response, 'reason', 'N/A') if hasattr(e, 'response') else 'N/A'

        logging.error(f"{error_type.__name__}: {message}, code={status_code}, reason={reason}")
        progress_callback(0.0)
        response = {
            "status": False,
            "message": message
        }
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        progress_callback(0.0)
        response = {
            "status": False,
            "message": "An unexpected error occurred"
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


def check_for_updates(github_owner, enabled_auto_check_update):
    current_version = get_version(size=3)
    remote_url = f"https://api.github.com/repos/{github_owner}/StarLuxe/releases/latest"
    if not enabled_auto_check_update:
        logging.info(f"Check update inactive")
        return {
            "status": False
        }

    try:
        response = requests.get(remote_url)
        response.raise_for_status()
        body = response.json()
        latest_version = None

        version_str = body["tag_name"].strip()
        if version_str.lower().startswith("v"):
            latest_version = version_str.lstrip("v").rstrip("-beta")

        if version.parse(latest_version) > version.parse(current_version):
            for c in range(0, 2):
                if body["assets"][c]["content_type"] == "application/x-msdownload":
                    update_url = body["assets"][c]["browser_download_url"]
                    break
            logging.info(f"Download URL: {update_url}")

            logging.info("Update version checked!")
            return {
                "status": True,
                "url": update_url,
                "version": latest_version,
                "size": body["assets"][c]["size"]
            }

        else:
            logging.info("StarLuxe is already up to date!")
            return {
                "status": False
            }

    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return {
            "status": False,
            "message": "Error checking for updates",
        }


def download_update(url):
    logging.info("Downloading update...")

    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "StarLuxe_Update.exe")

    try:
        r = requests.get(url, stream=True)
        with open(installer_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info("Update downloaded successfully!")
        subprocess.Popen([installer_path, "/SILENT", "/SP-", "/SUPPRESSMSGBOXES", "/NORESTART"])
        sys.exit(0)

    except Exception as e:
        logging.error(f"Error applying update: {e}")


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
# download_r2_dependencies(config["Packages"]["download_dir"])
# check_for_updates("Dimitri-Matheus", "1.0.3")
# sync_metadata(config["Account"]["github_name"], config["Account"]["repository_name"])
