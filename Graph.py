from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx

from Node import Node


class Graph:
    def __init__(self) -> None:
        # Ensures unique node names since nodes should not have the same name (not talking about attributes)
        self.names = set()

        # Mostly used for queries
        self.companies = dict()
        self.risk_factors = dict()
        self.general_events = dict()
        self.events = dict()
        self.articles = dict()

    @staticmethod
    def add_new_relationship(node1: 'Node', node2: 'Node', relation1: str, relation2: str) -> None:
        node1.add_relation(relation1, node2)
        node2.add_relation(relation2, node1)

    def add_company(self, company: str, ticker: str) -> str:
        if company in self.companies:
            return "Company is already in the Graph"
        elif company in self.names:
            return "Node name already exists"
        else:
            new_company = Node(company)
            company_ticker = Node(ticker)

            self.add_new_relationship(new_company, company_ticker, "tickerSymbol", "tickerOfCompany")
            self.names.add(company)
            self.companies[company] = new_company

            return "Success"

    def add_risk_factor(self, risk_factor: str) -> str:
        if risk_factor in self.risk_factors:
            return "Risk Factor is already in the Graph"
        elif risk_factor in self.names:
            return "Node name already exists"
        else:
            new_risk_factor = Node(risk_factor)

            self.names.add(risk_factor)
            self.risk_factors[risk_factor] = new_risk_factor

            return "Success"

    def add_general_event(self, general_event: str) -> str:
        if general_event in self.general_events:
            return "General Event is already in the Graph"
        elif general_event in self.names:
            return "Node name already exists"
        else:
            new_general_event = Node(general_event)

            self.names.add(general_event)
            self.general_events[general_event] = new_general_event

            return "Success"

    def add_event(self, event: str) -> str:
        if event in self.events:
            return "Event is already in the Graph"
        elif event in self.names:
            return "Node name already exists"
        else:
            new_event = Node(event)

            self.names.add(event)
            self.events[event] = new_event

            return "Success"

    def add_article(self, article: str) -> str:
        if article in self.articles:
            return "Article is already in the Graph"
        elif article in self.names:
            return "Node name already exists"
        else:
            new_article = Node(article)

            self.names.add(article)
            self.events[article] = new_article

            return "Success"

    def build_graph(self, csv_path):
        # VERY UNFINISHED
        cache: list[tuple[str, str, str]] = []
        with open(csv_path) as csv_file:
            for line in csv_file:
                line_arr = line.split(",")
                if len(line_arr) == 3:
                    name1, relation, name2 = line_arr[0], line_arr[1], line_arr[2]
                    if name1 in self.names and name2 in self.names:
                        node1 = self.find_node_by_name(name1)
                        node2 = self.find_node_by_name(name2)
                        if node1 and node2:
                            self.add_new_relationship(node1, node2, )

        # when instanceOf --> redirect to types defined
        pass

    def query(self):
        pass

    def find_node_by_name(self, name) -> Optional['Node']:
        if name not in self.names:
            return None
        elif name in self.companies:
            return self.companies[name]
        elif name in self.risk_factors:
            return self.risk_factors[name]
        elif name in self.general_events:
            return self.general_events[name]
        elif name in self.events:
            return self.events[name]
        elif name in self.articles:
            return self.articles[name]
        else:
            return None

    def visualize_graph(self, scale: int) -> None:
        G = nx.Graph()

        for company in self.companies.values():
            G.add_node(company.value)
        for risk_factor in self.risk_factors.values():
            G.add_node(risk_factor.value)
        for general_event in self.general_events.values():
            G.add_node(general_event.value)
        for event in self.events.values():
            G.add_node(event.value)
        for article in self.articles.values():
            G.add_node(article.value)

        for company in self.companies.values():
            for neighbor in company.neighbor:
                G.add_edge(company.value, neighbor.value)
        for risk_factor in self.risk_factors.values():
            for neighbor in risk_factor.neighbor:
                G.add_edge(risk_factor.value, neighbor.value)
        for general_event in self.general_events.values():
            for neighbor in general_event.neighbor:
                G.add_edge(general_event.value, neighbor.value)
        for event in self.events.values():
            for neighbor in event.neighbor:
                G.add_edge(event.value, neighbor.value)
        for article in self.articles.values():
            for neighbor in article.neighbor:
                G.add_edge(article.value, neighbor.value)

        pos = nx.spring_layout(G, scale=scale)
        nx.draw(G, pos, with_labels=True, font_weight='bold')
        plt.show()
