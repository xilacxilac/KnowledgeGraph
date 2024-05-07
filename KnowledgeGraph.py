from typing import Optional

import pycountry

from AttributeBuilder import yf_company_attr, yf_company_twoway_attr, build_company, build_risk_factor, build_general_event, build_event
from rdflib import Graph, Literal, RDF, URIRef, RDFS
from rdflib.tools.rdf2dot import rdf2dot
from io import StringIO

rdf_types = {"streetAddress", "city", "state", "country", "company", "sector", "industry"}
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

    def add_edge(self, node1: URIRef, node2: URIRef, relation1: str, relation2: str = "") -> None:
        namespace1 = self.uri + f"{relation1}"
        predicate1 = URIRef(namespace1)
        namespace2 = self.uri + f"{relation2}"
        predicate2 = URIRef(namespace2)

        self.rdf.add((node1, predicate1, node2))

        if relation2:
            self.rdf.add((node2, predicate2, node1))

    def add_attribute_literal(self, node1: URIRef, attribute: str, relation1: str) -> None:
        namespace1 = self.uri + f"{relation1}"
        predicate1 = URIRef(namespace1)
        self.rdf.add((node1, predicate1, Literal(attribute)))

    def add_attribute_resource(self, node1: URIRef, attribute: str, relation1: str, relation2: str = "", namespace: str = "") -> None:
        if attribute not in self.rdf_nodes:
            if namespace:
                self.rdf_nodes[attribute] = URIRef(namespace + attribute)
            else:
                self.rdf_nodes[attribute] = URIRef(self.uri + attribute)

        namespace1 = self.uri + f"{relation1}"
        predicate1 = URIRef(namespace1)
        self.rdf.add((node1, predicate1, self.rdf_nodes[attribute]))

        if relation2:
            namespace2 = self.uri + f"{relation2}"
            predicate2 = URIRef(namespace2)
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
        attr_list, company, location = build_company(ticker)
        address, city, state, country = self.format_location(location)

        # See if company already exists
        if not attr_list or not company:
            return "Error in returns from add_company()"
        else:
            company_no_space = company.replace(" ", "%20")
            rdf_namespace = self.uri + "company/" + company_no_space
            rdf_company = URIRef(rdf_namespace)

            if rdf_namespace not in self.rdf_nodes:
                self.rdf_nodes[rdf_namespace] = rdf_company
                self.rdf.add((rdf_company, RDF.type, self.rdf_nodes["company"]))

                for (relation1, attribute) in attr_list:
                    if relation1 in yf_company_twoway_attr:
                        attr_name = relation1.replace("Key", "") if "Key" in relation1 else relation1
                        relation2 = f"companyIn{attr_name.title()}"

                        if attribute not in self.rdf_nodes:
                            attr_namespace = self.uri + f"{attr_name}/"
                            self.rdf_nodes[attribute] = URIRef(attr_namespace + attribute)
                            self.rdf.add((self.rdf_nodes[attribute], RDF.type, self.rdf_nodes[attr_name]))

                        self.add_edge(rdf_company, self.rdf_nodes[attribute], attr_name, relation2)
                    else:
                        self.add_attribute_literal(rdf_company, attribute, relation1)

                if city and state and country:
                    full_address = "/".join([country, state, city, address])
                    city_address = "/".join([country, state, city])
                    state_address = "/".join([country, state])
                    self.add_location(address, city, state, country)
                    self.add_attribute_resource(rdf_company, full_address, "headquarteredIn", "companiesHeadquartedIn")
                    self.add_attribute_resource(rdf_company, city_address, "headquarteredIn", "companiesHeadquartedIn")
                    self.add_attribute_resource(rdf_company, state_address, "headquarteredIn", "companiesHeadquartedIn")
                    self.add_attribute_resource(rdf_company, country, "headquarteredIn", "companiesHeadquartedIn")

                return "Success"

            else:
                return "Company has already been added"

    def add_risk_factor(self, risk_factor: str) -> str:
        pass

    def add_general_event(self, general_event: str) -> str:
        pass

    def add_event(self, event: str) -> str:
        pass

    def add_article(self, article: str) -> str:
        pass

    def build_graph(self, json_path):
        pass

    def query(self):
        pass

    def export_visualization(self) -> None:
        dot_stream = StringIO()
        rdf2dot(self.rdf, dot_stream)
        dot_data = dot_stream.getvalue()

        # Save DOT data to a file
        with open("graph.dot", "w") as dot_file:
            dot_file.write(dot_data)

    def export_graph(self, output: str = "output.json", format_: str = "json-ld") -> None:
        try:
            serialized_data = self.rdf.serialize(format=format_)

            with open(output, 'w') as json_file:
                json_file.write(serialized_data)
        except Exception as e:
            print(e)
