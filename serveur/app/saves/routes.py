import os
import zipfile

from flask import Blueprint, jsonify, send_file

from ..utils import get_directory_size, get_creation_time, obtenir_arborescence

saves_bp = Blueprint('saves', __name__)


@saves_bp.route('/saves', methods=['GET'])
def get_saves():
    """
    Renvoie la liste des différentes sauvegardes contenues dans le serveur (leurs dates).
    :return: Un objet contenant la date et le poids de chaque sauvegarde.
    """
    stored_files_path = 'stored_files'
    directories = []

    if os.path.exists(stored_files_path) and os.path.isdir(stored_files_path):
        for entry in os.scandir(stored_files_path):
            if entry.is_dir():
                dir_info = {
                    'id': entry.name,
                    'size': get_directory_size(entry.path),
                    'creation_time': get_creation_time(entry.path)
                }
                directories.append(dir_info)

    return jsonify({'directories': directories})


@saves_bp.route('/save/<id>', methods=['GET'])
def get_save_by_id(id):
    save_path = 'stored_files/'
    save_folder_path = os.path.join(save_path, id)

    # Vérifier si le dossier spécifié par l'ID existe
    if os.path.exists(save_folder_path) and os.path.isdir(save_folder_path):
        # Créer un fichier ZIP temporaire pour le dossier spécifié
        temp_zip_path = f"{id}.zip"
        with zipfile.ZipFile(temp_zip_path, 'w') as zipf:
            for folder_name, _, filenames in os.walk(save_folder_path):
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, save_folder_path))

        # Envoyer le fichier ZIP en réponse à la requête GET
        print(f"/app/{temp_zip_path}")
        return send_file(f"/app/{temp_zip_path}", as_attachment=True)
    else:
        return 'Not Found', 404  # Le dossier n'existe pas, renvoie un code 404


@saves_bp.route('/save/<id>/tree', methods=['GET'])
def get_save_tree_by_id(id):
    save_path = 'stored_files/'
    save_folder_path = os.path.join(save_path, id)

    # Vérifier si le dossier spécifié par l'ID existe
    if os.path.exists(save_folder_path) and os.path.isdir(save_folder_path):
        return obtenir_arborescence(os.path.join(save_path, id)), 200  # Le dossier existe, renvoie un code 200
    else:
        return 'Not Found', 404  # Le dossier n'existe pas, renvoie un code 404
