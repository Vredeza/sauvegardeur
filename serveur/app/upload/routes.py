import os
import uuid
import zipfile
from datetime import datetime

from flask import Blueprint, request

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Sauvegarde le contenu du fichier zip passé dans le corps de la requête dans un dossier nommé par la date.
    :return: Un code HTTP, 200 ou 400.
    """
    if 'file' not in request.files:
        return 'Aucun fichier envoyé.', 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return 'Nom de fichier vide.', 400

    save_path = 'stored_files/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    now = datetime.now()
    folder_name = str(uuid.uuid4())  # Format de nom de dossier basé sur la date et l'heure actuelles
    folder_path = os.path.join(save_path, folder_name)

    # Création du dossier pour extraire le contenu du fichier ZIP
    os.makedirs(folder_path)

    # Sauvegarde du fichier ZIP dans le dossier avec le nom original
    zip_path = os.path.join(folder_path, uploaded_file.filename)
    uploaded_file.save(zip_path)

    # Vérifier si le fichier est un fichier .zip
    if uploaded_file.filename.endswith('.zip'):
        # Dézipper le fichier dans le dossier créé
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(folder_path)

        # Supprimer le fichier ZIP après extraction
        os.remove(zip_path)

        return 'Fichier .zip reçu et décompressé avec succès !', 200
    else:
        # Supprimer le fichier ZIP s'il n'est pas au format .zip
        os.remove(zip_path)
        return 'Le fichier n\'est pas un fichier .zip.', 400
