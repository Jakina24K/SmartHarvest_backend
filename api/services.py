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

def get_culture_from_caracteristics(caracteristic):

    query = f"""
    {prefix}

    SELECT DISTINCT ?culture ?region
    WHERE {{
        ?region :aPourClimat :{caracteristic} .

        ?culture rdf:type :Culture .
        ?culture :estLocaliseeDans ?region .
    }}
    """

    results = g.query(query)

    data = []

    for row in results:
        data.append({
            "culture": str(row.culture).split("/")[-1],
            "region": str(row.region).split("/")[-1]
        })

    return data