## General knowledge
This data source contains sales information about wines from PoS system. When querying it, the agent should consider the following structure and semantics:

### Primary Fact Table: sales_fact
This is the main fact table containing individual sales data. Each row typically represents a single sale operation in PoS system.

### Lookup Dimenstion Table: date_dimension 
- Provides date, month, quarter, year information.

### Lookup Dimention Table: wine_dimension 
- Contains information about wines in our store.

### Lookup Dimention Table: review_dimension 
- Provide user's reviews of wines.
