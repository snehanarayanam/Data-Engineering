# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/144gFNjXul1P7GS9DrcB94mlLKyLcnmPJ
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import time

url = "http://www.hubertiming.com/results/2017GPTR10K"
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')
type(soup)

# Get the title
title = soup.title
print(title)

# Print out the text
text = soup.get_text()
#print(soup.text)
soup.find_all('a')

all_links = soup.find_all("a")
for link in all_links:
    print(link.get("href"))

# Print the first 10 rows for sanity check
rows = soup.find_all('tr')
print(rows[:10])

"""convert such table data to a Python Pandas dataframe for easier transformation and analysis
 You should get all of the table’s rows in list form first and then convert that list into a pandas dataframe."""

for row in rows:
  row_td = row.find_all('td')
print(row_td)
type(row_td)

#To remove html tags using Beautiful Soup, pass the string of interest into BeautifulSoup() and use the get_text() method to extract the text without html tags.

str_cells = str(row_td)
cleantext = BeautifulSoup(str_cells, "lxml").get_text()
print(cleantext)

list_rows = []
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '',str_cells))
    list_rows.append(clean2)
print(clean2)
type(clean2)

df = pd.DataFrame(list_rows)
df.head(10)

#Data Transformation
df1 = df[0].str.split(',', expand=True)
df1.head(10)
df1[0] = df1[0].str.strip('[')
df1.head(10)

#The table is missing table headers. So go back to BeautifulSoup and use its find_all() method to get the table headers.

col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)
print(all_header)

#Next convert the table headers to a new pandas dataframe.

df2 = pd.DataFrame(all_header)
df2.head()

#Again, split column "0" into multiple columns at the comma position for all rows.

df3 = df2[0].str.split(',', expand=True)
df3.head()

#Next, concatenate the two dataframes into one using the concat() method.

frames = [df3, df1]

df4 = pd.concat(frames)
df4.head(10)

#Next, re-configure the data frame so that the first row is the table header.

df5 = df4.rename(columns=df4.iloc[0])
df5.head()

#Behold all of the progress that you have made! At this point, the table is almost properly formatted. For analysis, start by getting an overview of the data as shown below.

df5.info()
df5.shape

# transform it again to drop all rows with any missing values.
df6 = df5.dropna(axis=0, how='any')
df6.info()
df6.shape

#Notice how the table header is replicated as the first row in df5 and df6. Drop this redundant row like this:

df7 = df6.drop(df6.index[0])
df7.head()

#Clean up the headers a bit more by renaming the '[Place' and ' Team]' columns. Python is picky about whitespace. Make sure you include a space after the quotation mark in ' Team]'.

df7.rename(columns={'[Place': 'Place'},inplace=True)
df7.rename(columns={' Team]': 'Team'},inplace=True)
df7.head()

#The final data cleaning step involves removing the closing bracket for cells in the "Team" column.
df7['Team'] = df7['Team'].str.strip(']')
df7.head()

#Data Analysis and Visualization
#1.what was the average finish time (in minutes) for the runners?

time_list = df7[' Time'].tolist()

# You can use a for loop to convert 'Chip Time' to minutes

time_mins = []
for i in time_list:
    parts = i.split(':')
    seconds = 0
    if len(parts) == 3:  # H:M:S format
        h, m, s = parts
        seconds = int(h) * 3600 + int(m) * 60 + int(s)
    elif len(parts) == 2:  # M:S format
        m, s = parts
        seconds = int(m) * 60 + int(s)
    else:
        print(f"Unexpected time format: {i}")
        continue

    time_in_mins = seconds / 60
    time_mins.append(time_in_mins)

print(time_mins)

#Next, convert the list back into a dataframe and create a new column ("Runner_mins") for runner chip times expressed in just minutes.

df7['Runner_mins'] = time_mins
df7.head()

#Pandas provides a handy “describe” method that computes a generous list of explanatory statistics for the dataframe.


df7.describe(include=[np.number])

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5


df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])

#2.Did the runners' finish times follow a normal distribution?


x = df7['Runner_mins']
ax = sns.distplot(x, hist=True, kde=True, rug=False, color='m', bins=25, hist_kws={'edgecolor':'black'})
plt.show()

#3.Were there any performance differences between males and females of various age groups?
f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']
sns.distplot(f_fuko, hist=True, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Female')
sns.distplot(m_fuko, hist=False, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Male')
plt.legend()

#descriptive statistics to the visual plot, then use the pandas groupby() method to compute summary statistics for males and females separately.

g_stats = df7.groupby(" Gender", as_index=True).describe()
print(g_stats)

#display a side-by-side boxplot comparison of male and female finish times.
df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel(' Time')
plt.suptitle("")