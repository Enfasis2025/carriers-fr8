#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza carriers y los mapea con 12 rutas específicas
"""

import csv
from collections import defaultdict

# Definición de las rutas con sus ubicaciones de origen y destino
RUTAS = {
    "RUTA 1": {
        "descripcion": "Cuautitlán, EM → San Antonio, TX",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Cuautitlán", "estado": "Estado de México", "pais": "Mexico"},
        "destino": {"ciudad": "San Antonio", "estado": "Texas", "pais": "United States"}
    },
    "RUTA 2": {
        "descripcion": "Laredo, TX → McAllen, TX",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Laredo", "estado": "Texas", "pais": "United States"},
        "destino": {"ciudad": "McAllen", "estado": "Texas", "pais": "United States"}
    },
    "RUTA 3": {
        "descripcion": "Pico Rivera, CA → Tlalnepantla, MX (cruce por McAllen y Laredo)",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Pico Rivera", "estado": "California", "pais": "United States"},
        "destino": {"ciudad": "Tlalnepantla", "estado": "Estado de México", "pais": "Mexico"}
    },
    "RUTA 4": {
        "descripcion": "San Nicolás de los Garza, NL → El Paso, TX (cruce por Laredo)",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "San Nicolás de los Garza", "estado": "Nuevo León", "pais": "Mexico"},
        "destino": {"ciudad": "El Paso", "estado": "Texas", "pais": "United States"}
    },
    "RUTA 5": {
        "descripcion": "Independence, MO → San Mateo Atenco, EDOMX",
        "tipo": "DV53 HZMT, semanal",
        "origen": {"ciudad": "Independence", "estado": "Missouri", "pais": "United States"},
        "destino": {"ciudad": "San Mateo Atenco", "estado": "Estado de México", "pais": "Mexico"}
    },
    "LANE 6": {
        "descripcion": "Morelia, MICH → Brantford, ON, CA",
        "tipo": "DV53/R53, semanal",
        "origen": {"ciudad": "Morelia", "estado": "Michoacán", "pais": "Mexico"},
        "destino": {"ciudad": "Brantford", "estado": "Ontario", "pais": "Canada"}
    },
    "RUTA 7": {
        "descripcion": "Ciudad López Mateos, EDOMX → Sweetwater, TX",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Ciudad López Mateos", "estado": "Estado de México", "pais": "Mexico"},
        "destino": {"ciudad": "Sweetwater", "estado": "Texas", "pais": "United States"}
    },
    "RUTA 8": {
        "descripcion": "Parque Industrial FINSA II, Querétaro → Saint Clair, MI",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Querétaro", "estado": "Querétaro", "pais": "Mexico"},
        "destino": {"ciudad": "Saint Clair", "estado": "Michigan", "pais": "United States"}
    },
    "LANE 9": {
        "descripcion": "El Pino, EDOMX → NY - ON - QC",
        "tipo": "R53 HZMT, semanal",
        "origen": {"ciudad": "El Pino", "estado": "Estado de México", "pais": "Mexico"},
        "destino": {"ciudad": "Multiple", "estado": "New York|Ontario|Quebec", "pais": "United States|Canada"}
    },
    "RUTA 10": {
        "descripcion": "Morelia, MICH → Laredo, TX / Ramos Arizpe, COAH → Laredo, TX / San Juan Del Río, QRO → Laredo, TX",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Morelia|Ramos Arizpe|San Juan Del Río", "estado": "Michoacán|Coahuila|Querétaro", "pais": "Mexico"},
        "destino": {"ciudad": "Laredo", "estado": "Texas", "pais": "United States"}
    },
    "RUTA 11": {
        "descripcion": "San Antonio, TX → Ramos Arizpe, COAH / Houston, TX → Ramos Arizpe, COAH / Carrolton, TX → Ramos Arizpe, COAH",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "San Antonio|Houston|Carrolton", "estado": "Texas", "pais": "United States"},
        "destino": {"ciudad": "Ramos Arizpe", "estado": "Coahuila", "pais": "Mexico"}
    },
    "RUTA 12": {
        "descripcion": "Hidalgo del Parral, CHIH → Houston, TX (cruce por El Paso)",
        "tipo": "DV53, semanal",
        "origen": {"ciudad": "Hidalgo del Parral", "estado": "Chihuahua", "pais": "Mexico"},
        "destino": {"ciudad": "Houston", "estado": "Texas", "pais": "United States"}
    }
}

# Mapeo de abreviaciones y variaciones de estados
ESTADO_MAPPING = {
    # México
    "EM": "Estado de México",
    "EDOMX": "Estado de México",
    "MX": "Estado de México",
    "Estado de México": "Estado de México",
    "NL": "Nuevo León",
    "Nuevo León": "Nuevo León",
    "Nuevo Leon": "Nuevo León",  # Sin acento
    "Newfoundland and Labrador": "Nuevo León",  # Parece ser un error en los datos
    "MICH": "Michoacán",
    "MC": "Michoacán",
    "Michoacán": "Michoacán",
    "Michoacan": "Michoacán",  # Sin acento
    "QRO": "Querétaro",
    "QE": "Querétaro",
    "Querétaro": "Querétaro",
    "Queretaro": "Querétaro",  # Sin acento
    "COAH": "Coahuila",
    "Coahuila": "Coahuila",
    "CHIH": "Chihuahua",
    "CH": "Chihuahua",
    "Chihuahua": "Chihuahua",
    "TL": "Tlaxcala",
    "Tlaxcala": "Tlaxcala",
    "PU": "Puebla",
    "Puebla": "Puebla",
    "TM": "Tamaulipas",
    "Tamaulipas": "Tamaulipas",
    "BN": "Baja California",
    "Baja California": "Baja California",
    "CL": "Colima",
    "Colima": "Colima",

    # Estados Unidos
    "TX": "Texas",
    "Texas": "Texas",
    "CA": "California",
    "California": "California",
    "MO": "Missouri",
    "Missouri": "Missouri",
    "MI": "Michigan",
    "Michigan": "Michigan",
    "NY": "New York",
    "New York": "New York",

    # Canadá
    "ON": "Ontario",
    "Ontario": "Ontario",
    "QC": "Quebec",
    "Quebec": "Quebec",
}

def normalize_state(state):
    """Normaliza el nombre del estado"""
    if state is None or state == "" or state == "None":
        return None
    state = str(state).strip()
    return ESTADO_MAPPING.get(state, state)

def normalize_city(city):
    """Normaliza el nombre de la ciudad"""
    if city is None or city == "" or city == "None":
        return None
    return str(city).strip().lower()

def normalize_country(country):
    """Normaliza el nombre del país"""
    if country is None or country == "" or country == "None":
        return None
    return str(country).strip()

def carrier_matches_location(carrier, location):
    """
    Verifica si un carrier tiene base en una ubicación específica
    location puede tener múltiples valores separados por |
    """
    carrier_state = normalize_state(carrier.get('STATE'))
    carrier_city = normalize_city(carrier.get('CITY'))
    carrier_country = normalize_country(carrier.get('COUNTRY'))

    # Manejar múltiples estados/ciudades en la ubicación
    estados = location['estado'].split('|')
    ciudades = location['ciudad'].split('|')
    paises = location['pais'].split('|')

    # Normalizar estados de la ubicación
    estados_normalizados = [normalize_state(e.strip()) for e in estados]
    ciudades_normalizadas = [normalize_city(c.strip()) for c in ciudades]
    paises_normalizados = [normalize_country(p.strip()) for p in paises]

    # Verificar si el país coincide
    if carrier_country not in paises_normalizados:
        return False

    # Verificar si el estado coincide
    if carrier_state and carrier_state in estados_normalizados:
        return True

    # Verificar si la ciudad coincide (aunque el estado no esté mapeado correctamente)
    if carrier_city and carrier_city in ciudades_normalizadas:
        return True

    return False

def main():
    print("Leyendo archivo carriers.csv...")

    # Leer el archivo CSV
    carriers = []
    with open('/home/user/carriers-fr8/carriers/Carriers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filtrar solo carriers
            if row['COMPANY TYPE'] == 'CARRIER':
                carriers.append(row)

    print(f"Total de registros de carriers encontrados: {len(carriers)}")

    # Analizar cada ruta
    resultados = defaultdict(list)

    for ruta_nombre, ruta_info in RUTAS.items():
        print(f"\nAnalizando {ruta_nombre}...")
        carriers_unicos = set()
        registros_agregados = 0

        origen = ruta_info['origen']
        destino = ruta_info['destino']

        for carrier in carriers:
            # Verificar si el carrier tiene base en origen o destino
            en_origen = carrier_matches_location(carrier, origen)
            en_destino = carrier_matches_location(carrier, destino)

            if en_origen or en_destino:
                # Contar carriers únicos para el resumen
                carrier_key = (
                    carrier['BAN'],
                    carrier['COMPANY NAME'],
                    carrier.get('CITY', ''),
                    normalize_state(carrier.get('STATE', '')),
                    carrier.get('COUNTRY', '')
                )
                carriers_unicos.add(carrier_key)

                # Agregar TODOS los registros del carrier (incluyendo diferentes emails)
                ubicacion = "ORIGEN" if en_origen else ""
                ubicacion += " y " if (en_origen and en_destino) else ""
                ubicacion += "DESTINO" if en_destino else ""

                resultados[ruta_nombre].append({
                    'RUTA': ruta_nombre,
                    'DESCRIPCION_RUTA': ruta_info['descripcion'],
                    'TIPO_RUTA': ruta_info['tipo'],
                    'BAN': carrier['BAN'],
                    'CARRIER': carrier['COMPANY NAME'],
                    'CITY': carrier.get('CITY', ''),
                    'STATE': carrier.get('STATE', ''),
                    'STATE_NORMALIZADO': normalize_state(carrier.get('STATE', '')),
                    'COUNTRY': carrier.get('COUNTRY', ''),
                    'UBICACION_EN_RUTA': ubicacion,
                    'EMAIL': carrier.get('EMAIL', ''),
                    'PHONE': carrier.get('PHONE #', ''),
                    'DATA_ORIGIN': carrier.get('DATA ORIGIN', '')
                })
                registros_agregados += 1

        print(f"  Carriers únicos: {len(carriers_unicos)}")
        print(f"  Registros totales (inc. múltiples contactos): {registros_agregados}")

    # Generar archivo de salida
    print("\nGenerando archivo carriers_12_rutas.csv...")

    output_rows = []
    for ruta in sorted(resultados.keys()):
        output_rows.extend(resultados[ruta])

    if output_rows:
        # Ordenar por RUTA y CARRIER
        output_rows.sort(key=lambda x: (x['RUTA'], x['CARRIER']))

        # Escribir CSV
        with open('/home/user/carriers-fr8/carriers_12_rutas.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['RUTA', 'DESCRIPCION_RUTA', 'TIPO_RUTA', 'BAN', 'CARRIER', 'CITY',
                         'STATE', 'STATE_NORMALIZADO', 'COUNTRY', 'UBICACION_EN_RUTA',
                         'EMAIL', 'PHONE', 'DATA_ORIGIN']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)

        print(f"✓ Archivo generado con {len(output_rows)} registros totales")

        # Resumen por ruta
        print("\n=== RESUMEN POR RUTA ===")
        print("(Incluye múltiples contactos por carrier cuando están disponibles)\n")
        for ruta in sorted(resultados.keys()):
            registros = len(resultados[ruta])
            # Contar carriers únicos
            carriers_unicos = set()
            for r in resultados[ruta]:
                key = (r['BAN'], r['CARRIER'], r['CITY'], r['STATE_NORMALIZADO'], r['COUNTRY'])
                carriers_unicos.add(key)
            print(f"{ruta}: {len(carriers_unicos)} carriers únicos, {registros} registros totales")
    else:
        print("No se encontraron coincidencias")

if __name__ == "__main__":
    main()
