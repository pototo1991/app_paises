import requests
import random
import unicodedata
from django.shortcuts import render, redirect
from .translations import TRANSLATIONS
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse


# Función para traducir automáticamente textos según el archivo translations.py
def translate(text):
    return TRANSLATIONS.get(text, text)


def index(request):
    try:
        return render(request, "index.html")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def principal(request):
    response = requests.get("https://restcountries.com/v3.1/all")
    countries = response.json()

    query = request.GET.get("query", "")
    region = request.GET.get("region", "")

    # Filtrar por nombre de país
    if query:
        query_normalized = normalize(query)
        matching_country = next(
            (
                country
                for country in countries
                if query_normalized
                in normalize(country["translations"]["spa"]["common"])
            ),
            None,
        )
        if matching_country:
            country_name = matching_country["translations"]["spa"]["common"]
            return redirect("country_detail", country_name=country_name)

    # Filtrar por región
    if region:
        region_normalized = normalize(region)
        countries = [
            country
            for country in countries
            if region_normalized == normalize(country.get("region", ""))
        ]

    countries = [
        {
            "nombre": country["translations"]["spa"]["common"],
            "bandera": country["flags"]["svg"],
            "capital": country["capital"][0] if country.get("capital") else "N/A",
            "region": translate(country.get("region", "Desconocido")),
            "subregion": translate(country.get("subregion", "Desconocido")),
            "poblacion": f"{int(country.get('population', 0)):,}".replace(",", ".")
            + " habitantes",
            "area": f"{int(country.get('area', 0)):,}".replace(",", ".") + " km²",
        }
        for country in countries
        if country.get("translations") and country["translations"]["spa"]["common"]
    ]

    countries.sort(
        key=lambda x: x["nombre"]
    )  # Ordenar alfabéticamente por el nombre en español
    total_countries = len(countries)

    return render(
        request,
        "principal.html",
        {
            "countries": countries,
            "total_countries": total_countries,
            "query": "",
            "region": "",
        },
    )


def country_detail(request, country_name):
    response = requests.get("https://restcountries.com/v3.1/all")
    countries = response.json()
    country_data = next(
        (
            c
            for c in countries
            if normalize(c["translations"]["spa"]["common"]) == normalize(country_name)
        ),
        None,
    )

    query = request.GET.get("query", "")

    # Filtrar por nombre de país
    if query:
        query_normalized = normalize(query)
        matching_country = next(
            (
                country
                for country in countries
                if query_normalized
                in normalize(country["translations"]["spa"]["common"])
            ),
            None,
        )
        if matching_country:
            country_name = matching_country["translations"]["spa"]["common"]
            return redirect("country_detail", country_name=country_name)

    if country_data:
        # Valores predeterminados
        DEFAULT_FLAG = (
            "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
        )
        DEFAULT_COAT = (
            "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
        )

        # Crear el objeto `country` con manejo de claves faltantes
        country = {
            "nombre": country_data["translations"]["spa"]["common"],
            "nombre_oficial": country_data["translations"]["spa"]["official"],
            "bandera": country_data["flags"].get("svg", DEFAULT_FLAG),
            "escudo": country_data.get("coatOfArms", {}).get("svg", DEFAULT_COAT),
            "capital": (
                country_data["capital"][0] if country_data.get("capital") else "N/A"
            ),
            "region": translate(country_data.get("region", "Desconocido")),
            "subregion": translate(country_data.get("subregion", "Desconocido")),
            "poblacion": f"{int(country_data.get('population', 0)):,}".replace(
                ",", "."
            ),
            "area": f"{int(country_data.get('area', 0)):,}".replace(",", ".") + " km²",
            "latlng": country_data.get("latlng", ["N/A", "N/A"]),
            "fronteras": (
                ", ".join(
                    [translate(border) for border in country_data.get("borders", [])]
                )
                if country_data.get("borders")
                else "No tiene"
            ),
            "monedas": (
                [
                    translate(currency["name"])
                    for currency in country_data.get("currencies", {}).values()
                ]
                if country_data.get("currencies")
                else ["Desconocida"]
            ),
            "idiomas": (
                [translate(lang) for lang in country_data.get("languages", {}).values()]
                if country_data.get("languages")
                else ["Desconocidos"]
            ),
            "continentes": (
                ", ".join(
                    [
                        translate(continent)
                        for continent in country_data.get("continents", [])
                    ]
                )
                if country_data.get("continents")
                else "Desconocido"
            ),
            "tld": (
                ", ".join(country_data.get("tld", []))
                if country_data.get("tld")
                else "N/A"
            ),
            "independencia": "Sí" if country_data.get("independent") else "No",
            "maps": country_data["maps"].get("googleMaps", "N/A"),
            "fifa": country_data.get("fifa", "N/A"),
            "zona_horaria": ", ".join(country_data.get("timezones", ["N/A"])),
            "demonyms": country_data.get("demonyms", {}).get("eng", {}).get("f", "N/A")
            + " / "
            + country_data.get("demonyms", {}).get("eng", {}).get("m", "N/A"),
            "start_of_week": country_data.get("startOfWeek", "Desconocido"),
            "capital_info": country_data.get("capitalInfo", {"latlng": ["N/A", "N/A"]}),
            "codigo_postal": country_data.get(
                "postalCode", {"format": "N/A", "regex": "N/A"}
            ),
        }
        return render(request, "country_detail.html", {"country": country})
    else:
        return render(request, "404.html", {"message": "País no encontrado"})


def normalize(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).lower()


def game(request):
    # Obtener datos de la API
    response = requests.get("https://restcountries.com/v3.1/all")
    countries = response.json()

    # Inicializar contadores desde la sesión
    correct_count = request.session.get("correct_count", 0)
    incorrect_count = request.session.get("incorrect_count", 0)
    change_flag_count = request.session.get("change_flag_count", 0)

    # Obtener los parámetros de filtro desde la solicitud
    query = request.GET.get("query", "").strip().lower()
    region = request.GET.get("region", "").strip()

    # Filtrar países por región
    if region:
        countries = [
            country
            for country in countries
            if country.get("region", "").lower() == region.lower()
        ]

    # Filtrar países por nombre si se ingresó un término de búsqueda
    if query:
        countries = [
            country
            for country in countries
            if query in country["translations"]["spa"]["common"].lower()
        ]

    # Validar si hay países después del filtro
    if not countries:
        return render(
            request,
            "game.html",
            {
                "country": None,
                "correct_count": correct_count,
                "incorrect_count": incorrect_count,
                "change_flag_count": change_flag_count,
                "message": "No se encontraron países que coincidan con los criterios.",
            },
        )

    # Procesar respuesta del usuario
    if request.method == "POST":
        user_answer = normalize(request.POST.get("answer").strip())
        correct_answer = normalize(request.POST.get("correct_answer").strip())
        country_bandera = request.POST.get("country_bandera")

        if user_answer == correct_answer:
            result = "¡Correcto!"
            correct_count += 1
        else:
            result = (
                f"Incorrecto. La respuesta correcta es {correct_answer.capitalize()}."
            )
            incorrect_count += 1

        request.session["correct_count"] = correct_count
        request.session["incorrect_count"] = incorrect_count

        return render(
            request,
            "game.html",
            {
                "country": {
                    "nombre": translate(correct_answer.capitalize()),
                    "bandera": country_bandera,
                },
                "result": result,
                "correct_count": correct_count,
                "incorrect_count": incorrect_count,
                "change_flag_count": change_flag_count,
            },
        )

    # Incrementar contador si se cambia de bandera
    elif request.method == "GET" and "change_flag" in request.GET:
        change_flag_count += 1
        request.session["change_flag_count"] = change_flag_count

    # Seleccionar un país al azar después del filtrado
    random_country = random.choice(countries)
    country = {
        "nombre": translate(random_country["translations"]["spa"]["common"]),
        "bandera": random_country["flags"]["svg"],
    }

    # Renderizar la página del juego
    return render(
        request,
        "game.html",
        {
            "country": country,
            "correct_answer": country["nombre"],
            "country_bandera": country["bandera"],
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "change_flag_count": change_flag_count,
            "query": query,
            "region": region,
        },
    )


@csrf_exempt
def reset_counters(request):
    if request.method == "POST":
        request.session["correct_count"] = 0
        request.session["incorrect_count"] = 0
        request.session["change_flag_count"] = 0
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)
