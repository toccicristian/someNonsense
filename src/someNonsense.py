#!/usr/bin/env python3

"""
someNonesense.py

Convierte notas de MyBrain al formato de tareas de NoNonsense.
Porque, al combinar ambos backups, necesariamente aparece
some nonsense.
"""

import argparse
import copy
import json
import sys

def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Error: no existe el archivo: {ruta}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"Error de JSON en {ruta}: {error}", file=sys.stderr)
        sys.exit(1)


def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")


def obtener_ids_existentes(backup_nononsense):
    ids_listas = []
    ids_tareas = []

    for lista in backup_nononsense.get("lists", []):
        if isinstance(lista.get("_id"), int):
            ids_listas.append(lista["_id"])

        for tarea in lista.get("tasks", []):
            if isinstance(tarea.get("_id"), int):
                ids_tareas.append(tarea["_id"])

    return ids_listas, ids_tareas


def convertir_notas(notas, nuevo_id_tarea):
    tareas = []

    for posicion, nota in enumerate(notas):
        titulo = nota.get("title", "")
        contenido = nota.get("content", "")

        # NoNonsense utiliza lft/rgt para ordenar las tareas.
        # Se asignan en orden ascendente.
        lft = posicion * 2 + 1
        rgt = posicion * 2 + 2

        tarea = {
            "_id": nuevo_id_tarea + posicion,
            "dblist": None,  # Se completa después de crear la lista.
            "locked": 0,
            "updated": nota.get("updatedDate", nota.get("createdDate", 0)),
            "note": contenido,
            "title": titulo,
            "lft": lft,
            "rgt": rgt,
            "remotes": [],
            "reminders": []
        }

        tareas.append(tarea)

    return tareas


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convierte las notas de MyBrain al formato de tareas "
            "de NoNonsense."
        )
    )

    parser.add_argument(
        "mybrain",
        help="Archivo JSON exportado desde MyBrain"
    )

    parser.add_argument(
        "nononsense",
        help="Archivo JSON exportado desde NoNonsense"
    )

    parser.add_argument(
        "salida",
        help="Archivo JSON que se generará"
    )

    parser.add_argument(
        "--lista",
        default="mybrain",
        help="Nombre de la nueva lista. Por defecto: mybrain"
    )

    args = parser.parse_args()

    backup_mybrain = cargar_json(args.mybrain)
    backup_nononsense = cargar_json(args.nononsense)

    if not isinstance(backup_mybrain.get("notes"), list):
        print(
            "Error: el backup de MyBrain no contiene un array 'notes'.",
            file=sys.stderr
        )
        sys.exit(1)

    if not isinstance(backup_nononsense.get("lists"), list):
        print(
            "Error: el backup de NoNonsense no contiene un array 'lists'.",
            file=sys.stderr
        )
        sys.exit(1)

    # Copia para no modificar accidentalmente el objeto original en memoria.
    resultado = copy.deepcopy(backup_nononsense)

    ids_listas, ids_tareas = obtener_ids_existentes(resultado)

    nuevo_id_lista = max(ids_listas, default=0) + 1
    nuevo_id_tarea = max(ids_tareas, default=0) + 1

    tareas = convertir_notas(
        backup_mybrain["notes"],
        nuevo_id_tarea
    )

    # Todas las tareas deben apuntar al _id de la nueva lista.
    for tarea in tareas:
        tarea["dblist"] = nuevo_id_lista

    # La fecha de actualización de la lista será la mayor fecha disponible.
    fechas = [
        nota.get("updatedDate", nota.get("createdDate", 0))
        for nota in backup_mybrain["notes"]
        if isinstance(nota.get("updatedDate", nota.get("createdDate", 0)), int)
    ]

    fecha_actualizacion = max(fechas, default=0)

    nueva_lista = {
        "_id": nuevo_id_lista,
        "updated": fecha_actualizacion,
        "title": args.lista,
        "remotes": [],
        "tasks": tareas
    }

    resultado["lists"].append(nueva_lista)

    guardar_json(args.salida, resultado)

    print(f"Conversión terminada.")
    print(f"Notas convertidas: {len(tareas)}")
    print(f"Nueva lista: {args.lista}")
    print(f"_id de la nueva lista: {nuevo_id_lista}")
    print(f"Archivo generado: {args.salida}")


if __name__ == "__main__":
    main()

