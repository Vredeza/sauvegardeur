import requests
import argparse
import os
import zipfile


def get_file_extensions(file_path):
    """

    :param file_path: Le chemin vers le fichier contenant les extensions de fichier à envoyer au serveur.
    :return: Une liste contenant les extensions de fichier à envoyer au serveur.
    """
    extensions = []

    with open(file_path, 'r') as file:
        for line in file:
            extension = line.strip()  # J'enlève les espaces au cas où
            if extension and not extension.startswith('#'):
                extensions.append(extension)

    return extensions


def zip_folder_with_extensions(folder_path, extensions=None):
    """
    Créer un fichier zip contenant les fichiers à envoyer au serveur. Selon les extensions spécifiées.
    :param folder_path: Chemin vers le dossier à compresser.
    :param extensions: Liste d'extensions de fichiers. Si vide, envoie tous les fichiers contenu dans le dossier.
    :return: Le chemin vers le fichier zip créé.
    """
    # Création d'un fichier .zip temporaire
    if extensions is None:
        extensions = []
    temp_zip_path = 'temp.zip'
    with zipfile.ZipFile(temp_zip_path, 'w') as zipf:
        for folder_name, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                # Vérification de l'extension du fichier
                if not extensions or any(file_path.endswith(ext) for ext in extensions):
                    # Ajout des fichiers avec les extensions spécifiées au fichier .zip
                    zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))

    return temp_zip_path


def send_zip_to_server(zip_file_path, server_name, server_port):
    """
    Envoie un fichier au serveur.
    :param zip_file_path: Le chemin vers le fichier zip à envoyer.
    :param server_name: L'addresse du serveur.
    :param server_port: Le port sur lequel envoyer fichier.
    """
    server_url = f'http://{server_name}:{server_port}/upload'

    with open(zip_file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(server_url, files=files)

        if response.status_code == 200:
            print("Fichier envoyé avec succès au serveur !")
        else:
            print("Échec de l'envoi du fichier au serveur.")


def save_action(args):
    # Vérification du dossier racine
    if not os.path.isdir(os.path.abspath(args.dossier)):
        print(f"Erreur : Le chemin spécifié pour le dossier '{args.dossier}' n'existe pas ou n'est pas un dossier "
              f"valide.")
        exit(1)

    # Vérification du fichier extensions
    if args.fichier and not os.path.isfile(os.path.abspath(args.fichier)):
        print(
            f"Erreur : Le chemin spécifié pour le fichier '{args.fichier}' n'existe pas ou n'est pas un fichier valide.")
        exit(1)

    if args.fichier:
        zip_path = zip_folder_with_extensions(args.dossier, get_file_extensions(args.fichier))
    else:
        zip_path = zip_folder_with_extensions(args.dossier)

    send_zip_to_server(zip_path, args.adresse, args.port)
    os.remove(zip_path)


def ls_action(args):
    url = f'http://{args.adresse}:{args.port}/saves'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        directories = data.get('directories', [])

        # Affichage sous forme de tableau
        print("ID\t\t\t\t\tDate\t\t\tSize")
        print("----------------------------------------------------------------------")
        for directory in directories:
            name = directory.get('name', '')
            size = directory.get('size', 0)
            date = directory.get('creation_time', '')
            print(f"{name}\t{date}\t{size}")
    else:
        print("Erreur lors de la récupération des informations de sauvegarde.")


def restore_action(args):
    full_id = get_full_id(args.sauvegarde, args.adresse, args.port)
    if full_id == '':
        print("Impossible de faire correspondre l'identifiant de la sauvegarde.")
        exit(1)

    url = f'http://{args.adresse}:{args.port}/save/{full_id}'

    # Effectuer la requête GET pour obtenir le fichier ZIP
    response = requests.get(url)

    if response.status_code == 200:
        # Chemin où sauvegarder le fichier ZIP téléchargé
        zip_file_path = 'temp_restore.zip'

        # Écriture du contenu du fichier ZIP
        with open(zip_file_path, 'wb') as file:
            file.write(response.content)

        # Décompresser le fichier ZIP dans le dossier spécifié
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(args.destination)

        # Supprimer le fichier ZIP temporaire après extraction
        os.remove(zip_file_path)

        print("Restauration terminée.")
    else:
        print("Erreur lors de la restauration.")


def get_full_id(incomplete_id, server, port):
    url = f'http://{server}:{port}/saves'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        directories = data.get('directories', [])

        # Stocker les correspondances potentielles trouvées
        matches = [directory['name'] for directory in directories if incomplete_id in directory['name']]

        # Filtrer les correspondances pour obtenir l'ID complet
        full_ids = [match for match in matches if match.startswith(incomplete_id)]

        if len(full_ids) == 1:
            return full_ids[0]  # Retourne l'ID complet unique correspondant à l'ID partiel donné
        else:
            return ''  # Plusieurs correspondances ou aucune
    else:
        print("Erreur lors de la récupération des informations de sauvegarde.")
        return ''


def tree_action(args):
    url = f'http://{args.adresse}:{args.port}/save/{get_full_id(args.id, args.adresse, args.port)}/tree'
    response = requests.get(url)

    if response.status_code == 200:
        print(response.content.decode('utf-8'))
    elif response.status_code == 404:
        print("Erreur : sauvegarde n'existe pas.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Client pour sauvegarder une arborescence. Réalisé dans le cadre du projet de fin de ressource "
                    "'Continuité de services'.")

    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Commande 'save'
    save_parser = subparsers.add_parser('save', help='Sauvegarde une arborescence')
    save_parser.add_argument('dossier', help="Chemin du dossier à sauvegarder")
    save_parser.add_argument('-e', '--fichier',
                             help="Chemin du fichier contenant, si nécessaire, les extensions à envoyer.")
    save_parser.add_argument('-s', '--adresse', default='localhost', help="Adresse IP du serveur (défaut : localhost)")
    save_parser.add_argument('-p', '--port', type=int, default=80, help="Numéro de port du serveur (défaut : 80)")

    # Commande 'ls'
    ls_parser = subparsers.add_parser('ls', help='Liste les sauvegardes disponibles')
    ls_parser.add_argument('-s', '--adresse', default='localhost', help="Adresse IP du serveur (défaut : localhost)")
    ls_parser.add_argument('-p', '--port', type=int, default=80, help="Numéro de port du serveur (défaut : 80)")

    # Commande 'restore'
    restore_parser = subparsers.add_parser('restore', help='Restaure une sauvegarde')
    restore_parser.add_argument('sauvegarde', help="L'id de la sauvegarde à restaurer.")
    restore_parser.add_argument('-d', '--destination', help="Chemin de destination pour la restauration", required=True)
    restore_parser.add_argument('-s', '--adresse', default='localhost',
                                help="Adresse IP du serveur (défaut : localhost)")
    restore_parser.add_argument('-p', '--port', type=int, default=80, help="Numéro de port du serveur (défaut : 80)")

    tree_parser = subparsers.add_parser('tree', help="Affiche l'arborescence d'une sauvegarde.")
    tree_parser.add_argument('id', help="L'id de la sauvegarde à visualiser.")
    tree_parser.add_argument('-s', '--adresse', default='localhost', help="Adresse IP du serveur (défaut : localhost)")
    tree_parser.add_argument('-p', '--port', type=int, default=80, help="Numéro de port du serveur (défaut : 80)")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.command == 'save':
        save_action(args)
    elif args.command == 'ls':
        ls_action(args)
    elif args.command == 'restore':
        restore_action(args)
    elif args.command == 'tree':
        tree_action(args)
    else:
        print("Commande non reconnue")


if __name__ == "__main__":
    main()


