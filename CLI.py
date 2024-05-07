# ADD COMMANDS TO LIST COMPANIES, RISK FACTORS, ETC SO THEY CAN QUERY??

from KnowledgeGraph import KnowledgeGraph

g = KnowledgeGraph()

command: str = input()
while command != "exit":
    args: list[str] = command.split()
    if args:
        if args[0] == "build_graph":
            if len(args) == 2:
                g.build_graph(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_company":
            if len(args) == 2:
                g.add_company(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_risk_factor":
            if len(args) == 2:
                g.add_risk_factor(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_general_event":
            if len(args) == 2:
                g.add_general_event(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_event":
            if len(args) == 2:
                g.add_event(args[1])
            else:
                print("Missing or too many arguments")
        elif args[0] == "add_article":
            if len(args) == 2:
                g.add_article(args[1])
            else:
                print("Missing or too many arguments")
        #elif args[0] == "add_edge":
        #    if len(args) == 5:
        #        node1 = g.find_node_by_name(args[1])
        #        node2 = g.find_node_by_name(args[2])
        #        if node1 and node2:
        #            g.add_new_relationship(node1, node2, args[3], args[4])
        #        else:
        #            print("Nodes not found")
        #    else:
        #        print("Missing or too many arguments")
        elif args[0] == "query":
            # NOT IMPLEMENTED
            print("NOT IMPLEMENTED")
            if len(args) == 1:
                g.query()
            else:
                print("Missing or too many arguments")
        elif args[0] == "visualize_graph":
            if len(args) == 2:
                g.visualize_graph(int(args[1]))
            else:
                print("Missing or too many arguments")
        elif args[0] == "export_graph":
            if len(args) == 1:
                g.export_graph()
            elif len(args) == 2:
                g.export_graph(output=str(args[1]))
            elif len(args) == 3:
                g.export_graph(output=str(args[1]), format=str(args[2]))
            else:
                print("Too many arguments")
    command = input()
