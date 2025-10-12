<div align="center">
<h1 align="center">
<img src="https://github.com/flechtenberg/flechtenberg_images/blob/main/Pulpo-Logo_INKSCAPE.png?raw=true" width="300" />
<h3>◦ Python-based User-defined Lifecycle Production Optimization!</h3>

<p align="center">
<img src="https://img.shields.io/badge/Jupyter-F37626.svg?style&logo=Jupyter&logoColor=white" alt="Jupyter" />
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Markdown-000000.svg?style&logo=Markdown&logoColor=white" alt="Markdown" />
</p>
<img src="https://img.shields.io/github/license/flechtenberg/pulpo?style=flat&color=5D6D7E" alt="GitHub license" />
<img src="https://img.shields.io/github/last-commit/flechtenberg/pulpo?style=flat&color=5D6D7E" alt="git-last-commit" />
<img src="https://img.shields.io/github/commit-activity/m/flechtenberg/pulpo?style=flat&color=5D6D7E" alt="GitHub commit activity" />
<img src="https://img.shields.io/github/languages/top/flechtenberg/pulpo?style=flat&color=5D6D7E" alt="GitHub top language" />
</div>

---

## 📍 Overview

Pulpo is a comprehensive Life Cycle Optimization (LCO) tool designed to streamline the optimization of environmental impacts across the entire lifecycle of products. It facilitates the import of data from the LCI databases accessed via brightway, converts inputs into optimization-ready formats, defines and solves optimization models using the Pyomo package, and saves and summarizes results. Pulpo empowers users to efficiently optimize and analyze environmental impacts, supporting sustainable decision-making through lifecycle-based strategies.

---

## 🚀 Getting Started

### 🔧 Installation
You can now install PULPO via pip:

```sh
pip install pulpo-dev
```

This will install PULPO and all its dependencies. It is advised to create a new venv/conda environment for 
performing tasks with PULPO, in order to avoid package conflicts with other tools such as brightway, activity-browser, 
or premise.

### 🤖 Running pulpo
After installing PULPO, check if the package has been set up properly by running the setup function:
```sh
from pulpo.utils import tests

tests.setup()
```
This function mimics the development test functions and if all tests have passed you are good to go.

To learn the PULPO workflow for more complex case studies, find example notebooks for a [hydrogen case](https://github.com/flechtenberg/pulpo/blob/master/notebooks/hydrogen_showcase.ipynb), an [electricity case](https://github.com/flechtenberg/pulpo/blob/master/notebooks/electricity_showcase.ipynb), and a [plastic case](https://github.com/flechtenberg/pulpo/blob/master/notebooks/plastic_showcase.ipynb) here.

You can also follow these notebooks locally with the shipped package by calling:
```sh
from pulpo import pulpo

pulpo.electricity_showcase()
pulpo.hydrogen_showcase()
pulpo.plastic_showcase()
```

It should be noted that to run these showcase it is necessary to install the ecoinvent cutoff38 system model via brightway2/activity-browser.
Please follow instructions on [Brightway2](https://learn.brightway.dev/en/latest/content/notebooks/BW2_for_beginners.html) or
[Activity-Browser](https://github.com/LCA-ActivityBrowser/activity-browser) to see how this is done.

---

## 📄 License

This project is licensed under the `ℹ️  BSD 3-Clause` License.
Copyright (c) 2023, Fabian Lechtenberg. All rights reserved.

---

## 👏 Acknowledgments

We would like to acknowledge the authors and contributors of these main packages that pulpo is based on:
 - [pyomo](https://github.com/Pyomo/pyomo)
 - [brightway2](https://github.com/brightway-lca/brightway2)
---
## Authors
- [@flechtenberg](https://www.github.com/flechtenberg)
- [@robyistrate](https://www.github.com/robyistrate)
- [@vtulus](https://www.github.com/vtulus)
---
[↑ Return](#Top)