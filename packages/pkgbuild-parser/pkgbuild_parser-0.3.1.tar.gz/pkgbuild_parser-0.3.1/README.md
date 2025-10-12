# pkgbuild_parser

[English documentation (GitHub)](https://github.com/KevinCrrl/pkgbuild_parser/blob/main/ingles.md)
[English documentation (Codeberg)](https://codeberg.org/KevinCrrl/pkgbuild_parser/src/branch/main/ingles.md)

## Introducción

**pkgbuild_parser** es un módulo escrito en **Python** (compatible con Python 3.x) diseñado para extraer información básica de un **PKGBUILD** de Arch Linux.El propósito principal de este módulo es proporcionar un acceso sencillo y directo a los campos más importantes de un PKGBUILD sin depender de herramientas externas ni librerías adicionales.

- **Versión:** 0.3.1
- **Licencia:** MIT 2025 KevinCrrl
- **Dependencias:** Ninguna
- **Estilo:** Simplicidad, sin dependencias externas, fácil de usar

Este módulo permite obtener datos como el nombre del paquete, versión, descripción, licencia, URL y archivo fuente de manera rápida y directa.

---

## Funciones principales para el usuario

Aunque internamente el módulo tiene funciones de soporte (`get_base`), el **usuario solo necesita usar las funciones de alto nivel**, que son claras y directas:

| Función                                              | Descripción                                                                                                      |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `get_pkgname()`                                     | Retorna el nombre del paquete (`pkgname`) como string.                                                          |
| `get_pkgver()`                                      | Retorna la versión del paquete (`pkgver`) como string.                                                         |
| `get_pkgrel()`                                      | Retorna el número de release (`pkgrel`) como string.                                                           |
| `get_pkgdesc()`                                     | Retorna la descripción del paquete (`pkgdesc`) como string, eliminando comentarios y paréntesis innecesarios. |
| `get_arch()`                                        | Retorna la arquitectura del paquete (`arch`) como una lista de strings.                                                       |
| `get_url()`                                         | Retorna la URL principal del proyecto (`url`) como string.                                                      |
| `get_license()`                                     | Retorna la licencia del paquete (`license`) como string, sin comentarios ni paréntesis extra.                  |
| `get_source()`                                      | Retorna la(s) fuente(s) (`source`) del paquete como una lista de strings.                                       |
| `get_dict_base_info()`                              | Retorna un diccionario con todos los campos anteriores en formato `{'pkgname': ..., 'pkgver': ..., ...}`.       |
| `base_info_to_json()`                               | Retorna la información base en formato**JSON** con indentación y codificación UTF-8.                     |
| `write_base_info_to_json(json_name)`                | Escribe la información base en un archivo JSON con nombre `json_name`.                                         |
| `remove_quotes(string)`                             | Elimina las comillas de un string.                                                                                |
| `get_dict_base_info_without_quotes()`               | Retorna un diccionario con la información base pero sin comillas en sus valores.                                 |
| `base_info_to_json_without_quotes()`                | Retorna la información base en formato **JSON** sin comillas en sus valores.                              |
| `write_base_info_to_json_without_quotes(json_name)` | Escribe la información base en un archivo JSON sin comillas en sus valores.                                      |
| `get_epoch()`                                       | Retorna la `epoch` del paquete.                                                                                 |
| `get_full_package_name()`                           | Retorna el nombre completo del paquete, incluyendo `epoch`, versión y `pkgrel`.                              |
| `get_depends()`                                     | Retorna una lista de las dependencias del paquete.                                                              |
| `get_makedepends()`                                 | Retorna una lista de las dependencias de compilación del paquete.                                               |
| `get_optdepends()`                                  | Retorna una lista de las dependencias opcionales del paquete.                                                   |
| `get_dict_optdepends()`                             | Retorna un diccionario de las dependencias opcionales del paquete.                                              |

**Nota:** Las funciones internas (`get_base` y `multiline`) están pensadas para uso del módulo y **no necesita ser usada por el usuario**.

---

## Instalación y uso

### Opción 1: AUR

El módulo está disponible en el AUR como **`python-pkgbuild-parser`**:

### Opción 2: Construcción manual

Si deseas construirlo manually:

```bash
python -m build
python -m installer --destdir=/ruta/de/instalacion dist/*.whl
```

## Uso básico

```python
import pkgbuild_parser
import sys

try:
    mi_pkgbuild = pkgbuild_parser.Parser("PKGBUILD")
except pkgbuild_parser.ParserFileError as exc:
    print(exc)
    sys.exit(1)

# Obtener datos básicos
try:
    print(mi_pkgbuild.get_pkgname())
    print(mi_pkgbuild.get_pkgver())
    print(mi_pkgbuild.get_pkgrel())
    print(mi_pkgbuild.get_pkgdesc())
    print(mi_pkgbuild.get_arch())
    print(mi_pkgbuild.get_url())
    print(mi_pkgbuild.get_license())
    print(mi_pkgbuild.get_source())
    print(mi_pkgbuild.get_epoch())
    print(mi_pkgbuild.get_full_package_name())
    print(mi_pkgbuild.get_depends())
    print(mi_pkgbuild.get_makedepends())
    print(mi_pkgbuild.get_optdepends())
    print(mi_pkgbuild.get_dict_optdepends())

    # Obtener un diccionario de toda la info
    info = mi_pkgbuild.get_dict_base_info()
    print(info)

    # Mostrar en formato JSON
    print(mi_pkgbuild.base_info_to_json())

    # Obtener JSON y escribirlo a archivo
    mi_pkgbuild.write_base_info_to_json("info.json")

    # Uso de remove_quotes
    cadena_con_comillas = mi_pkgbuild.get_pkgdesc()
    cadena_sin_comillas = pkgbuild_parser.remove_quotes(cadena_con_comillas)
    print(f"Cadena original: {cadena_con_comillas}")
    print(f"Cadena sin comillas: {cadena_sin_comillas}")
except (pkgbuild_parser.ParserKeyError, pkgbuild_parser.ParserNoneTypeError) as e:
    print(e)
```

## Manejo de errores

Si el archivo PKGBUILD no existe, se lanza un `ParserFileError`, que debe ser capturado para evitar que el programa falle.

También puede ocurrir que se lanza un `ParserKeyError` en caso de que la obtención de un valor del PKGBUILD falle, por ejemplo, si license no está bien declarado, y se hace get_license() se producirá dicha excepción.

Desde la versión 0.2.0, también se puede lanzar un `ParserNoneTypeError` si una función retorna `None` cuando no se esperaba.

## Limitaciones

- El objetivo del módulo es extraer únicamente **información básica** de PKGBUILD estándar.
- Funciona mejor con PKGBUILD que siguen las normas de la **Arch Wiki**.
- Desde la versión 0.3.0, el módulo puede extraer información de arrays o listas, como `depends`, `makedepends`, `source` y `optdepends`.