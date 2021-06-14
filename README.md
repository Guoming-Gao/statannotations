![coverage](https://raw.githubusercontent.com/trevismd/statannotations/master/coverage.svg)

## What is it

Python package to optionally compute statistical test and add statistical
annotations on an existing boxplot/barplot generated by seaborn.

## Derived work

This repository is evolving independently from
[webermarcolivier/statannot](https://github.com/webermarcolivier/statannot)
by Marc Weber. It is based on commit 1835078 of Feb 21, 2020, tagged "v0.2.3".

Additions/modifications since that fork are below represented **in bold** 
(previous fixes are not listed). *New issues and PRs are welcome and will be 
looked into.*

The statannot interface, at least until its version 0.2.3, is directly usable in
statannotations, which provides additional features.

## Features

- Single function to add statistical annotations on an existing boxplot/barplot
  generated by seaborn boxplot.
- Integrated statistical tests (binding to `scipy.stats` methods):
    - Mann-Whitney
    - t-test (independent and paired)
    - Welch's t-test
    - Levene test
    - Wilcoxon test
    - Kruskal-Wallis test
- **Interface to use any other function from any source with minimal extra code**
- Smart layout of multiple annotations with correct y offsets.
- Annotations can be located inside or outside the plot.
- **Corrections for multiple testing can be applied
  (binding to `statsmodels.stats.multitest.multipletests` methods):**
    - Bonferroni
    - Holm-Bonferroni
    - Benjamini-Hochberg
    - Benjamini-Yekutieli
- **And any other function from any source with minimal extra code**
- Format of the statistical test annotation can be customized:
      star annotation, simplified p-value, or explicit p-value.
- Optionally, custom p-values can be given as input.
      In this case, no statistical test is performed, but **corrections for
      multiple testing can be applied.**
- And various fixes (see [CHANGELOG.md](https://raw.githubusercontent.com/trevismd/statannotations/master/CHANGELOG.md)).
## Installation

From version 0.3.0 on, the package is distributed on PyPi.  
The latest stable release can be downloaded and installed with:
```bash
pip install statannotations
```

or, after cloning the repository,
```bash
pip install -r requirements.txt .
```

## Documentation

See example jupyter notebook [doc/example.ipynb](`https://raw.githubusercontent.com/trevismd/statannotations/master/doc/example.ipynb).

## Usage

Here is a minimal example:

```python
import seaborn as sns
from statannotations import add_stat_annotation

df = sns.load_dataset("tips")
x = "day"
y = "total_bill"
order = ['Sun', 'Thur', 'Fri', 'Sat']
ax = sns.boxplot(data=df, x=x, y=y, order=order)
add_stat_annotation(
    ax, data=df, x=x, y=y, order=order,
    box_pairs=[("Thur", "Fri"), ("Thur", "Sat"), ("Fri", "Sun")],
    test='Mann-Whitney', text_format='star', loc='outside', verbose=2)

```

## Examples

![Example 1](https://raw.githubusercontent.com/trevismd/statannotations/master/doc/example_non-hue_outside.png)

![Example 2](https://raw.githubusercontent.com/trevismd/statannotations/master/doc/example_hue_layout.png)

## Requirements

+ Python >= 3.6
+ numpy >= 1.12.1
+ seaborn >= 0.9
+ matplotlib >= 2.2.2
+ pandas >= 0.23.0
+ scipy >= 1.1.0
+ statsmodels (optional, for multiple testing corrections)
