import os
from datetime import datetime


def get_creation_time(path):
    creation_time = os.path.getctime(path)
    return datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")


def obtenir_arborescence(dossier, indentation=0):
    arborescence = ""
    if not os.path.exists(dossier):
        return "Le dossier spécifié n'existe pas."

    for element in os.listdir(dossier):
        chemin_element = os.path.join(dossier, element)
        arborescence += " " * indentation + "|___ " + element + "\n"
        if os.path.isdir(chemin_element):
            arborescence += obtenir_arborescence(chemin_element, indentation + 4)

    return arborescence


def get_directory_size(path):
    """
    Parcours un dossier et renvoie son poids.
    :param path: Le chemin du dossier à analyser.
    :return: Le poids du dossier.
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size
