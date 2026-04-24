import re

def limpiar_texto(texto):
    return texto.upper()

def extraer_curp(texto):

    texto = texto.replace(" ", "").replace("\n", "")

    match = re.search(
        r"[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]",
        texto
    )

    return match.group(0) if match else ""

def extraer_sexo_curp(curp):
    if not curp:
        return ""

    return "M" if curp[10] == "H" else "F"

def extraer_fecha(texto):

    texto = texto.replace(" ", "").replace("\n", "")

    match = re.search(r"FECHADENACIMIENTO([0-9]{2}/[0-9]{2}/[0-9]{4})", texto)
    if match:
        return match.group(1)

    fechas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)

    for f in fechas:
        if not f.startswith("00"):
            return f

    return ""

def extraer_nombre(texto):

    texto = limpiar_texto(texto)

    basura = [
        "INSTITUTO", "NACIONAL", "ELECTORAL",
        "CREDENCIAL", "VOTAR", "DOMICILIO",
        "CLAVE", "ELECTOR", "CURP", "PARA"
    ]

    palabras = re.findall(r"\b[A-ZÑ]{3,}\b", texto)

    palabras = [p for p in palabras if p not in basura]

    palabras_invalidas = [
        "MEXICO", "ESTADO", "FEDERAL", "SECCION",
        "REGISTRO", "NACIMIENTO"
    ]

    palabras = [p for p in palabras if p not in palabras_invalidas]

    for i in range(len(palabras) - 2):

        p1, p2, p3 = palabras[i], palabras[i+1], palabras[i+2]

        if len(p1) > 3 and len(p2) > 3 and len(p3) > 3:
            return {
                "apellido_paterno": p1,
                "apellido_materno": p2,
                "nombre": p3
            }

    return {
        "nombre": "",
        "apellido_paterno": "",
        "apellido_materno": ""
    }

def extraer_domicilio(texto):

    domicilio = {
        "calle": "",
        "numero": "",
        "colonia": "",
        "municipio": "",
        "estado": "",
        "cp": ""
    }

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for i, linea in enumerate(lineas):

        if "DOMICILIO" in linea:

            bloque = lineas[i+1:i+6]
            bloque_texto = " ".join(bloque)

            if len(bloque) > 0:
                domicilio["calle"] = bloque[0]

            num = re.search(r"\b\d{1,5}\b", bloque_texto)
            if num:
                domicilio["numero"] = num.group(0)

            cp_match = re.search(r"\b\d{5}\b", bloque_texto)
            if cp_match:
                domicilio["cp"] = cp_match.group(0)

            for linea_b in bloque:
                if "FRACC" in linea_b or "COL" in linea_b:
                    domicilio["colonia"] = re.sub(r"\b\d{5}\b", "", linea_b).strip()
                    break

            municipios = ["TARIMBARO", "MORELIA", "URUAPAN"]
            for m in municipios:
                if m in bloque_texto:
                    domicilio["municipio"] = m

            estados = ["MICH", "JAL", "CDMX", "EDOMEX"]
            for e in estados:
                if e in bloque_texto:
                    domicilio["estado"] = e

            break

    return domicilio