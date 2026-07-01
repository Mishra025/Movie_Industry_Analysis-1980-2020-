# Movie Industry Intelligence App

An interactive Streamlit dashboard for exploring movie industry trends, financial performance, correlations, outliers, and business insights from a movie dataset covering 1980 to 2020.

This project converts notebook-based analysis into a clean app-like dashboard where users can filter data, view charts, compare genres, study profitability, and download reports.

## Project Highlights

- Interactive Streamlit dashboard
- Movie industry overview with KPI cards
- Sidebar filters for year, genre, rating, country, and IMDb score
- Exploratory Data Analysis with distributions and outlier detection
- Financial intelligence by genre and budget tier
- Pearson and Spearman correlation analysis
- Profit, ROI, budget, and gross revenue analysis
- Searchable movie data explorer
- Downloadable filtered CSV
- Downloadable Markdown report
- Clean app structure with reusable source files

## Dataset Overview

The dataset contains movie records with information about release year, genre, rating, IMDb score, votes, budget, gross revenue, director, writer, star, country, company, and runtime.

Original dataset:

```text
Rows: 7,668
Columns: 15
```

After cleaning:

```text
Clean rows: 7,661
Financial analysis rows: 5,435
Year range: 1980-2020
Genres: 19
Countries: 59
```

## Columns Used

```text
name
rating
genre
year
released
score
votes
director
writer
star
country
budget
gross
company
runtime
```

## Data Cleaning Process

The raw dataset was cleaned carefully so useful rows were not removed unnecessarily.

### 1. Removed rows with missing essential fields

Rows were removed only when important non-financial fields were missing.

```python
df = df.dropna(subset=["name", "genre", "year", "score", "runtime"])
```

Budget and gross revenue were not used for global row removal because some movies still had useful score, runtime, genre, and year information.

### 2. Removed duplicate rows

```python
df = df.drop_duplicates()
```

Duplicate rows can affect counts, averages, rankings, correlations, and trends.

### 3. Converted numeric columns

Important columns were converted into numeric format:

```python
for col in ["budget", "gross", "votes", "score", "runtime", "year"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
```

Numeric columns used in analysis:

```text
score
votes
budget
gross
runtime
year
```

### 4. Created financial features

New columns were created for financial analysis:

```python
df["budget_M"] = df["budget"] / 1_000_000
df["gross_M"] = df["gross"] / 1_000_000
df["profit"] = df["gross"] - df["budget"]
df["profit_M"] = df["profit"] / 1_000_000
df["roi"] = ((df["gross"] - df["budget"]) / df["budget"]) * 100
df["profitable"] = df["profit"] > 0
```

These features make it easier to compare movies using budget, gross revenue, profit, and return on investment.

### 5. Created budget tiers

Movies with valid budget and gross values were grouped into budget tiers:

```text
Low
Medium
High
Blockbuster
```

This helps compare small-budget films with large-budget films more fairly.

### 6. Cleaned release information

The release column was separated into release date and release country.

```python
df["released_date"] = pd.to_datetime(df["released_date_text"], errors="coerce")
```

This made it easier to analyze movies by time period and release geography.

### 7. Detected outliers

Outliers were detected using:

```text
IQR Method
Z-score Method
```

Outlier columns:

```text
budget_M
gross_M
score
```

This helped identify extreme blockbuster movies and unusual financial cases.

## Analysis Performed

## 1. Movie Industry Overview

The overview page gives a quick summary of the dataset:

- Total raw rows
- Clean rows
- Financial analysis rows
- Year range
- Number of genres
- Number of countries
- Yearly movie volume
- Average IMDb score trend
- Most common genres
- Top movies by gross, profit, ROI, and score

## 2. Exploratory Data Analysis

The EDA section studies the shape of the dataset using:

- Score distribution
- Budget distribution
- Gross revenue distribution
- Runtime distribution
- Outlier watchlist

Important observation:

```text
Budget, gross revenue, and votes are highly skewed.
```

This means most movies have moderate values, while a small number of blockbuster movies have extremely high values.

## 3. Financial Intelligence

The financial section focuses on:

- Genre ROI ranking
- Average budget by genre
- Average gross revenue by genre
- Average profit by genre
- Percentage of profitable movies
- Budget tier performance
- Profit vs IMDb score

Important business idea:

```text
High gross revenue does not always mean high ROI.
```

A movie can earn a lot of money but still have a lower ROI if its production budget was extremely high.

## 4. Correlation Analysis

Two correlation methods were used.

### Pearson Correlation

Pearson correlation checks linear relationships between numeric variables.

Useful for:

```text
budget vs gross
score vs votes
runtime vs score
```

### Spearman Correlation

Spearman correlation checks ranked relationships and is more reliable for skewed data.

Since movie budgets, gross revenue, and votes contain extreme outliers, Spearman is very useful for this dataset.

## Key Findings

## 1. Budget is strongly connected with gross revenue

Movies with higher budgets usually earn more at the box office.

Possible reasons:

- Bigger marketing campaigns
- Wider theatrical release
- Better production scale
- Larger star cast
- Stronger distribution network

Connection:

```text
Higher budget -> More visibility -> Larger audience reach -> Higher gross revenue
```

## 2. Votes are strongly connected with popularity and revenue

Movies with more votes often have higher gross revenue.

This shows that vote count is a strong signal of audience reach.

Connection:

```text
More viewers -> More votes -> More popularity -> Higher gross revenue
```

## 3. IMDb score is important but not the strongest revenue driver

A high IMDb score does not always guarantee high revenue.

A movie can have a strong rating but still earn less because of:

- Limited release
- Small production budget
- Less marketing
- Niche audience
- Non-mainstream genre

Connection:

```text
High score -> Better audience satisfaction
```

But:

```text
High score does not always mean high box office revenue
```

## 4. Genre affects profitability

Some genres can produce better ROI because they do not always require huge budgets.

For example, genres like horror can become highly profitable when production cost is low and audience interest is strong.

Connection:

```text
Genre -> Budget requirement -> Audience size -> Profitability -> ROI
```

## 5. Blockbusters create outliers

Some movies earn extremely high revenue compared with the rest of the dataset.

These movies affect averages and make the distribution right-skewed.

That is why median values and outlier detection are important.

Connection:

```text
Few blockbuster movies -> Very high gross values -> Skewed averages
```

## 6. Runtime is not a major success factor

Runtime does not strongly decide whether a movie becomes successful.

Movie success depends more on:

- Story
- Genre
- Budget
- Marketing
- Audience reach
- Star power
- Release timing

## Interesting Trends

### Movie production increased over time

The number of movies increased from earlier decades to later decades.

Possible reasons:

- Growth of the global film industry
- Expansion of production companies
- Easier digital production
- More international releases
- Higher demand for entertainment content

### Revenue became more blockbuster-driven

The dataset shows that a small number of films earn very large amounts compared with most movies.

This creates a long-tail pattern:

```text
Many movies earn moderate revenue
Few movies earn extremely high revenue
```

### Budget tiers show different performance patterns

Low-budget movies can sometimes produce strong ROI, while blockbuster movies usually generate higher gross revenue.

This means:

```text
Blockbusters often win in total revenue
Smaller films can win in efficiency
```

## How the Factors Are Interconnected

Movie success is not controlled by only one variable. The analysis shows that many features are connected.

```text
Budget -> Production quality + Marketing -> Audience reach -> Gross revenue
```

```text
Votes -> Popularity -> Audience reach -> Gross revenue
```

```text
Genre -> Budget level -> Audience type -> ROI
```

```text
Score -> Audience satisfaction -> Long-term reputation
```

```text
Gross revenue - Budget = Profit
```

```text
Profit / Budget = ROI
```

The most important idea is that revenue, profitability, popularity, and quality are related but not identical.

## App Pages

## How to Use This App

After starting the app with Streamlit, open the local browser link shown in the terminal.

```bash
streamlit run app.py
```

Usually the app opens at:

```text
http://localhost:8501
```

### 1. Use Sidebar Filters

The left sidebar contains filters that control the whole dashboard.

You can filter movies by:

- Release year
- Genre
- Rating
- Country
- Minimum IMDb score

Example:

```text
Select years 2000-2020
Choose genre Action or Drama
Set minimum IMDb score to 7.0
```

After changing filters, all charts, tables, KPIs, and reports update automatically.

### 2. Start with the Overview Page

Use the Overview page to understand the dataset quickly.

This page helps answer:

- How many movies are available after filtering?
- What is the year range?
- Which genres appear most often?
- How did movie volume change over time?
- Which movies are top ranked by gross, profit, ROI, or score?

### 3. Explore Distributions in EDA

Use the Exploratory Analysis page to study numeric patterns.

You can inspect:

- IMDb score distribution
- Budget distribution
- Gross revenue distribution
- Runtime distribution
- Outlier movies

This page is useful for finding unusual movies, blockbuster outliers, and skewed financial patterns.

### 4. Analyze Profitability

Use the Financial Intelligence page to study business performance.

This page helps compare:

- Genre ROI
- Average budget by genre
- Average gross revenue by genre
- Budget tier performance
- Profit vs IMDb score

Use this page to understand which genres and budget levels are more financially efficient.

### 5. Study Relationships with Correlations

Use the Correlations page to compare numeric variables.

The app includes:

- Pearson correlation
- Spearman correlation
- Ranked correlation pairs

Pearson is useful for linear relationships, while Spearman is better when values are skewed or affected by blockbuster outliers.

### 6. Search and Export Data

Use the Data Explorer page to search and download data.

You can search by:

- Movie name
- Director
- Star
- Company

You can also select which columns to display.

Available downloads:

- Filtered CSV file
- Markdown report

This makes the app useful for both visual analysis and reporting.

### 7. Suggested Analysis Flow

For the best experience, use the app in this order:

```text
Overview -> Exploratory Analysis -> Financial Intelligence -> Correlations -> Data Explorer
```

This flow starts with general trends, then moves into deeper financial and statistical insights.

## Overview

Shows high-level movie industry metrics and trends.

Includes:

- KPI cards
- Yearly trend chart
- Genre count chart
- Top movie rankings

## Exploratory Analysis

Shows the distribution of key numeric variables.

Includes:

- IMDb score distribution
- Budget distribution
- Gross revenue distribution
- Runtime distribution
- Outlier table

## Financial Intelligence

Shows how movies perform financially.

Includes:

- Genre ROI ranking
- Budget vs gross by genre
- Budget tier performance
- Profit vs IMDb score

## Correlations

Shows relationships between numeric variables.

Includes:

- Pearson correlation heatmap
- Spearman correlation heatmap
- Ranked correlation pairs

## Data Explorer

Allows users to search, filter, and export data.

Includes:

- Search by movie, director, star, or company
- Select visible columns
- Download filtered CSV
- Download Markdown report

## Tech Stack

```text
Python
Pandas
NumPy
Streamlit
Plotly
```

## Project Structure

```text
movies_streamlit_app/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── movies.csv
│
└── src/
    ├── data_pipeline.py
    ├── charts.py
    └── __init__.py
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

Open in browser:

```text
http://localhost:8501
```

## Conclusion

This project shows how raw movie industry data can be transformed into an interactive intelligence dashboard.

The analysis found that movie success is connected with budget, popularity, genre, IMDb score, votes, gross revenue, profit, and ROI.

The strongest business insight is that high revenue is often connected with budget and popularity, while high profitability depends more on efficiency, genre, and return on investment.

This dashboard makes the movie industry easier to understand through visual analysis instead of static tables only.
