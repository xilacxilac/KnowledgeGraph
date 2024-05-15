## Knowledge Graph

### Graph.py
#### Notes:
- Attributes are mostly used for fast access for queries
#### Attributes
- self.companies: A dictionary of a company name to their node
- self.risk_factors: A dictionary of risk factors to their node
- self.general_events: A dictionary of general events to their node
- self.events: A dictionary of an event to their node
- self.articles: A dictionary of articles to their node
#### Schemas
- Company
  - Ticker Symbol: tickerSymbol <--> tickerOfCompany
- Risk Factor
- General Events
- Events
- Articles 
#### Other Edges
- Company to Risk Factor: companyRiskFactor <--> ???need a name???
- Risk Factor to General Events: generalEventExample <--> relatedRiskFactor
- General Events to Events: specificEventExample <--> relatedGeneralEvent
- Events to Articles: specificArticleExample <--> relatedEvent
#### Functions
- add_new_relationship(node1: 'Node', node2: 'Node', relation1: str, relation2: str):
  - Creates a new relationship between two nodes
- add_X(self, ...):
  - Adds a new node with information about it (addition details in [Schemas](#Schemas))
- build_graph(self, path):
  - Builds the graph

      def query(self):
          pass

      def find_node_by_name(self, name) -> Optional['Node']:
- visualize_graph(self, scale: int)
  - Creates a simple visual of the graph without edge names

### CLI.py
#### Description
- Provides a command line interface for the Knowledge Graphs
- Allows adding additional nodes and edges to the Knowledge Graph
- You can also upload a .csv to build the graph