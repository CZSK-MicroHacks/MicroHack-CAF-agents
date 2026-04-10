```
### Table Descriptions

**Table: date_dimension**

Important columns:
- Date - Primary key
- DateCode - Unique date in format YYYYMMDD
- MonthNumber - Month number
- MonthNameCzech - Czech name of month such as "Leden", "Duben", ...
- MonthNameEnglish - English name of month such as "January", "April", ...
- DayNumber - Number of day in month
- DayNameCzech - Czech name of day such as "Pondělí", "Středa", ...
- DayNameEnglish - English name of day such as "Monday", "Wednesday", ...
- Quarter - Quarter such as "Q1", "Q2", ...
- YearQuarter - Quarter including Year such as "2025-Q1", "2026-Q3", ...
- YearMonth - Month including Year sucha as "2025-01", "2025-12", "2026-04", ...
- Year - Year such as "2025", "2026"


**Table: review_dimension**

Important columns:
- ReviewId - Primary key
- Date - Date used to join to date_dimension.date
- WineCode - Wine code used
- Review - User's review of wine in Czech language
- Sentiment - User's sentiment of wine with values "Negative", "Neutral", "Positive"
- Score - Sentiment score with values between -1.0 to 1.0 (Positive > 0.1, Negative < -0.1, Neutral between 0.1 to -0.1)
- Wine2Meal - Recommended meal for wine based on user review in Czech
- User - User's email
- UserName - User's first name
- UserSurname - User's surname
- UserDomain - User's domain from email sucha as "seznam.cz", "outlook.cz", "gmail.com"


**Table: wine_dimension**

Important columns:
- WineId - WineId Primary key
- WineCode - Unique wine code
- WineName - Name of wine in Czech language
- Vintage - Vintage Year
- Type - Type of wine in Czech such as "Frankovka", "Merlot", "Pálava", ...
- Color - Color of wine in Czech, available only "Červené", "Bílé", "Růžové"
- Classification - Classification of wine in Czech such as "Pozdní sběr", "Jakostní víno", "Ledové víno", "Výběr z bobulí", ...
- Category - Category of wine in Czech, available only "Suché", "Polosuché", "Polosladké", "Sladké"
- Country - Country in Czech, available only "Česká republika", "Rakousko", "Maďarsko"
- Area - Wine area in Country
- Producer - Producer of wine

**Table: sales_fact**

Important columns:
- Date - Date of Sales
- PaymentMethod - Name of payment method, only available "Online", "Card", "Cash"
- Country - Country of store, only available "Česká republika"
- Store - Store in city in Country, city is in Czech such as "Jihlava", "Praha", "Brno", "Opava", ...
- WineId - Foreign key used to join to wine_dimension.WineId
- UnitPrice - List price of wine
- Quantity - Sale quantity
- Discount - Sale discount
- TotalAmount - Total amount after discount


### Guidance for Querying
- Always join sales_fact with wine_dimension using WineId to bring in descriptive attributes such as wine names, color, and classification.
- Use date_dimension to aggregate or filter data by time — for example, monthly sales trends, quarterly reviews, or year comparisons. Prefer readable formats like MonthNameCzech, Quarter, or Year when presenting summaries.
- When analyzing customer perceptions or feedback, join review_dimension with wine_dimension using WineCode to connect user sentiment, ratings, and meal recommendations with the corresponding wines. Use Sentiment and Score fields to explain customer perception.
- Combine review_dimension with date_dimension via the Date column to study sentiment or review volume over time.
- For sales performance analysis, focus on TotalAmount, Quantity, and Discount, optionally grouped by Store or PaymentMethod for operational insights.
- Expect the dataset to support scenarios like sales trend monitoring, customer sentiment analysis, wine-type performance evaluation, and regional sales optimization. Highlight how sales trends align or contrast with sentiment patterns to give richer business insights.
```