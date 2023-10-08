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

## Graphomics examples

List of more or less complex examples for a custom usage of the `graphomics` package using `Python` scripts.

| :triangular_flag_on_post: Note |
|:-------------------------------|
| Since all the examples relies on the availability of the input images, they must be customized before their usage, setting a valid `mask_filepath`. Alternatively, you can use the samples provided on the online Google-Drive directory used for the code testing (ref. [here](https://github.com/Nico-Curti/graphomics/blob/main/test/download_from_drive.py)) |

Starting from a beginner usage to more advanced applications you can check the list of the deeply documented examples as follow:

* [`GraphomicsHelloWorld`](https://github.com/Nico-Curti/graphomics/blob/main/examples/GraphomicsHelloWorld):

  Definition of a basic `graphomic` pipeline with the visualization of the intermediate skeleton-graph extracted.
  Starting from the provided mask file as input, in this example you can see how to enable all the available graphomic features and visualize the skeleton-graph extracted on the volume as 3D plot.

* [`GraphomicsFeatureClass`](https://github.com/Nico-Curti/graphomics/blob/main/examples/GraphomicsFeatureClass):

  Example for a custom and fine grain usage of the graphomic classes of features.
  Without any input image, this example show you how you can manage the `GraphomicsFeatureExtractor` object according to your needs, checking also its behavior with a provided configuration file.

These are just 'HelloWorld' examples and further documentations and real-case applications could be found
in the [notebooks](https://github.com/Nico-Curti/graphomics/blob/main/docs/source/notebooks) folder.

## Authors

* <img src="https://avatars0.githubusercontent.com/u/24650975?s=400&v=4" width="25px"> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/Nico-Curti) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/nico.curti2) **Nico Curti**

* <img src="https://avatars.githubusercontent.com/u/48323996?v=4" width="25px"> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/GianlucaCarlini) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/gianluca.carlini3) **Gianluca Carlini**

* <img src="https://avatars.githubusercontent.com/u/48323959?v=4" width="25px;"/> [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="27px">](https://github.com/RiccardoBiondi) [<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="25px">](https://www.unibo.it/sitoweb/riccardo.biondi7) **Riccardo Biondi**

See also the list of [contributors](https://github.com/Nico-Curti/graphomics/contributors) [![GitHub contributors](https://img.shields.io/github/contributors/Nico-Curti/graphomics.svg?style=plastic)](https://github.com/Nico-Curti/graphomics/graphs/contributors/) who participated in this project.

## License

The `graphomics` package is licensed under the BSD 3-Clause "New" or "Revised" [License](https://github.com/Nico-Curti/graphomics/blob/main/LICENSE).
