## What is a Lakehouse and a Medallion Architecture?

A **medallion architecture** is a data design pattern used to logically organize data in a [lakehouse](https://www.databricks.com/glossary/data-lakehouse), with the goal of incrementally and progressively improving the structure and quality of data as it flows through each layer of the architecture (from Bronze ⇒ Silver ⇒ Gold layer tables). Medallion architectures are sometimes also referred to as "multi-hop" architectures.

More information about Medallion Architecture you can find [here.](https://www.databricks.com/glossary/medallion-architecture)
## Bronze Layer (**Raw** Data Management)

This is the foundational layer where raw data is ingested directly from various source. The data is stored in its original, unmodified form.

## Silver Layer (**Enriched** / Refined Data Management)

In this intermediate layer, data is cleansed, standardized, and enriched to resolve inconsistencies and prepare for more detailed analysis. This includes resolving issues with data quality, standardizing formats, and enriching data with additional contextual information. The goal here is to create a reliable, query-optimized dataset that supports more efficient analysis and reporting.

## Gold Layer (**Curated** Data Management)

The highest level of the lakehouse, where data is further transformed, modeled, and summarized to support advanced analytics and business intelligence. This layer focuses on deriving actionable insights and supporting high-level decision-making. It could involve aggregating data into meaningful metrics, developing KPIs, or building machine learning models to predict future trends based on historical patterns.
