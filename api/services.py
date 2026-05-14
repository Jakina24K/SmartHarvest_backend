from rdflib import Graph

g = Graph()
g.parse("api/ontology/Hasimboly_Ontologie_expert.ttl", format="turtle")

prefix = "PREFIX : <http://www.semanticweb.org/tsanta/ontologies/2026/4/untitled-ontology-12/>"

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

    filters = []

    if region:
        filters.append(f"?culture :estLocaliseeDans :{region} .")

    if climate:
        filters.append(f"""
            ?region rdf:type :Region .
            ?region :aPourClimat :{climate} .
            ?culture :estLocaliseeDans ?region .
        """)

    if soil:
        filters.append(f"""
            ?region :aPourTypeDeSol :{soil} .
            ?culture :estLocaliseeDans ?region .
        """)

    filters_query = "\n".join(filters)

    query = f"""
    {prefix}

    SELECT DISTINCT ?culture ?season
    WHERE {{

        ?culture rdf:type :Culture .
        ?culture :estLocaliseeDans ?region .
        ?culture :seCultiveDurant ?season .

        {filters_query}
    }}
    """

    results = g.query(query)

    data = []

    for row in results:

        data.append({
            "culture": str(row.culture).split("/")[-1],
            "season": str(row.season).split("/")[-1]
        })
    print("Données retournés : ",data)
    return data