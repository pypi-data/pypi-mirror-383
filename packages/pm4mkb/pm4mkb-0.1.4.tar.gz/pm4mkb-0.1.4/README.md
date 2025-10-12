![](https://github.com/pm291097/pm4mkb/blob/main/imgs/Logo.png?raw=true)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pm4mkb)](https://pypi.org/project/pm4mkb)
[![PyPI - Version](https://img.shields.io/pypi/v/pm4mkb)](https://pypi.org/project/pm4mkb)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pm4mkb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
### [Documentation](https://process-mining-mkb.readthedocs.io/en/latest/)  |  [Installation](#installation) | [Quick start](#quick-start)
# MKBProcessMining (PM4MKB) – Process Mining Python framework
PM4MKB is an open-source Python library for conducting a comprehensive analysis of business processes with the use of process mining and machine learning techniques. By implementing this tool, objective and deep insights into the process on all levels can be revealed. These insights are then used to detect problems such as bottlenecks and deviations and identify potential opportunities for process improvement and optimization.

Authors: Process Mining for MKB Team.

# Installation

To install PM4MKB framework on your machine from PyPI:
```bash
pip install pm4mkb
```
To install from sources:
```bash
git clone https://github.com/pm291097/pm4mkb.git

cd MKB_Process_Mining
pip install .
```

Additionally, you have to install graphviz executables and add the path to the executables to PATH variable:  
https://graphviz.org/download/

# Quick start

There are some steps for quick start for your process log analysis:
* Create a DataHolder object:
```python
from pm4mkb import SuccessInputs, DurationUnits

path = "example_data.xlsx"
data_holder = DataHolder(
    data=path,
    col_case="id",
    col_stage="action",
    col_start_time="start_time",
    col_end_time="end_time",
    col_user="user_id",
    col_text="text",
    success_inputs=SuccessInputs(entries={"Подписание документов ", "Принято"}),
)

data_holder.data.head()
```
* Apply AutoInsights:
```python
from pm4mkb.autoinsights import AutoInsights

auto_insights = AutoInsights(data_holder, successful_stage="Принято")
auto_insights.apply()
```

# License
This project is released under the [MIT License](https://github.com/pm291097/pm4mkb/blob/main/LICENSE).