---
title: 'SIMIO-continuum: Connecting simulations to ALMA observations'
tags:
  - Python
  - CASA
  - astronomy
  - interferometry
  - synthetic observations
  - visibility modelling
authors:
  - name: Nicolas T. Kurtovic
    orcid: 0000-0002-2358-4796
    affiliation: "1" #
affiliations:
 - name: Max-Planck-Institut f\"{u}r Astronomie, K\"{o}nigstuhl 17, 69117, Heidelberg, Germany.
   index: 1
date: 15 August 2022
bibliography: paper.bib

---

# Summary

Interferometric observations sample the visibility space of the targeted source. Thus, procedures for image reconstruction are needed to obtain images from those observations. Several factors are involved in the detectability of physical features in a reconstructed image, such as the angular resolution of the observation, point spread function, noise level, and the assumptions of the reconstruction algorithm. The most robust way to test the observability of simulated emission features is by taking a simulated image and reconstructing it with the same algorithms. SIMIO-continuum takes simulated images of continuum emission in millimeter wavelengths and returns the synthetic observation and reconstructed images as if the input image had been observed in the sky with an existing interferometric observation.

The documentation and tutorials give a detailed description of the code functionalities and syntax, with publicly available datasets for reproducibility.

# Background

SIMIO-continuum is a python-based package for \texttt{CASA} [@McMullin:2007; @Emonts:2020], designed to take simulated images of millimeter continuum emission and return a synthetic interferometric observation and its reconstructed images. This functionality is particularly useful when comparing simulated models to archival observations. A common way to do this is by convolving the model image with a Gaussian representative of the angular resolution of the observation. Although this method is quick and easy to apply, it only considers a small step of the imaging reconstruction algorithms. Convolving with a gaussian does not take into account other factors that could impact the brightness distribution of a reconstructed image (see introduction section of @Czekala:2021 and references therein). On the other hand, the \texttt{CASA} task \texttt{simobserve} allows to create a new observational setup to include the simulated image (e.g., @Barraza:2021), but this requires a level of knowledge of interferometric observations. Additionally, it can become tedious if the goal is to reproduce an existing observational setup composed of several projects [e.g., @Huang:2018].

Instead of creating a new observational setup as \texttt{simobserve}, SIMIO-continuum uses an existing observation as a template for the synthetic observation. The package takes an input image (containing a millimeter continuum brightness distribution), calculates its visibilities, and then replaces this data in the template observation. This way, the synthetic observation mimics all the technical details of the template (such as the number of antennas, exposure time, frequency coverage, sky orientation, time of observation, and angular resolution). Once the synthetic observation is created, the synthetic reconstructed images are obtained the same way as real observations.

SIMIO-continuum was designed to be easy to use by non-observers while offering the full range of data products for people with different observational expertise. Based on a template observation, astronomers with little or no interferometric experience can obtain synthetic observations and images of their models. Additionally, SIMIO-continuum allows changing the model's geometry, including white noise in the reconstructed images, and changing the model distance to the observer, thus enabling multiple feature-recovery tests with a visibility-based approach.

# Acknowledgements

The author thanks the support of Paola Pinilla during the development of SIMIO-continuum. The author also acknowledges the support provided by the Alexander von Humboldt Foundation in the framework of the Sofja Kovalevskaja Award endowed by the Federal Ministry of Education and Research.

# References