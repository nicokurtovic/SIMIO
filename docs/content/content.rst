From sky to images.
===============================

How are ALMA images generated?
------------------------------

Let us assume there is an interesting object in the sky, and we wish to study its spatial brightness distribution. For simplicity, let us assume we are observing a portion of the sky small enough such that the sky can be described as a flat surface (this is the case for most ALMA observations of planet-forming disks). In such scenario, our object of study will have a certain intensity distribution over the 2D surface defined as :math:`I(l,m)`, where "math"`(l,m)` are the sky spatial coordinates. From an observational point of view, our goal is to recover the function :math:`I` as accurately as possible.

As ALMA is an interferometer, it does not directly observes the sky brightness distribution :math:`I` (as most optical and near infrared cameras), but it rather observes the visibility function :math:`V` of the sky brightness, which is calculated as the Fourier Transform of the brightness distribution:

    .. math::
        \mathscr{V}(u, v) = \int \int \mathscr{I}(l,m) \, e^{-2\pi i (ul + vm)}\,\text{d}l\,\text{d}m

