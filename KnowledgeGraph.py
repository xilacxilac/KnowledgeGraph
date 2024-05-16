import urllib.parse
import pycountry

from AttributeBuilder import yf_company_twoway_attr, build_company, build_risk_factor, get_company_name
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.tools.rdf2dot import rdf2dot
from io import StringIO

quick_build_tickers = {'KINS', 'ACU', 'B', 'TCI', 'UHAL', 'CVCO', 'COKE', 'BA', 'HAS', 'CVR', 'NEE', 'CACI', 'FHN',
                       'CVX', 'HRB', 'AVY', 'FMC', 'COO', 'USB', 'CULP', 'EAT', 'AIG', 'CATO', 'IDCC', 'AFL', 'FELE',
                       'GLW', 'AME', 'JPM', 'BC', 'ADI', 'AVT', 'CMTL', 'TRMK', 'AIRT', 'FLS', 'AAPL', 'AIT', 'SWKS',
                       'HE', 'GHM', 'CCK', 'GATX', 'BOOM', 'BSET', 'PCG', 'ARCB', 'M', 'VZ', 'GPC', 'TGT', 'ATRO',
                       'BPOP', 'ALCO', 'BRC', 'NEU', 'ATO', 'EQT', 'D', 'BAX', 'JOB', 'BK', 'ETR', 'GGG', 'ABM', 'AAL',
                       'AEP', 'DTE', 'BOH', 'IFF', 'CHDN', 'CBT', 'CAG', 'CWT', 'DG', 'DHR', 'DLX', 'GIS', 'NBR', 'CMA',
                       'DAN', 'IP', 'FRD', 'IBM', 'AVD', 'EFX', 'FCNCA', 'ARL', 'CPB', 'IPG', 'CW', 'CNA', 'ALOT',
                       'INTC', 'GTN', 'FDX', 'CMI', 'HXL', 'ADSK', 'DE', 'REX', 'BIO', 'HUBB', 'CMCSA', 'EBF', 'MATX',
                       'AMSWA', 'HSY', 'XOM', 'GRC', 'BEN', 'FITB', 'RYN', 'ITW', 'STRL', 'ECL', 'CSX', 'FSS', 'TGNA',
                       'WEN', 'BRID', 'CAMP', 'CSL', 'MTZ', 'DWSN', 'MTB', 'ADP', 'RYI', 'AE', 'ED', 'BDX', 'CHE',
                       'CNP', 'AZZ', 'AIR', 'HPQ', 'APOG', 'MARA', 'GD', 'AXR', 'HRL', 'ATRI', 'DBD', 'EMR', 'IIIN',
                       'HON', 'CPK', 'F', 'CBRL', 'ESCA', 'HP', 'TAP', 'GNTX', 'ENZN', 'BMI', 'ALK', 'GPS', 'KODK',
                       'GM', 'BKH', 'BDL', 'DDS', 'AON', 'HNI', 'FSTR', 'GWW', 'FUL', 'TILE', 'SPXC', 'HD', 'EGP',
                       'PXD', 'AMAT', 'BELFB', 'FRT', 'HVT', 'ALLY', 'BBY', 'CAL', 'CMS', 'HBAN', 'GIGA', 'PNW', 'JBHT',
                       'CMC', 'GLT', 'EDUC', 'CL', 'AJG', 'RF', 'CFR', 'MTRN', 'GFF', 'KO', 'HOV', 'FLXS', 'RAVE',
                       'COHU', 'EML', 'DOV', 'IDA', 'CDE', 'RHI', 'WELL', 'OSG', 'HWKN', 'HEI', 'DAL', 'DUK', 'FLR',
                       'STZ', 'CTAS', 'DY', 'BMY', 'CRS', 'BRN', 'BCPC', 'ABT', 'DAIO', 'FLO', 'ENZ', 'CTO'}
rdf_types = {"streetAddress", "city", "state", "country", "company", "sector", "industry", "riskFactor", "year", "month",
             "day", "SECSentence"}
predicates = {"hasState", "belongsToCountry", "hasCity", "belongsToState", "hasAddress", "belongsToCity", "isYear",
              "isMonth", "text", "relatedToRiskFactor", "belongsToCompany", "hasRiskFactor", "companiesWithRiskFactor",
              "hasFilingYear", "hasSECSentence"}
risk_factors = {"General", "Weather", "Political", "Economy", "Energy", "Business"}


class KnowledgeGraph:
    def __init__(self) -> None:
        # Stores the graph as an RDF
        self.rdf = Graph()
        self.uri = "http://example.org/"

        # Stores nodes
        self.rdf_nodes: dict[str, URIRef] = dict()

        for types in rdf_types:
            self.rdf_nodes[types] = URIRef(self.uri + types)
        for risk_factor in risk_factors:
            self.rdf_nodes[f"riskFactor/{risk_factor}"] = URIRef(self.uri + f"riskFactor/{risk_factor}")
            self.rdf.add((self.rdf_nodes[f"riskFactor/{risk_factor}"], RDF.type, self.rdf_nodes["riskFactor"]))

        # Stores predicates (edges)
        self.predicates: dict[str, URIRef] = dict()

        for predicate in predicates:
            self.predicates[predicate] = URIRef(self.uri + predicate)

        # Counter Variables
        self.SEC_sentence_count = dict()

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

    def add_date(self, year: str, month: str, day: str):
        if year:
            year_uri = self.uri + f"date/{year}"
            if year not in self.rdf_nodes:
                self.rdf_nodes[year] = URIRef(year_uri)
                self.rdf.add((self.rdf_nodes[year], RDF.type, self.rdf_nodes["year"]))

            if month:
                month_loc = f"{year}/{month}"
                month_uri = year_uri + f"/{month}"
                if month_loc not in self.rdf_nodes:
                    self.rdf_nodes[month_loc] = URIRef(month_uri)
                    self.rdf.add((self.rdf_nodes[month_loc], RDF.type, self.rdf_nodes["month"]))
                    self.rdf.add((self.rdf_nodes[month_loc], self.predicates["isYear"], self.rdf_nodes[year]))

                if day:
                    day_loc = f"{month_loc}/{day}"
                    day_uri = month_uri + f"/{day}"
                    if day_loc not in self.rdf_nodes:
                        self.rdf_nodes[day_loc] = URIRef(day_uri)
                        self.rdf.add((self.rdf_nodes[day_loc], RDF.type, self.rdf_nodes["day"]))
                        self.rdf.add((self.rdf_nodes[day_loc], self.predicates["isYear"], self.rdf_nodes[year]))
                        self.rdf.add((self.rdf_nodes[day_loc], self.predicates["isMonth"], self.rdf_nodes[month_loc]))

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
            self.SEC_sentence_count[ticker] = 0

            if rdf_namespace not in self.rdf_nodes:
                self.rdf_nodes[rdf_namespace] = rdf_company
                self.rdf.add((rdf_company, RDF.type, self.rdf_nodes["company"]))

                for (relation1, attribute) in attr_list:
                    if relation1 in yf_company_twoway_attr:
                        attr_name = relation1.replace("Key", "") if "Key" in relation1 else relation1
                        relation2 = f"companyIn{attr_name.title()}"

                        if attribute not in self.rdf_nodes:
                            attr_namespace = self.uri + f"{attr_name}/"
                            self.rdf_nodes[f"companyAttribute/{attribute}"] = URIRef(attr_namespace + attribute)
                            self.rdf.add((self.rdf_nodes[f"companyAttribute/{attribute}"], RDF.type, self.rdf_nodes[attr_name]))

                        self.add_edge(rdf_company, self.rdf_nodes[f"companyAttribute/{attribute}"], attr_name, relation2)
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

    def add_risk_factors(self, ticker: str) -> str:
        add_company_response = self.add_company(ticker)
        company_name = get_company_name(ticker)

        if add_company_response != "Success":
            return add_company_response
        elif not company_name:
            return "Company not found"
        else:
            company_no_space = company_name.replace(" ", "%20")

            year_to_events = build_risk_factor(ticker)
            company_risk_factors = set()
            company_node = self.rdf_nodes[f"{self.uri}company/{company_no_space}"]

            for year in year_to_events:
                dates, arr = year_to_events[year]
                self.add_date(dates[0], "", "") # dates[1], dates[2] will not be included for simplicity
                for sentence_in_SEC_filing, risk_factor in arr:
                    if risk_factor in risk_factors:
                        if risk_factor not in company_risk_factors:
                            company_risk_factors.add(risk_factor)

                        sentence_node = URIRef(self.uri + f"company/{company_no_space}/SEC/sentence/sentence{self.SEC_sentence_count[ticker]}")
                        self.rdf.add((sentence_node, RDF.type, self.rdf_nodes["SECSentence"]))
                        self.rdf.add((sentence_node, self.predicates["text"], Literal(sentence_in_SEC_filing)))
                        self.rdf.add((sentence_node, self.predicates["relatedToRiskFactor"], self.rdf_nodes[f"riskFactor/{risk_factor}"]))
                        self.rdf.add((sentence_node, self.predicates["belongsToCompany"], company_node))
                        self.rdf.add((sentence_node, self.predicates["hasFilingYear"], self.rdf_nodes[dates[0]]))
                        self.rdf.add((company_node, self.predicates["hasSECSentence"], sentence_node))

                        self.SEC_sentence_count[ticker] += 1

            for risk_factor in company_risk_factors:
                self.rdf.add((self.rdf_nodes[f"riskFactor/{risk_factor}"], self.predicates["companiesWithRiskFactor"], company_node))
                self.rdf.add((company_node, self.predicates["hasRiskFactor"], self.rdf_nodes[f"riskFactor/{risk_factor}"]))

            return "Success"

    def quick_build(self) -> str:
        failures = 0
        for ticker in quick_build_tickers:
            response = self.add_risk_factors(ticker)
            if response != "Success":
                failures += 1
                print(response)

        return f"Completed with {failures} failures"

    @staticmethod
    def reformat_single_query(results):
        results_list = list()
        for result in results:
            uri = result[0]
            name = urllib.parse.unquote(uri.split('/')[-1])
            results_list.append(name)

        return results_list

    @staticmethod
    def reformat_double_query(results):
        results_list = list()
        for result in results:
            predicate_uri = result[0]
            predicate = urllib.parse.unquote(predicate_uri.split('/')[-1])
            if predicate == "22-rdf-syntax-ns#type":
                predicate = "type"

            object_uri = result[1]
            object_ = urllib.parse.unquote(object_uri.split('/')[-1])
            results_list.append((predicate, object_))

        return results_list

    def list_sectors(self):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT DISTINCT ?sector
            WHERE {{
                ?company ns1:sector ?sector .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_by_sector(self, sector):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?company ?symbol
            WHERE {{
                ?company rdf:type ns1:company .
                ?company ns1:symbol ?symbol .
                ?company ns1:sector <{self.uri}sector/{sector}> .
            }}
        """

        return self.reformat_double_query(self.rdf.query(query))

    def list_industries(self):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT DISTINCT ?industry
            WHERE {{
                ?company ns1:industry ?industry .
            }}
        
        """
        return self.reformat_single_query(self.rdf.query(query))

    def query_by_industries(self, industry):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?company ?symbol 
            WHERE {{
                ?company rdf:type ns1:company .
                ?company ns1:symbol ?symbol .
                ?company ns1:industry <{self.uri}industry/{industry}> .
            }}
        """

        return self.reformat_double_query(self.rdf.query(query))

    def list_companies(self):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT DISTINCT ?company ?symbol
            WHERE {{
                ?company ns1:symbol ?symbol .
            }}
        """

        return self.reformat_double_query(self.rdf.query(query))

    def query_by_ticker(self, ticker):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?predicate ?object
            WHERE {{
                ?company rdf:type ns1:company .
                ?company ns1:symbol "{ticker}" .
                ?company ?predicate ?object .
            }}
        """

        return self.reformat_double_query(self.rdf.query(query))

    def query_risk_factors(self, ticker):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?riskFactor
            WHERE {{
                ?company ns1:symbol "{ticker}" .
                ?company ns1:hasRiskFactor ?riskFactor .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences(self, ticker):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:symbol "{ticker}" .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences_by_year(self, ticker, year):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:symbol "{ticker}" .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:hasFilingYear <{self.uri}date/{year}> .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences_by_sector(self, sector):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:sector <{self.uri}sector/{sector}> .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences_by_sector_year(self, sector, year):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:sector <{self.uri}sector/{sector}> .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:hasFilingYear <{self.uri}date/{year}> .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences_by_industry(self, industry):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:industry <{self.uri}industry/{industry}> .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def query_SEC_sentences_by_industry_year(self, industry, year):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?text
            WHERE {{
                ?company ns1:industry <{self.uri}industry/{industry}> .
                ?company ns1:hasSECSentence ?SECSentence .
                ?SECSentence ns1:hasFilingYear <{self.uri}date/{year}> .
                ?SECSentence ns1:text ?text .
            }}
        """

        return self.reformat_single_query(self.rdf.query(query))

    def list_risk_factors(self):
        return list(risk_factors)

    def query_by_risk_factor(self, risk_factor):
        query = f"""
            PREFIX ns1: <{self.uri}>
            SELECT ?company ?symbol
            WHERE {{
                ?company rdf:type ns1:company .
                ?company ns1:hasRiskFactor <{self.uri}riskFactor/{risk_factor}> .
                ?company ns1:symbol ?symbol
            }}
        """

        return self.reformat_double_query(self.rdf.query(query))

    def export_visualization(self) -> str:
        try:
            dot_stream = StringIO()
            rdf2dot(self.rdf, dot_stream)
            dot_data = dot_stream.getvalue()

            with open("graph.dot", "w") as dot_file:
                dot_file.write(dot_data)

            return "Success"
        except Exception as e:
            return str(e)

    def export_graph(self, output: str = "output.json", format_: str = "json-ld") -> str:
        try:
            serialized_data = self.rdf.serialize(format=format_)

            with open(output, 'w') as json_file:
                json_file.write(serialized_data)

            return "Success"
        except Exception as e:
            return str(e)
