from rdflib import Graph

g = Graph()
g.parse("api/ontology/Hasimboly_Ontologie_expert.ttl", format="turtle")

def get_culture_caracteristics(culture_name):
    culture_caracteristics_query = f"""
    PREFIX : <http://www.semanticweb.org/tsanta/ontologies/2026/4/untitled-ontology-12/>

    SELECT ?predicate ?object
    WHERE {{
        :{culture_name} ?predicate ?object .
    }}
    """

    results = g.query(culture_caracteristics_query)

    data = []

    for row in results:
        data.append({
            "predicate": str(row.predicate).split("/")[-1],
            "object": str(row.object).split("/")[-1]
        })

    return data