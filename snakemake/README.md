<p align="center">
  <img src="https://github.com/Nico-Curti/graphomics/blob/main/img/logo.png" width="90" height="90">
  <br>
  <b>
    pyGraphomics
  </b>
</p>

| **Authors**  | **Project** |  **Documentation** | **Build Status** | **Code Quality** | **Coverage** |
|:------------:|:-----------:|:------------------:|:----------------:|:----------------:|:------------:|
| [**N. Curti**](https://github.com/Nico-Curti) <br/> [**G. Carlini**](https://github.com/GianlucaCarlini) <br/> [**R.Biondi**](https://github.com/RiccardoBiondi) | **graphomics** | [![Doxygen Sphinx](https://github.com/Nico-Curti/graphomics/actions/workflows/docs.yml/badge.svg)](https://github.com/Nico-Curti/graphomics/actions/workflows/docs.yml) <br/> [![ReadTheDocs](https://readthedocs.org/projects/graphomics/badge/?version=latest)](https://graphomics.readthedocs.io/en/latest/?badge=latest) | [![Python](https://github.com/Nico-Curti/graphomics/actions/workflows/python.yml/badge.svg)](https://github.com/Nico-Curti/graphomics/actions/workflows/python.yml) | **TODO** | [![codecov](https://codecov.io/gh/Nico-Curti/graphomics/graph/badge.svg?token=YcCFfQqC3r)](https://codecov.io/gh/Nico-Curti/graphomics) |

**Appveyor:** [![appveyor](https://ci.appveyor.com/api/projects/status/djnkyxc64dlm4r6p/branch/main?svg=true)](https://ci.appveyor.com/project/Nico-Curti/graphomics-9jr6a/branch/main)

[![GitHub pull-requests](https://img.shields.io/github/issues-pr/Nico-Curti/graphomics.svg?style=plastic)](https://github.com/Nico-Curti/graphomics/pulls)
[![GitHub issues](https://img.shields.io/github/issues/Nico-Curti/graphomics.svg?style=plastic)](https://github.com/Nico-Curti/graphomics/issues)

[![GitHub stars](https://img.shields.io/github/stars/Nico-Curti/graphomics.svg?label=Stars&style=social)](https://github.com/Nico-Curti/graphomics/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/Nico-Curti/graphomics.svg?label=Watch&style=social)](https://github.com/Nico-Curti/graphomics/watchers)

<a href="https://github.com/UniboDIFABiophysics">
  <div class="image">
    <img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="90" height="90">
  </div>
</a>

## Graphomics Snakemake pipeline

In real case applications, we are commonly interested in extracting features from a wide range of medical images.
Further the one-shot command line interface *or* the fine grain customization of the pipeline using the `Python` codes, the `graphomics` package provides a ready-to-use multi-patients pipeline via `snakemake`.

The `snakemake` python package could be easily installed using the command

```bash
python -m pip install snakemake
```

`snakemake` is a standard tool in bio-informatics and bio-medical applications, which allow a fast scheduling of multi-processing *and* distributed pipelines combining `shell` and `Python` syntaxes.
In this folder we provide a minimal example of a basic `graphomic` pipeline which keeps a series of files in input and it provides as output the global database of features extracted.
This is just a simple example about how you can manage the `graphomics` package with multiple inputs.

In particular, in the [`template.yml`](https://github.com/Nico-Curti/graphomics/blob/main/snakemake/template.yml) we schedule a template example of a configuration file for a multi-patients application.
All the parameters set in the configuration file are documented in the file.
Further parameters could be added in it for the customization and expansion of this minimal working example.

The entire pipeline is stored in the [`Snakefile`](https://github.com/Nico-Curti/graphomics/blob/main/snakemake/Snakefile).
The propose workflow requires an input folder (aka `mask_dir`) in which all the `mask_filepath`s are stored.
The entire list of files, according to the desired file extensions, are processed as a series of independent processes, and therefore they are analyzed in parallel (or along multiple machines).
If the `skeleton` masks and/or the `label` maps are required, we assume a perfect match (in terms of filenames) between the mask files and these optional arguments.
For a finer grain customization you can edit the header of the `Snakefile` script.

The proposed workflow is simply made by 2 rules:

* `features_extraction`

  Run the graphomic features extraction on a single file extracted from the list of the available ones in the provided `mask_dir` directory.
  The output of this rule is a single `.json` file, one for each file found in the directory.

* `features_merge`

  Take the entire list of `.json` files resulting by the feature extraction task, and merge them into a unique tabular database in `.csv` format.
  The output path as much as the name of the resulting database can be customized editing the configuration file.

### How to run

The complete list of parameters and instructions for the customization of the `snakemake` file could be found in the official documentation of the package, provided [here](https://snakemake.readthedocs.io/en/stable/executing/cli.html).

For sake of clarity, we propose in the following a minimal list of command line examples:

| :triangular_flag_on_post: Note |
|:-------------------------------|
| Before the usage, the `snakemake` [configuration file](https://github.com/Nico-Curti/graphomics/blob/main/snakemake/template.yml) as much as the `graphomics` [configuration file](https://github.com/Nico-Curti/graphomics/blob/main/cfg/template.yml) **must** be edited according to your needs! |

* **Run the entire workflow**

```bash
snakemake --cores 1
```

* **Force the execution of a single rule**

```bash
# force the clear execution
snakemake --force clear
```

* **Check the workflow correctness**

```bash
snakemake --dryrun --forceall
```

* **Dump the workflow DAG**

```bash
snakemake --dag | dot -Tpdf > workflow.pdf
```

| :triangular_flag_on_post: Note |
|:-------------------------------|
| This command requires the pre-installation of the `dot` package, using the command `sudo apt install graphviz` |

## Authors

* <img src="https://avatars0.githubusercontent.com/u/24650975?s=400&v=4" width="25px"> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/Nico-Curti) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/nico.curti2) **Nico Curti**

* <img src="https://avatars.githubusercontent.com/u/48323996?v=4" width="25px"> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/GianlucaCarlini) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/gianluca.carlini3) **Gianluca Carlini**

* <img src="https://avatars.githubusercontent.com/u/48323959?v=4" width="25px;"/> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/RiccardoBiondi) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/riccardo.biondi7) **Riccardo Biondi**

See also the list of [contributors](https://github.com/Nico-Curti/graphomics/contributors) [![GitHub contributors](https://img.shields.io/github/contributors/Nico-Curti/graphomics.svg?style=plastic)](https://github.com/Nico-Curti/graphomics/graphs/contributors/) who participated in this project.

## License

The `graphomics` package is licensed under the BSD 3-Clause "New" or "Revised" [License](https://github.com/Nico-Curti/graphomics/blob/main/LICENSE).
