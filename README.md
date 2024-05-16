## Knowledge Graph

### KnowledgeGraph.py
#### Description:
- Provides a simple framework to build, populate, and query our RDF Graph

#### Attributes
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

- self.rdf: An RDF Graph which contains a set of RDF triples
- self.uri: The Uniform Resource Identifier, an example is set in this case
- self.rdf_nodes: Stores frequently used RDF nodes, ensures uniqueness and re-usability
- self.predicates: Stores frequently used RDF predicates, ensures uniqueness and re-usability
- self.SEC_sentence_count: a unique counter for each company to ensure unique sentence names

#### Common Nodes and Predicates
- Node Types
  - streetAddress, city, state, country, company, sector, industry, riskFactor, year, month, day, SECSentence
- Predicates
  - RDF.type, hasState, belongsToCountry, hasCity, belongsToState, hasAddress, belongsToCity, isYear, isMonth, text, relatedToRiskFactor, belongsToCompany, hasRiskFactor, companiesWithRiskFactor, hasFilingYear, hasSECSentence
- Risk Factors
  - General, Weather, Political, Economy, Energy, Business

#### Schemas
- Company
  - Type: RDF.type
  - Ticker: symbol
  - Location of HQ: headquarteredIn
  - Long Business Summary: longBusinessSummary
  - Full-time Employees: fullTimeEmployees
  - Audit Risk (1-10, low-high): auditRisk
  - Board Risk (1-10, low-high): boardRisk
  - Compensation Risk (1-10, low-high): compensationRisk
  - Shareholder Rights Risk (1-10, low-high): shareHolderRightsRisk
  - Overall Risk (1-10, low-high): overallRisk
  - Industry: industryKey
  - Sector: sectorKey
  - SEC 10-K Filing Sentence [Optional]: hasSECSentence 
  - Risk Factors [Optional]: hasRiskFactor
- SECSentence
  - Type: RDF.type
  - SEC Sentence: text
  - Filing Year: hasFilingYear
  - Related Risk Factor: relatedToRiskFactor
  - Related Company: belongsToCompany
- Location - Address
  - Type: RDF.type
  - City: belongsToCity
  - State: belongsToState
  - Country: belongsToCountry
  - Companies at Address: companiesHeadquartedIn
- Location - City
  - Type: RDF.type
  - State: belongsToState
  - Country: belongsToCountry 
  - Companies in City: companiesHeadquartedIn
  - Address in City: hasAddress
- Location - State
  - Type: RDF.type
  - Country: belongsToCountry 
  - Companies in State: companiesHeadquartedIn
  - City in State: hasCity
- Location - Country
  - Type: RDF.type
  - Companies in Country: companiesHeadquartedIn
  - State in Country: hasState

#### Construction Functions
- format_location(location: tuple[str, str, str, str]) -> tuple[str, str, str, str]
  - Cleans and reformats a location to a format which rdflib can support
- add_edge(self, node1: URIRef, node2: URIRef, relation1: str, relation2: str = "") -> None:
  - Creates an edge between two URIRefs
- add_attribute_literal(self, node1: URIRef, attribute: str, relation1: str) -> None:
  - Creates an attribute edge for a URIRef
- add_attribute_resource(self, node1: URIRef, attribute: str, relation1: str, relation2: str = "", namespace: str = "") -> None:
  - Same as add_edge(), but you can pass in a custom namespace
- add_location(self, address: str, city: str, state: str, country: str):
  - Adds location nodes and edges
- add_date(self, year: str, month: str, day: str):
  - Adds date nodes and edges
- add_company(self, ticker: str) -> str:
  - Adds a company node with attributes with information from yfinance (attribute details in [Schemas](#Schemas))
- add_risk_factors(self, ticker: str) -> str:
  - Adds sentences in a company's SEC 10-K fillings that correspond with a risk factor
- quick_build(self) -> str:
  - Iterates through a preset list of tickers and builds the graph

#### Query Functions
- query_by_sector(self, sector):
  - Finds companies in a sector and returns a list of tuples with the company name and ticker
- query_by_industries(self, industry):
  - Finds companies in an industry and returns a list of tuples with the company name and ticker
- query_by_ticker(self, ticker):
  - Finds a company by ticker and returns all of its edges and corresponding nodes
- query_risk_factors(self, ticker):
  - Finds a company by ticker and returns their risk factors
- query_SEC_sentences(self, ticker):
  - Finds a company by ticker and returns all of their risk-related SEC 10-K filing sentences
- query_SEC_sentences_by_year(self, ticker, year):
  - Finds a company by ticker and returns all of their risk-related SEC 10-K filing sentences for a specific year
- query_SEC_sentences_by_sector(self, sector):
  - Finds companies by a sector and returns all of their risk-related SEC 10-K filing sentences
- query_SEC_sentences_by_sector_year(self, sector, year):
  - Finds companies by a sector and returns all of their risk-related SEC 10-K filing sentences for a specific year
- query_SEC_sentences_by_industry(self, industry):
  - Finds companies by an industry and returns all of their risk-related SEC 10-K filing sentences
- query_SEC_sentences_by_industry_year(self, industry, year):
  - Finds companies by an industry and returns all of their risk-related SEC 10-K filing sentences for a specific year
- query_by_risk_factor(self, risk_factor):
  - Returns all companies that have a specific risk factor

#### Query Assistance Functions
- list_sectors(self):
- list_industries(self):
- list_companies(self):
- list_risk_factors(self):

#### Export Functions
- export_visualization(self) -> str:
  - Exports a .dot visualization of the graph
- export_graph(self, output: str = "output.json", format_: str = "json-ld") -> str:
  - Exports the graph into specified formats

### CLI.py
#### Description
- Provides a command line interface for the Knowledge Graphs

        # Example Commands to Run
        quick_build
        add_company MSFT
        list_sectors
        list_industries
        list_companies
        list_risk_factors
        query_by_sector technology
        query_by_ticker IBM
        query_risk_factors AAPL
        query_by_risk_factor Energy
        query_SEC_sentences AIT
        query_SEC_sentences_by_year AIT 2010
        query_SEC_sentences_by_sector technology
        query_SEC_sentences_by_sector_year technology 2010
        export_graph


### AttributeBuilder.py
#### Description
- Provides functions that gets and loosely formats attribute information for the graph

#### Functions
- def build_company(ticker: str) -> tuple[list[tuple[str, str]], str, tuple[str, str, str, str]]:
  - Gets information about a company from yfinance, loosely reformats it, and returns it
- get_company_name(ticker: str) -> str:
  - Gets a company name from their ticker using yfinance
- build_risk_factor(ticker: str) -> dict[str, tuple[list[str], list[tuple[str, str]]]]:
  - Extracts SEC 10-K filing sentences and related risk factors for a company, reformats it, and returns it 
