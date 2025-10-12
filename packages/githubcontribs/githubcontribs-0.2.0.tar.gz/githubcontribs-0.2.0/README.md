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

Plotting:

```python
plotter = githubcontribs.Plotter(df)
plotter.plot_total_number_by_author_by_type()
plotter.plot_number_by_month_by_author()
```

Contributing: Please run `pre-commit install` and `gitmoji -i` on the CLI before starting to work on this repository!
