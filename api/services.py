import re

from rdflib import Graph, RDF, URIRef

g = Graph()
g.parse("api/ontology/Hasimboly_Ontologie_expert.ttl", format="turtle")

NAMESPACE = "http://www.semanticweb.org/tsanta/ontologies/2026/4/untitled-ontology-12/"
prefix = f"PREFIX : <{NAMESPACE}>"

_IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")

def get_culture_caracteristics(culture_name):
    culture_caracteristics_query = f"""
    {prefix}

    SELECT ?predicate ?object
    WHERE {{
        :{culture_name} ?predicate ?object .
    }}
    """

    results = g.query(culture_caracteristics_query)
    print('Le resultat est : ', results)
    data = []

    for row in results:
        data.append({
            "predicate": str(row.predicate).split("/")[-1],
            "object": str(row.object).split("/")[-1]
        })

    return data

def get_cultures(region=None, climate=None, soil=None):
    region = _normalise_identifier(region)
    climate = _normalise_identifier(climate)
    soil = _normalise_identifier(soil)

    if not any((region, climate, soil)):
        return []

    levels = []
    if region and climate and soil:
        levels.append(("exact", 100, "Mifanaraka amin'ny faritra, toetrandro ary karazana tany", lambda: _cultures_for_region(region, climate, soil)))
    if region and climate:
        levels.append(("region_climate", 85, "Mifanaraka amin'ny faritra sy toetrandro", lambda: _cultures_for_region(region, climate)))
    if region and soil:
        levels.append(("region_soil", 80, "Mifanaraka amin'ny faritra sy karazana tany", lambda: _cultures_for_region(region, soil=soil)))
    if region:
        levels.append(("region", 70, "Mifanaraka amin'ny faritra", lambda: _cultures_for_region(region)))
    if climate and soil:
        levels.append(("climate_soil", 60, "Mifanaraka amin'ny toetrandro sy karazana tany", lambda: _cultures_for_climate_or_soil(climate, soil)))
    if climate:
        levels.append(("climate", 50, "Mifanaraka amin'ny toetrandro", lambda: _cultures_for_climate_or_soil(climate=climate)))
    if soil:
        levels.append(("soil", 40, "Mifanaraka amin'ny karazana tany", lambda: _cultures_for_climate_or_soil(soil=soil)))

    for level, score, message, finder in levels:
        cultures = finder()
        if cultures:
            return [
                {
                    "culture": culture,
                    "season": season,
                    "score": score,
                    "match_level": level,
                    "match_message": message,
                }
                for culture, season in cultures
            ]

    return []


def _normalise_identifier(value):
    if value is None:
        return None
    value = str(value).strip().lower()
    return None if value in {"", "none", "null"} else value


def _uri(identifier):
    if not identifier or not _IDENTIFIER.fullmatch(identifier):
        return None
    return URIRef(NAMESPACE + identifier)


def _cultures_for_region(region, climate=None, soil=None):
    region_uri = _uri(region)
    climate_uri = _uri(climate)
    soil_uri = _uri(soil)
    if not region_uri or (climate and not climate_uri) or (soil and not soil_uri):
        return []
    if climate_uri and (region_uri, URIRef(NAMESPACE + "aPourClimat"), climate_uri) not in g:
        return []
    if soil_uri and (region_uri, URIRef(NAMESPACE + "aPourTypeDeSol"), soil_uri) not in g:
        return []
    return _cultures_in_regions({region_uri})


def _cultures_for_climate_or_soil(climate=None, soil=None):
    climate_uri = _uri(climate)
    soil_uri = _uri(soil)
    if (climate and not climate_uri) or (soil and not soil_uri):
        return []
    regions = set()
    for region_uri in g.subjects(RDF.type, URIRef(NAMESPACE + "Region")):
        if climate_uri and (region_uri, URIRef(NAMESPACE + "aPourClimat"), climate_uri) not in g:
            continue
        if soil_uri and (region_uri, URIRef(NAMESPACE + "aPourTypeDeSol"), soil_uri) not in g:
            continue
        regions.add(region_uri)
    return _cultures_in_regions(regions)


def _cultures_in_regions(regions):
    result = []
    seen = set()
    for culture in g.subjects(RDF.type, URIRef(NAMESPACE + "Culture")):
        if not any((culture, URIRef(NAMESPACE + "estLocaliseeDans"), region) in g for region in regions):
            continue
        for season in g.objects(culture, URIRef(NAMESPACE + "seCultiveDurant")):
            item = (str(culture).rsplit("/", 1)[-1], str(season).rsplit("/", 1)[-1])
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


# def get_cultures(region=None, climate=None, soil=None):

#     filters = []

#     if region:
#         filters.append(f"?culture :estLocaliseeDans :{region} .")

#     if climate:
#         filters.append(f"""
#             ?region rdf:type :Region .
#             ?region :aPourClimat :{climate} .
#             ?culture :estLocaliseeDans ?region .
#         """)

#     if soil:
#         filters.append(f"""
#             ?region :aPourTypeDeSol :{soil} .
#             ?culture :estLocaliseeDans ?region .
#         """)

#     filters_query = "\n".join(filters)

#     query = f"""
#     {prefix}

#     SELECT DISTINCT ?culture ?season
#     WHERE {{

#         ?culture rdf:type :Culture .
#         ?culture :estLocaliseeDans ?region .
#         ?culture :seCultiveDurant ?season .

#         {filters_query}
#     }}
#     """

#     results = g.query(query)

#     data = []

#     for row in results:

#         data.append({
#             "culture": str(row.culture).split("/")[-1],
#             "season": str(row.season).split("/")[-1]
#         })
#     print("Données retournés : ",data)
#     return data