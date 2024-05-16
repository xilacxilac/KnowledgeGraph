# ADD COMMANDS TO LIST COMPANIES, RISK FACTORS, ETC SO THEY CAN QUERY??

from KnowledgeGraph import KnowledgeGraph

g = KnowledgeGraph()
quick_built_open = True

command: str = input()
while command != "exit":
    args: list[str] = command.split()
    if args:
        if args[0] == "quick_build":
            if quick_built_open:
                if len(args) == 1:
                    print(g.quick_build())
                    quick_built_open = False
                else:
                    print("Missing or too many arguments")
        elif args[0] == "add_company":
            if len(args) == 2:
                print(g.add_company(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_risk_factors":
            if len(args) == 2:
                print(g.add_risk_factors(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_by_sector":
            if len(args) == 2:
                print(g.query_by_sector(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_by_industries":
            if len(args) == 2:
                print(g.query_by_industries(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_by_ticker":
            if len(args) == 2:
                print(g.query_by_ticker(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_risk_factors":
            if len(args) == 2:
                print(g.query_risk_factors(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences":
            if len(args) == 2:
                print(g.query_SEC_sentences(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences_by_year":
            if len(args) == 3:
                print(g.query_SEC_sentences_by_year(args[1], args[2]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences_by_sector":
            if len(args) == 2:
                g.query_SEC_sentences_by_sector(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences_by_sector_year":
            if len(args) == 3:
                print(g.query_SEC_sentences_by_sector_year(args[1], args[2]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences_by_industry":
            if len(args) == 2:
                print(g.query_SEC_sentences_by_industry(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_SEC_sentences_by_industry_year":
            if len(args) == 3:
                print(g.query_SEC_sentences_by_industry_year(args[1], args[2]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "query_by_risk_factor":
            if len(args) == 2:
                print(g.query_by_risk_factor(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "list_sectors":
            if len(args) == 1:
                print(g.list_sectors())
            else:
                print("Missing or too many arguments")
        elif args[0] == "list_industries":
            if len(args) == 1:
                print(g.list_industries())
            else:
                print("Missing or too many arguments")
        elif args[0] == "list_companies":
            if len(args) == 1:
                print(g.list_companies())
            else:
                print("Missing or too many arguments")
        elif args[0] == "list_risk_factors":
            if len(args) == 1:
                print(g.list_risk_factors())
            else:
                print("Missing or too many arguments")
        elif args[0] == "export_visualization":
            if len(args) == 1:
                print(g.export_visualization())
            else:
                print("Missing or too many arguments")
        elif args[0] == "export_graph":
            if len(args) == 1:
                print(g.export_graph())
            elif len(args) == 2:
                print(g.export_graph(output=str(args[1])))
            elif len(args) == 3:
                print(g.export_graph(output=str(args[1]), format_=str(args[2])))
            else:
                print("Too many arguments")

    command = input()
