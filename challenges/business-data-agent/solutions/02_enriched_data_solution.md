

```python
# chybějící část kódu pro load dat do DataFrame:
df_wines = spark.read.option("multiline", "true").json("Files/raw-data-wine/Wines/wines.json")
df_sales = spark.read.option("multiline", "true").json("Files/raw-data-wine/Sales/sales.json")
df_reviews = spark.read.option("multiline", "true").json("Files/raw-data-wine/Reviews/reviews.json")
```