from silx.resources import ExternalResources

resources = ExternalResources(
    project="daxs",
    url_base="https://spectroscopy.gitlab-pages.esrf.fr/daxs-data",
    env_key="DAXS_DATA",
    timeout=60,
)
