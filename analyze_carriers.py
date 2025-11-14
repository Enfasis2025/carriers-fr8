#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from collections import defaultdict

# Definición de las rutas con sus estados de origen y destino
rutas = {
    "RUTA 1": {
        "descripcion": "Cuautitlán, EM → San Antonio, TX",
        "origen": ["Estado de México", "Mexico State", "EM", "EDOMX", "MX"],
        "origen_ciudades": ["cuautitlan"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["san antonio"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    },
    "RUTA 2": {
        "descripcion": "Laredo, TX → McAllen, TX",
        "origen": ["Texas", "TX"],
        "origen_ciudades": ["laredo"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["mcallen"],
        "pais_origen": "United States",
        "pais_destino": "United States"
    },
    "RUTA 3": {
        "descripcion": "Pico Rivera, CA → Tlalnepantla, MX (cruce por McAllen y Laredo)",
        "origen": ["California", "CA"],
        "origen_ciudades": ["pico rivera"],
        "destino": ["Estado de México", "Mexico State", "EM", "EDOMX", "MX"],
        "destino_ciudades": ["tlalnepantla"],
        "cruce": ["Texas", "TX"],
        "cruce_ciudades": ["mcallen", "laredo"],
        "pais_origen": "United States",
        "pais_destino": "Mexico"
    },
    "RUTA 4": {
        "descripcion": "San Nicolás de los Garza, NL → El Paso, TX (cruce por Laredo)",
        "origen": ["Nuevo León", "Nuevo Leon", "NL", "Newfoundland and Labrador"],
        "origen_ciudades": ["san nicolas de los garza", "general escobedo"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["el paso"],
        "cruce": ["Texas", "TX"],
        "cruce_ciudades": ["laredo"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    },
    "RUTA 5": {
        "descripcion": "Independence, MO → San Mateo Atenco, EDOMX",
        "origen": ["Missouri", "MO"],
        "origen_ciudades": ["independence"],
        "destino": ["Estado de México", "Mexico State", "EM", "EDOMX", "MX"],
        "destino_ciudades": ["san mateo atenco"],
        "pais_origen": "United States",
        "pais_destino": "Mexico"
    },
    "LANE 6": {
        "descripcion": "Morelia, MICH → Brantford, ON, CA",
        "origen": ["Michoacán", "Michoacan", "MICH", "MI"],
        "origen_ciudades": ["morelia"],
        "destino": ["Ontario", "ON"],
        "destino_ciudades": ["brantford"],
        "pais_origen": "Mexico",
        "pais_destino": "Canada"
    },
    "RUTA 7": {
        "descripcion": "Ciudad López Mateos, EDOMX → Sweetwater, TX",
        "origen": ["Estado de México", "Mexico State", "EM", "EDOMX", "MX"],
        "origen_ciudades": ["ciudad lopez mateos", "lopez mateos"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["sweetwater"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    },
    "RUTA 8": {
        "descripcion": "Parque Industrial FINSA II, Querétaro → Saint Clair, MI",
        "origen": ["Querétaro", "Queretaro", "QRO", "QE"],
        "origen_ciudades": ["queretaro", "san juan del rio"],
        "destino": ["Michigan", "MI"],
        "destino_ciudades": ["saint clair"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    },
    "LANE 9": {
        "descripcion": "El Pino, EDOMX → NY - ON - QC",
        "origen": ["Estado de México", "Mexico State", "EM", "EDOMX", "MX"],
        "origen_ciudades": ["el pino"],
        "destino": ["New York", "NY", "Ontario", "ON", "Quebec", "QC"],
        "destino_ciudades": [],
        "pais_origen": "Mexico",
        "pais_destino": ["United States", "Canada"]
    },
    "RUTA 10": {
        "descripcion": "Morelia, MICH → Laredo, TX + Ramos Arizpe, COAH → Laredo, TX + San Juan Del Río, QRO → Laredo, TX",
        "origen": ["Michoacán", "Michoacan", "MICH", "MI", "Coahuila", "COAH", "Querétaro", "Queretaro", "QRO", "QE"],
        "origen_ciudades": ["morelia", "ramos arizpe", "san juan del rio"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["laredo"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    },
    "RUTA 11": {
        "descripcion": "San Antonio, TX → Ramos Arizpe, COAH + Houston, TX → Ramos Arizpe, COAH + Carrolton, TX → Ramos Arizpe, COAH",
        "origen": ["Texas", "TX"],
        "origen_ciudades": ["san antonio", "houston", "carrolton"],
        "destino": ["Coahuila", "COAH"],
        "destino_ciudades": ["ramos arizpe"],
        "pais_origen": "United States",
        "pais_destino": "Mexico"
    },
    "RUTA 12": {
        "descripcion": "Hidalgo del Parral, CHIH → Houston, TX (cruce por El Paso)",
        "origen": ["Chihuahua", "CHIH", "CH"],
        "origen_ciudades": ["hidalgo del parral", "parral"],
        "destino": ["Texas", "TX"],
        "destino_ciudades": ["houston"],
        "cruce": ["Texas", "TX"],
        "cruce_ciudades": ["el paso"],
        "pais_origen": "Mexico",
        "pais_destino": "United States"
    }
}

def normalizar_texto(texto):
    """Normaliza texto para comparación: lowercase, sin acentos, sin espacios extra"""
    if not texto or texto == '':
        return ''
    # Convertir a minúsculas
    texto = str(texto).lower().strip()
    # Remover caracteres especiales pero mantener letras y espacios
    texto = re.sub(r'[^\w\s]', ' ', texto)
    # Remover espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def estado_coincide(estado_carrier, estados_ruta):
    """Verifica si el estado del carrier coincide con alguno de los estados de la ruta"""
    if not estado_carrier:
        return False

    estado_norm = normalizar_texto(estado_carrier)

    for estado_ruta in estados_ruta:
        estado_ruta_norm = normalizar_texto(estado_ruta)
        if estado_norm == estado_ruta_norm or estado_norm in estado_ruta_norm or estado_ruta_norm in estado_norm:
            return True
    return False

def ciudad_coincide(ciudad_carrier, ciudades_ruta):
    """Verifica si la ciudad del carrier coincide con alguna de las ciudades de la ruta"""
    if not ciudad_carrier or not ciudades_ruta:
        return False

    ciudad_norm = normalizar_texto(ciudad_carrier)
    if ciudad_norm == '':
        return False

    for ciudad_ruta in ciudades_ruta:
        ciudad_ruta_norm = normalizar_texto(ciudad_ruta)
        if ciudad_norm in ciudad_ruta_norm or ciudad_ruta_norm in ciudad_norm:
            return True
    return False

def analizar_carrier(carrier_data, ruta_info):
    """Analiza si un carrier coincide con una ruta"""
    estado = carrier_data.get('estado', '')
    ciudad = carrier_data.get('ciudad', '')
    pais = carrier_data.get('pais', '')

    coincidencias = []

    # Verificar origen
    if estado_coincide(estado, ruta_info.get('origen', [])):
        coincidencias.append('ORIGEN')
        if ciudad_coincide(ciudad, ruta_info.get('origen_ciudades', [])):
            coincidencias.append('ORIGEN_CIUDAD')

    # Verificar destino
    destinos = ruta_info.get('destino', [])
    if isinstance(destinos, list):
        if estado_coincide(estado, destinos):
            coincidencias.append('DESTINO')
            if ciudad_coincide(ciudad, ruta_info.get('destino_ciudades', [])):
                coincidencias.append('DESTINO_CIUDAD')

    # Verificar cruce (si existe)
    if 'cruce' in ruta_info:
        if estado_coincide(estado, ruta_info.get('cruce', [])):
            coincidencias.append('CRUCE')
            if ciudad_coincide(ciudad, ruta_info.get('cruce_ciudades', [])):
                coincidencias.append('CRUCE_CIUDAD')

    return coincidencias

# Leer el archivo CSV de carriers
carriers_por_ruta = defaultdict(list)
todos_carriers = []

print("Leyendo archivo de carriers...")

with open('/home/user/carriers-fr8/carriers/Carrires.csv', 'r', encoding='utf-8') as f:
    # Probar si la primera línea es un header
    primera_linea = f.readline()
    f.seek(0)

    # Si no tiene header claro, no saltamos línea
    reader = csv.reader(f)

    for row_num, row in enumerate(reader, 1):
        if len(row) < 10:
            continue

        carrier_data = {
            'id': row[0] if len(row) > 0 else '',
            'tipo': row[1] if len(row) > 1 else '',
            'nombre': row[2] if len(row) > 2 else '',
            'email': row[4] if len(row) > 4 else '',
            'telefono': row[5] if len(row) > 5 else '',
            'ciudad': row[7] if len(row) > 7 else '',
            'estado': row[8] if len(row) > 8 else '',
            'pais': row[9] if len(row) > 9 else '',
            'origen_data': row[10] if len(row) > 10 else ''
        }

        todos_carriers.append(carrier_data)

        # Analizar contra cada ruta
        for ruta_nombre, ruta_info in rutas.items():
            coincidencias = analizar_carrier(carrier_data, ruta_info)

            if coincidencias:
                carriers_por_ruta[ruta_nombre].append({
                    'carrier': carrier_data,
                    'tipo_coincidencia': ', '.join(coincidencias),
                    'descripcion_ruta': ruta_info['descripcion']
                })

print(f"Total de carriers leídos: {len(todos_carriers)}")
print("\nGenerando archivo de resultados...")

# Generar archivo CSV con resultados
with open('/home/user/carriers-fr8/carriers_12_rutas.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)

    # Header
    writer.writerow([
        'RUTA',
        'DESCRIPCION_RUTA',
        'CARRIER_ID',
        'CARRIER_NOMBRE',
        'CIUDAD',
        'ESTADO',
        'PAIS',
        'EMAIL',
        'TELEFONO',
        'TIPO_COINCIDENCIA',
        'ORIGEN_DATA'
    ])

    # Escribir resultados por ruta
    for ruta_nombre in sorted(rutas.keys()):
        coincidencias = carriers_por_ruta.get(ruta_nombre, [])

        print(f"\n{ruta_nombre}: {len(coincidencias)} carriers encontrados")

        for match in coincidencias:
            carrier = match['carrier']
            writer.writerow([
                ruta_nombre,
                match['descripcion_ruta'],
                carrier['id'],
                carrier['nombre'],
                carrier['ciudad'],
                carrier['estado'],
                carrier['pais'],
                carrier['email'],
                carrier['telefono'],
                match['tipo_coincidencia'],
                carrier['origen_data']
            ])

print("\n✓ Archivo 'carriers_12_rutas.csv' generado exitosamente!")
print("\nResumen por ruta:")
for ruta_nombre in sorted(rutas.keys()):
    count = len(carriers_por_ruta.get(ruta_nombre, []))
    print(f"  {ruta_nombre}: {count} carriers")
