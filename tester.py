import KnowledgeGraph as KG

g = KG.KnowledgeGraph()
g.add_company("NVDA")
g.add_company("AMD")
g.add_company("MSFT")
g.add_company("AMZN")
g.add_company("AAPL")
g.export_graph()