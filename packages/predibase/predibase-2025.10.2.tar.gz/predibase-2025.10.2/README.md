## Predibase Python SDK

[Official Docs](https://docs.predibase.com/sdk-guide/intro)

### PQL Notebook Extensions

Install the notebook extension:

```
jupyter nbextension install --py predibase_notebook
jupyter nbextension enable predibase_notebook --py
```

At the top of your notebook:

```
%load_ext predibase_notebook
```

Set the data source:

```
from predibase import pql
```

Use the cell magics:

```
%%pql
PREDICT Survived GIVEN * FROM titanic limit 10
```
