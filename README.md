# ACOW
####Metric Temporal Logic Model Checking Tool written in Python 3.X
---
This is the project for AERE/COMS 407X/507X Applied Formal Methods. You need Conda and Graphviz installed first.

####Steps:
1) Create python Environment:
```bash
conda env create -f environment.yml
```
2) Activate the Environment:
```bash
source activate MTL
```
3) Modefiy the state space model and MTL formula in MTL_main.py. Then run:
```bash
python MTL_main.py
```