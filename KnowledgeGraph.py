from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
import pycountry

from AttributeBuilder import yf_company_attr, build_company, build_risk_factor, build_general_event, build_event
from rdflib import Graph, Literal, RDF, URIRef, RDFS
from Node import Node

rdf_types = {"streetAddress", "city", "state", "country", "company"}
predicates = {"hasState", "belongsToCountry", "hasCity", "belongsToState", "hasAddress", "belongsToCity"}

# 5MODA8JgyXRwgmI2iWVWKY
class KnowledgeGraph:
    def __init__(self) -> None:
        # Stores the graph as an RDF
        self.rdf = Graph()
        self.uri = "http://example.org/"

        # Stores nodes
        self.rdf_nodes: dict[str, URIRef] = dict()

        for attribute in yf_company_attr:
            self.rdf_nodes[attribute] = URIRef(self.uri + attribute)

        for types in rdf_types:
            self.rdf_nodes[types] = URIRef(self.uri + types)

        # Stores predicates (edges)
        self.predicates: dict[str, URIRef] = dict()

        for predicate in predicates:
            self.predicates[predicate] = URIRef(self.uri + predicate)

        # Stores instances of nodes
        self.instance_of: dict[str, Node] = dict()

        # Stores frequently queried nodes, should have unique names
        self.companies: dict[str, tuple[Node, URIRef]] = dict()
        self.risk_factors: dict[str, Node] = dict()
        self.general_events: dict[str, Node] = dict()
        self.events: dict[str, Node] = dict()
        #self.articles: dict[str, Node] = dict() -- probably not all unique
        self.locations: dict[str, Node] = dict()
        self.timedates: None = None

    @staticmethod
    def format_location(location: tuple[str, str, str, str]) -> tuple[str, str, str, str]:
        address, city, state, country = location
        try:
            country = pycountry.countries.get(name=country)
            if country:
                country = country.alpha_2
            else:
                return "", "", "", ""
        except LookupError:
            print("LookupError")
            return "", "", "", ""

        return address.replace(" ", "%20"), city.replace(" ", "%20"), state.replace(" ", "%20"), country

    @staticmethod
    def add_new_relationship(node1: 'Node', node2: 'Node', relation1: str, relation2: str) -> None:
        node1.add_relation(relation1, node2)
        node2.add_relation(relation2, node1)

    @staticmethod
    def add_attribute(node1: 'Node', attribute: str, relation1: str, relation2: Optional[str]) -> None:
        attribute_node = Node(attribute)
        node1.add_relation(relation1, attribute_node)

        if relation2:
            attribute_node.add_relation(relation2, node1)

    def add_rdf_attribute(self, node1: URIRef, attribute: str, relation1: str, relation2: Optional[str]) -> None:
        if not relation2:
            new_namespace1 = self.uri + f"{relation1}"
            predicate1 = URIRef(new_namespace1)
            self.rdf.add((node1, predicate1, Literal(attribute)))

        else:
            if attribute not in self.rdf_nodes:
                self.rdf_nodes[attribute] = URIRef(attribute)

            new_namespace1 = self.uri + f"{relation1}"
            predicate1 = URIRef(new_namespace1)
            self.rdf.add((node1, predicate1, self.rdf_nodes[attribute]))

            new_namespace2 = self.uri + f"{relation2}"
            predicate2 = URIRef(new_namespace2)
            self.rdf.add((self.rdf_nodes[attribute], predicate2, node1))

    def add_location(self, address: str, city: str, state: str, country: str):
        if country:
            country_uri = self.uri + f"location/{country}"
            if country not in self.rdf_nodes:
                self.rdf_nodes[country] = URIRef(country_uri)
                self.rdf.add((self.rdf_nodes[country], RDF.type, self.rdf_nodes["country"]))

            if state:
                state_loc = f"{country}/{state}"
                state_uri = country_uri + f"/{state}"
                if state_loc not in self.rdf_nodes:
                    self.rdf_nodes[state_loc] = URIRef(state_uri)
                    self.rdf.add((self.rdf_nodes[state_loc], RDF.type, self.rdf_nodes["state"]))
                    self.rdf.add((self.rdf_nodes[country], self.predicates["hasState"], self.rdf_nodes[state_loc]))
                    self.rdf.add((self.rdf_nodes[state_loc], self.predicates["belongsToCountry"], self.rdf_nodes[country]))

                if city:
                    city_loc = f"{state_loc}/{city}"
                    city_uri = state_uri + f"/{city}"
                    if city_loc not in self.rdf_nodes:
                        self.rdf_nodes[city_loc] = URIRef(city_uri)
                        self.rdf.add((self.rdf_nodes[city_loc], RDF.type, self.rdf_nodes["city"]))
                        self.rdf.add((self.rdf_nodes[state_loc], self.predicates["hasCity"], self.rdf_nodes[city_loc]))
                        self.rdf.add((self.rdf_nodes[city_loc], self.predicates["belongsToState"], self.rdf_nodes[state_loc]))
                        self.rdf.add((self.rdf_nodes[city_loc], self.predicates["belongsToCountry"], self.rdf_nodes[country]))

                    if address:
                        address_loc = f"{city_loc}/{address}"
                        address_uri = city_uri + f"/{address}"
                        if address_loc not in self.rdf_nodes:
                            self.rdf_nodes[address_loc] = URIRef(address_uri)
                            self.rdf.add((self.rdf_nodes[address_loc], RDF.type, self.rdf_nodes["streetAddress"]))
                            self.rdf.add((self.rdf_nodes[city_loc], self.predicates["hasAddress"], self.rdf_nodes[address_loc]))
                            self.rdf.add((self.rdf_nodes[address_loc], self.predicates["belongsToCity"], self.rdf_nodes[city_loc]))
                            self.rdf.add((self.rdf_nodes[address_loc], self.predicates["belongsToState"], self.rdf_nodes[state_loc]))
                            self.rdf.add((self.rdf_nodes[address_loc], self.predicates["belongsToCountry"], self.rdf_nodes[country]))

    def add_company(self, ticker: str) -> str:
        # Adds instance of company Node if it does not exist
        if "Company" not in self.instance_of:
            self.instance_of["Company"] = Node("Company")

        attr_list, company, location = build_company(ticker)
        address, city, state, country = self.format_location(location)
        #address, city, state, country = ("1874 Virginia Avenue", "McLean", "VA", "22101", "USA")

        print(attr_list, company, location)
        # See if company already exists
        if not attr_list or not company:
            return "Error in returns from build_company()"
        elif ticker in self.companies:
            return "Company is already in the Graph"
        else:
            new_company = Node(company)
            company_no_space = company.replace(" ", "%20")
            rdf_namespace = self.uri + "company/" + company_no_space
            rdf_company = URIRef(rdf_namespace)

            self.rdf.add((rdf_company, RDF.type, self.rdf_nodes["company"]))

            for (relation1, relation2, attribute) in attr_list:
                self.add_attribute(new_company, attribute, relation1, relation2)
                self.add_rdf_attribute(rdf_company, attribute, relation1, relation2)

            self.add_new_relationship(self.instance_of["Company"], new_company, "categoryOf", "instanceOf")
            self.companies[ticker] = (new_company, rdf_company)
            if city and state and country:
                full_address = "/".join([country, state, city, address])
                city_address = "/".join([country, state, city])
                state_address = "/".join([country, state])
                self.add_location(address, city, state, country)
                self.add_rdf_attribute(rdf_company, full_address, "headquarteredIn", "companiesHeadquartedIn")
                self.add_rdf_attribute(rdf_company, city_address, "belongsToCity", "")
                self.add_rdf_attribute(rdf_company, state_address, "belongsToState", "")
                self.add_rdf_attribute(rdf_company, country, "belongsToCountry", "")

            return "Success"

    def add_risk_factor(self, risk_factor: str) -> str:
        # Adds instance of risk factor Node if it does not exist
        if "Risk Factor" not in self.instance_of:
            self.instance_of["Risk Factor"] = Node("Risk Factor")

        # See if risk factor already exists
        if risk_factor in self.risk_factors:
            return "Risk Factor is already in the Graph"
        else:
            new_risk_factor = Node(risk_factor)

            for (attribute, relation1, relation2) in build_risk_factor(risk_factor):
                self.add_attribute(new_risk_factor, attribute, relation1, relation2)

            self.add_new_relationship(self.instance_of["Risk Factor"], new_risk_factor, "categoryOf", "instanceOf")
            self.risk_factors[risk_factor] = new_risk_factor

            return "Success"

    def add_general_event(self, general_event: str) -> str:
        # Adds instance of general event Node if it does not exist
        if "General Event" not in self.instance_of:
            self.instance_of["General Event"] = Node("General Event")

        # See if general event already exists
        if general_event in self.general_events:
            return "General Event is already in the Graph"
        else:
            new_general_event = Node(general_event)

            for (attribute, relation1, relation2) in build_general_event(general_event):
                self.add_attribute(new_general_event, attribute, relation1, relation2)

            self.add_new_relationship(self.instance_of["General Event"], new_general_event, "categoryOf", "instanceOf")
            self.general_events[general_event] = new_general_event

            return "Success"

    def add_event(self, event: str) -> str:
        # Adds instance of event Node if it does not exist
        if "Event" not in self.instance_of:
            self.instance_of["Event"] = Node("Event")

        # See if general event already exists
        if event in self.events:
            return "Event is already in the Graph"
        else:
            new_event = Node(event)

            for (attribute, relation1, relation2) in build_event(event):
                self.add_attribute(new_event, attribute, relation1, relation2)

            self.add_new_relationship(self.instance_of["Event"], new_event, "categoryOf", "instanceOf")
            self.events[event] = new_event

            return "Success"

    def add_article(self, article: str) -> str:
        pass

        if article in self.articles:
            return "Article is already in the Graph"
        else:
            new_article = Node(article)

            self.events[article] = new_article

            return "Success"

    def build_graph(self, json_path):
        pass

        # VERY UNFINISHED
        cache: list[tuple[str, str, str]] = []
        with open(json_path) as json_file:
            for line in json_file:
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

    def visualize_graph(self, scale: int) -> None:
        G = nx.Graph()
        id_to_name = dict()

        for company in self.companies.values():
            G.add_node(company.node_id)
            id_to_name[company.node_id] = company.value
        for risk_factor in self.risk_factors.values():
            G.add_node(risk_factor.value)
        for general_event in self.general_events.values():
            G.add_node(general_event.value)
        for event in self.events.values():
            G.add_node(event.value)
        #for article in self.articles.values():
        #    G.add_node(article.value)

        for company in self.companies.values():
            for neighbor in company.neighbor:
                G.add_edge(company.node_id, neighbor.node_id)
                id_to_name[neighbor.node_id] = neighbor.value
        for risk_factor in self.risk_factors.values():
            for neighbor in risk_factor.neighbor:
                G.add_edge(risk_factor.value, neighbor.value)
        for general_event in self.general_events.values():
            for neighbor in general_event.neighbor:
                G.add_edge(general_event.value, neighbor.value)
        for event in self.events.values():
            for neighbor in event.neighbor:
                G.add_edge(event.value, neighbor.value)
        #for article in self.articles.values():
        #    for neighbor in article.neighbor:
        #        G.add_edge(article.value, neighbor.value)

        #pos = nx.spring_layout(G, scale=scale)
        #nx.draw(G, pos, with_labels=True, font_weight='bold')
        #plt.show()

        nx.draw(G, with_labels=True, labels=id_to_name, node_size=1000, node_color='skyblue', font_size=12)
        plt.show()

    def export_graph(self, output: str = "output.json", format_: str = "json-ld") -> None:
        try:
            serialized_data = self.rdf.serialize(format=format_)

            with open(output, 'w') as json_file:
                json_file.write(serialized_data)
        except Exception as e:
            print(e)
