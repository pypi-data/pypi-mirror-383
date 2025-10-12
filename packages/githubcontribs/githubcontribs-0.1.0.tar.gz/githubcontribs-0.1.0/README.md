# githubcontribs: Simple analytics for GitHub contributions across an organization

Install:

```bash
pip install githubcontribs
```

Quickstart:

```python
import githubcontribs
fetcher = githubcontribs.Fetcher("laminlabs")
df = fetcher.run("lamindb")
df.head()
#> Dataframe of contributions
```

Contributing: Please run `pre-commit install` and `gitmoji -i` on the CLI before starting to work on this repository!
