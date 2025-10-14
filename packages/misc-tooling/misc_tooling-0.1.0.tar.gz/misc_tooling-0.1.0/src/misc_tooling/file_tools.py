from pathlib import Path
import os


def file_exists(file_path) -> bool:
    """Returns whether or not the file exists"""
    return Path(file_path).exists()

def get_full_path(file_path: str) -> str:
    """returns the full path"""
    return str(Path(file_path).resolve())

def read_file(file_path: str) -> str:
    """Reads a file to a string"""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print("File not found.")
    except PermissionError:
        print("Invalid Permissions")
    except IsADirectoryError:
        print("The path given is a directory.")
    except UnicodeDecodeError:
        print("Invalid data.")
    return ""


def write_file(file_path, file_data):
    """Writes to a file"""
    try:
        with open(file_path, "w") as file:
            file.write(file_data)
            return True
    except NotADirectoryError as e:
        print(e)
        return False

    except PermissionError as e:
        print(f"Exception: {e}")
        return False
    
def write_file_all(file_path, file_data):
    """Creates a files path and writes a file to it"""
    try:
        path = Path(file_path)
        folder = path.parent
        folder.mkdir(parents=True, exist_ok=True)
        path.touch()
        with open(str(path), "w") as file:
            file.write(file_data)
            file.close()
    except Exception as e:
        print(e)


def delete_file(file_path) -> bool:
    """Deletes a file and returns if it was successful"""
    try:
        path = Path(file_path)
        os.remove(file_path)
        return not path.exists()
    except Exception as e:
        print(e)
        return False


def delete_folder(folder_path) -> bool:
    """Deletes a folder"""
    try:
        os.removedirs(folder_path)
        return not Path(folder_path).exists()
    except Exception as e:
        print(e)
        return False


def make_folder(folder_path) -> bool:
    """Makes folder and returns success"""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        print(e)
        return False


def make_file(file_path: str) -> bool:
    """Makes a file and returns success"""
    try:
        open(file_path, "a").close()
        return file_exists(file_path)
    except Exception as e:
        print(e)
        return False
