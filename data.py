import os
import requests

def download_file(url, output_path):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download the file: {url}")

def download_from_github(repo_owner, repo_name, folder_path, output_dir):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item['type'] == 'file':
                file_url = item['download_url']
                relative_path = os.path.relpath(item['path'], folder_path)
                output_path = os.path.join(output_dir, folder_path.split('/')[-1], relative_path)
                download_file(file_url, output_path)
            elif item['type'] == 'dir':
                subfolder_path = item['path']
                download_from_github(repo_owner, repo_name, subfolder_path, output_dir)
        print(f"All contents of the {folder_path} have been downloaded!")

    else:
        print(f"Error accessing the folder: {response.status_code}, {response.json()}")

# Test
#download_from_github("Dimitri-Matheus", "Snake", "assets/icon", os.getcwd())
