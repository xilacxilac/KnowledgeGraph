import KnowledgeGraph as KG
import urllib.parse

g = KG.KnowledgeGraph()
g.add_risk_factors("AIT")
g.add_risk_factors("MSFT")
g.export_graph()
print(g.list_sectors())
print(g.query_by_sector("industrials"))
print(g.list_industry())
print(g.query_by_industry("industrial-distribution"))
#print("RDF data after adding companies:")
#print(g.rdf.serialize(format="turtle"))