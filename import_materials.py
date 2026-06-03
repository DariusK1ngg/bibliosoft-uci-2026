import os
import django
import re
import sys
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from biblioteca.models import (
    Autor, Editorial, Categoria, Genero, TipoDocumento,
    Facultad, Carrera, Material, MaterialCarrera, MaterialGenero
)

def fix_double_utf8(val):
    if not isinstance(val, str):
        return val
    current = val
    for _ in range(3):
        try:
            if any(c in current for c in ('Ã', 'Â', '\x83', '\x91', '\xc3', '\xc2')):
                next_val = current.encode('latin1').decode('utf-8')
                if next_val == current:
                    break
                current = next_val
            else:
                break
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return current

def parse_author_name(name):
    if not name:
        return "", ""
    full_name = name.strip()
    full_name = " ".join(full_name.split())
    if "," in full_name:
        parts = full_name.split(",", 1)
        apellido = parts[0].strip()
        nombre = parts[1].strip()
    else:
        parts = full_name.rsplit(" ", 1)
        if len(parts) == 2:
            nombre = parts[1].strip()
            apellido = parts[0].strip()
        else:
            nombre = full_name
            apellido = ""
    return nombre, apellido

def parse_year(year_val):
    if not year_val:
        return None
    year_str = str(year_val).strip()
    match = re.search(r'\b(1\d{3}|20\d{2})\b', year_str)
    if match:
        return int(match.group(1))
    return None

def parse_date(date_val):
    if not date_val:
        return None
    date_str = str(date_val).strip()
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    if len(date_str) == 4 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, '%Y').date()
        except ValueError:
            pass
    return None

def parse_numero_entrada(val):
    if val is None:
        return ""
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val)
    return str(val).strip()

def parse_values_string(val_str):
    rows = []
    current_row = []
    in_string = False
    string_char = None
    escaped = False
    current_val = []
    current_val_is_string = False
    paren_depth = 0
    
    i = 0
    n = len(val_str)
    while i < n:
        c = val_str[i]
        if escaped:
            current_val.append(c)
            escaped = False
            i += 1
            continue
            
        if c == '\\':
            escaped = True
            i += 1
            continue
            
        if in_string:
            if c == string_char:
                if i + 1 < n and val_str[i+1] == string_char:
                    current_val.append(c)
                    i += 2
                    continue
                else:
                    in_string = False
            else:
                current_val.append(c)
            i += 1
            continue
            
        if c in ("'", '"'):
            in_string = True
            string_char = c
            current_val_is_string = True
            i += 1
            continue
            
        if c == '(':
            paren_depth += 1
            if paren_depth == 1:
                current_row = []
            else:
                current_val.append(c)
            i += 1
            continue
            
        if c == ')':
            paren_depth -= 1
            if paren_depth == 0:
                val = "".join(current_val).strip()
                current_row.append((val, current_val_is_string))
                rows.append(current_row)
                current_val = []
                current_val_is_string = False
            else:
                current_val.append(c)
            i += 1
            continue
            
        if c == ',':
            if paren_depth == 1:
                val = "".join(current_val).strip()
                current_row.append((val, current_val_is_string))
                current_val = []
                current_val_is_string = False
            elif paren_depth == 0:
                pass
            else:
                current_val.append(c)
            i += 1
            continue
            
        if c.isspace() and paren_depth == 0:
            i += 1
            continue
            
        if paren_depth > 0:
            current_val.append(c)
        i += 1
        
    processed_rows = []
    for row in rows:
        processed_row = []
        for val, is_str in row:
            if not is_str and val.upper() == 'NULL':
                processed_row.append(None)
            elif is_str:
                processed_row.append(val)
            else:
                try:
                    if '.' in val:
                        processed_row.append(float(val))
                    else:
                        processed_row.append(int(val))
                except ValueError:
                    processed_row.append(val)
        processed_rows.append(processed_row)
    return processed_rows

def extract_inserts(text, table_name):
    pattern = rf'INSERT INTO\s+\x60{table_name}\x60\s*\x28([^\x29]+)\x29\s*VALUES\s*(.*?);'
    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
    
    columns = []
    rows = []
    
    for match in matches:
        cols_str = match.group(1)
        cols = [c.strip().strip('`').strip('"').strip("'") for c in cols_str.split(',')]
        if not columns:
            columns = cols
        
        values_str = match.group(2)
        parsed_rows = parse_values_string(values_str)
        for r in parsed_rows:
            row_dict = {}
            for col, val in zip(cols, r):
                row_dict[col] = val
            rows.append(row_dict)
            
    return columns, rows

def get_value_by_key_pattern(row_dict, pattern):
    for k, v in row_dict.items():
        if re.search(pattern, k, re.IGNORECASE):
            return v
    return None

def main():
    sql_path = r"C:\Users\dario\Downloads\biblioteca.sql"
    if not os.path.exists(sql_path):
        print(f"Error: El archivo SQL no existe en la ruta {sql_path}")
        sys.exit(1)
        
    print(f"Cargando archivo SQL desde {sql_path} (usando codificación latin1)...")
    with open(sql_path, "r", encoding="latin1") as f:
        text = f.read()
        
    print("Extrayendo inserciones SQL en memoria...")
    _, facultad_rows = extract_inserts(text, 'facultad')
    _, carreras_rows = extract_inserts(text, 'carreras')
    _, generos_rows = extract_inserts(text, 'generos')
    _, editoriales_rows = extract_inserts(text, 'editoriales')
    _, autores_rows = extract_inserts(text, 'autores')
    _, tipo_material_rows = extract_inserts(text, 'tipo_material')
    _, materiales_rows = extract_inserts(text, 'materiales')
    _, mat_autores_rows = extract_inserts(text, 'materiales_y_autores')
    _, mat_carreras_rows = extract_inserts(text, 'materiales_y_carreras')
    _, mat_generos_rows = extract_inserts(text, 'materiales_y_generos')

    print(f"Registros extraídos:")
    print(f" - Facultades: {len(facultad_rows)}")
    print(f" - Carreras: {len(carreras_rows)}")
    print(f" - Géneros: {len(generos_rows)}")
    print(f" - Editoriales: {len(editoriales_rows)}")
    print(f" - Autores: {len(autores_rows)}")
    print(f" - Tipos de Material: {len(tipo_material_rows)}")
    print(f" - Materiales: {len(materiales_rows)}")
    print(f" - Materiales-Autores: {len(mat_autores_rows)}")
    print(f" - Materiales-Carreras: {len(mat_carreras_rows)}")
    print(f" - Materiales-Géneros: {len(mat_generos_rows)}")

    # Iniciar la importación dentro de una transacción atómica para asegurar rapidez e integridad
    print("\nIniciando la transacción en la base de datos...")
    with transaction.atomic():
        # 1. Facultades
        print("Importando Facultades...")
        facultades_cache = {}
        for row in facultad_rows:
            id_fac = row['idfacultad']
            nombre = fix_double_utf8(row['descripcion']).strip()[:100]
            fac, _ = Facultad.objects.update_or_create(
                id_facultad=id_fac,
                defaults={'nombre': nombre}
            )
            facultades_cache[id_fac] = fac
        print(f" - Facultades importadas: {len(facultades_cache)}")

        # 2. Carreras
        print("Importando Carreras...")
        carreras_cache = {}
        for row in carreras_rows:
            id_car = row['id_carrera']
            nombre = fix_double_utf8(row['nombre_carrera']).strip()[:100]
            fac_id = row['facultad_idfacultad']
            fac = facultades_cache.get(fac_id)
            if not fac:
                # Si por alguna razón no existe la facultad, intentamos obtenerla o crear una por defecto
                fac, _ = Facultad.objects.get_or_create(id_facultad=fac_id, defaults={'nombre': f'Facultad {fac_id}'})
                facultades_cache[fac_id] = fac
            
            carrera, _ = Carrera.objects.update_or_create(
                id_carrera=id_car,
                defaults={
                    'nombre': nombre,
                    'facultades_id_facultad': fac
                }
            )
            carreras_cache[id_car] = carrera
        print(f" - Carreras importadas: {len(carreras_cache)}")

        # 3. Géneros
        print("Importando Géneros...")
        generos_cache = {}
        for row in generos_rows:
            id_gen = row['id_genero']
            nombre = fix_double_utf8(row['nombre_genero']).strip()[:50]
            gen, _ = Genero.objects.update_or_create(
                id_genero=id_gen,
                defaults={'nombre': nombre}
            )
            generos_cache[id_gen] = gen
        print(f" - Géneros importados: {len(generos_cache)}")

        # 4. Editoriales
        print("Importando Editoriales...")
        editoriales_cache = {}
        for row in editoriales_rows:
            id_ed = row['id_editorial']
            nombre = fix_double_utf8(row['nombre_editorial']).strip()[:100]
            ed, _ = Editorial.objects.update_or_create(
                id_editorial=id_ed,
                defaults={
                    'nombre': nombre,
                    'direccion': '',
                    'telefono': ''
                }
            )
            editoriales_cache[id_ed] = ed
        print(f" - Editoriales importadas: {len(editoriales_cache)}")

        # 5. Autores
        print("Importando Autores...")
        autores_cache = {}
        for row in autores_rows:
            id_aut = row['id_autor']
            nombre_raw = fix_double_utf8(row['nombre_autor'])
            nombre, apellido = parse_author_name(nombre_raw)
            aut, _ = Autor.objects.update_or_create(
                id_autor=id_aut,
                defaults={
                    'nombre': nombre[:100],
                    'apellido': apellido[:100]
                }
            )
            autores_cache[id_aut] = aut
        print(f" - Autores importados: {len(autores_cache)}")

        # 6. Tipo de Material / TipoDocumento mapping
        print("Configurando Tipos de Documento...")
        tipo_material_mapping = {}
        for row in tipo_material_rows:
            id_tm = row['id_tipo_material']
            desc_raw = fix_double_utf8(row['descripcion_material']).strip()
            desc = desc_raw.title()
            
            # Normalizar nombres comunes
            if desc.upper() == 'LIBRO':
                desc = 'Libro'
            elif desc.upper() in ('REVISTA', 'REVISTA CIENTÍFICA'):
                desc = 'Revista Científica'
            elif desc.upper() in ('TESIS', 'TESIS DE GRADO', 'LIBRO DE TESIS'):
                desc = 'Tesis'
                
            td, _ = TipoDocumento.objects.get_or_create(
                descripcion=desc[:50]
            )
            tipo_material_mapping[id_tm] = (td, desc_raw)
        print(f" - Tipos de Documento cargados/creados.")

        # Obtener Categorias del Django (Literatura, Fantasía, Informática, etc.)
        categorias_db = {c.id_categoria: c for c in Categoria.objects.all()}

        # 7. Materiales
        print("Importando Materiales (este paso puede tardar unos segundos)...")
        materials_cache = {}
        
        # Primero desactivamos las señales si existieran para acelerar la creación
        total_materials = len(materiales_rows)
        for idx, row in enumerate(materiales_rows, 1):
            id_mat = row['id_material']
            
            # Título
            titulo = fix_double_utf8(row['titulo']).strip()[:200]
            
            # ISBN / ISSN
            isbn = row['ISBN'].strip()[:20] if row['ISBN'] else None
            issn = row['ISSN'].strip()[:20] if row['ISSN'] else None
            
            # Año de publicación
            year_val = row.get('año_publicacion') or row.get('ao_publicacion') or get_value_by_key_pattern(row, 'a.*o_publicacion')
            año = parse_year(year_val)
            
            # Estado del material
            estado = row['estado'].upper().strip()[:50] if row['estado'] else 'DISPONIBLE'
            
            # Editorial
            ed_id = row['editoriales_id_editorial']
            editorial_obj = editoriales_cache.get(ed_id)
            
            # Fecha ingreso
            fecha_ing = parse_date(row['fecha_ingreso'])
            
            # Numeración Dewey
            dewey = row['numeracion_dewey'].strip()[:50] if row['numeracion_dewey'] else None
            
            # Número de entrada
            num_entrada = parse_numero_entrada(row['numero_entrada'])[:50]
            
            # Título de grado
            grado = fix_double_utf8(row['titulo_grado']).strip()[:100] if row['titulo_grado'] else None
            
            # Edición
            edicion = fix_double_utf8(row['edicion']).strip()[:50] if row['edicion'] else None
            
            # Categoría
            cat_id = row['categoria']
            categoria_obj = categorias_db.get(cat_id)
            if not categoria_obj and cat_id:
                # Si la categoría no existe en el sistema actual, la creamos al vuelo
                categoria_obj, _ = Categoria.objects.get_or_create(
                    id_categoria=cat_id,
                    defaults={'nombre': f'Categoría {cat_id}', 'descripcion': 'Importada del sistema anterior'}
                )
                categorias_db[cat_id] = categoria_obj
                
            # Tipo Material y Registro
            tm_id = row['tipo_material_id_tipo_material']
            tipodoc_obj = None
            tipo_material_desc = None
            if tm_id in tipo_material_mapping:
                tipodoc_obj, tipo_material_desc = tipo_material_mapping[tm_id]
                
            tipo_reg = 'LIBRO'
            if tipo_material_desc:
                desc_upper = tipo_material_desc.upper()
                if any(w in desc_upper for w in ('TESIS', 'TRABAJO DE INVESTIGACION', 'INVESTIGACION', 'MAESTRÍA', 'ESPECIALIZACIÓN')):
                    tipo_reg = 'TRABAJO_INVESTIGACION'
                elif 'LIBRO' in desc_upper:
                    tipo_reg = 'LIBRO'
                else:
                    tipo_reg = 'OTROS'
                    
            # Crear o actualizar
            mat, _ = Material.objects.update_or_create(
                id_material=id_mat,
                defaults={
                    'titulo': titulo,
                    'isbn': isbn,
                    'issn': issn,
                    'año_publicacion': año,
                    'cantidad_total': 1,
                    'cantidad_disponible': 1,
                    'numeracion_dewey': dewey,
                    'numero_entrada': num_entrada,
                    'estado_material': estado,
                    'fecha_ingreso': fecha_ing,
                    'edicion': edicion,
                    'numero_paginas': None,
                    'descripcion': None,
                    'titulo_grado': grado,
                    'tipo_trabajo': tipo_material_desc[:100] if tipo_material_desc else None,
                    'tipo_material': tipo_material_desc[:100] if tipo_material_desc else None,
                    'tipo_registro': tipo_reg,
                    'editoriales_id_editorial': editorial_obj,
                    'categorias_id_categoria': categoria_obj,
                    'tipodocumento_id_tipo': tipodoc_obj
                }
            )
            materials_cache[id_mat] = mat
            
            if idx % 2000 == 0:
                print(f" - Materiales procesados: {idx} / {total_materials}...")

        print(f" - Materiales importados: {len(materials_cache)}")

        # 8. Relaciones: Materiales y Autores
        print("Importando Relaciones de Autores por Material...")
        material_autor_relations = []
        seen_relations = set()
        for row in mat_autores_rows:
            mat_id = row['materiales_id_material']
            aut_id = row['autores_id_autor']
            if mat_id in materials_cache and aut_id in autores_cache:
                pair = (mat_id, aut_id)
                if pair not in seen_relations:
                    seen_relations.add(pair)
                    material_autor_relations.append(
                        Material.autores_id_autor.through(
                            material_id=mat_id,
                            autor_id=aut_id
                        )
                    )
        # Limpiar existentes y recrear en lote
        Material.autores_id_autor.through.objects.all().delete()
        Material.autores_id_autor.through.objects.bulk_create(material_autor_relations, batch_size=1000)
        print(f" - Relaciones de Autores importadas: {len(material_autor_relations)}")

        # 9. Relaciones: Materiales y Carreras
        print("Importando Relaciones de Carreras por Material...")
        material_carrera_relations = []
        seen_relations = set()
        for row in mat_carreras_rows:
            mat_id = row['materiales_id_material']
            car_id = row['carreras_id_carrera']
            if mat_id in materials_cache and car_id in carreras_cache:
                pair = (mat_id, car_id)
                if pair not in seen_relations:
                    seen_relations.add(pair)
                    material_carrera_relations.append(
                        MaterialCarrera(
                            materiales_id_material_id=mat_id,
                            carreras_id_carrera_id=car_id
                        )
                    )
        # Limpiar existentes y recrear en lote
        MaterialCarrera.objects.all().delete()
        MaterialCarrera.objects.bulk_create(material_carrera_relations, batch_size=1000)
        print(f" - Relaciones de Carreras importadas: {len(material_carrera_relations)}")

        # 10. Relaciones: Materiales y Géneros
        print("Importando Relaciones de Géneros por Material...")
        material_genero_relations = []
        seen_relations = set()
        for row in mat_generos_rows:
            mat_id = row['materiales_id_material']
            gen_id = row['generos_id_genero']
            if mat_id in materials_cache and gen_id in generos_cache:
                pair = (mat_id, gen_id)
                if pair not in seen_relations:
                    seen_relations.add(pair)
                    material_genero_relations.append(
                        MaterialGenero(
                            materiales_id_material_id=mat_id,
                            generos_id_genero_id=gen_id
                        )
                    )
        # Limpiar existentes y recrear en lote
        MaterialGenero.objects.all().delete()
        MaterialGenero.objects.bulk_create(material_genero_relations, batch_size=1000)
        print(f" - Relaciones de Géneros importadas: {len(material_genero_relations)}")

    print("\n¡Importación completada exitosamente!")

if __name__ == "__main__":
    main()
