from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import jax
import numpyro
from jax import numpy as jnp
from numpyro import distributions as dist

from jaxglm.links import Link, IdentityLink, LogitLink, LogLink


class Family(ABC):
    """Abstract base class for GLM family specifications."""

    def __init__(self, link: Optional[Link] = None):
        """Initialize family with optional link function.

        Args:
            link: Link function instance. If None, uses canonical link.
        """
        if link is None:
            link = self._default_link()
        self.link = link

    @abstractmethod
    def _default_link(self) -> Link:
        """Return the canonical link function for this family.

        Returns:
            Canonical link function instance
        """
        pass

    @abstractmethod
    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        """Sample from the likelihood distribution using NumPyro.

        Args:
            name: Name for the sample site
            mu: Mean parameter
            obs: Observed data (if None, generates prior/posterior predictive samples)

        Returns:
            Sampled values
        """
        pass

    @abstractmethod
    def sample_dispersion(self) -> Optional[jnp.ndarray]:
        """Sample dispersion/scale parameter if required by the family.

        Returns:
            Dispersion parameter or None if family has no dispersion parameter
        """
        pass


class Gaussian(Family):
    """Gaussian (Normal) family with identity link as canonical."""

    def __init__(self, link: Optional[Link] = None, dispersion_prior: float = 5.0):
        super().__init__(link)
        self._sigma: Optional[jnp.ndarray] = None
        self.dispersion_prior = dispersion_prior

    def _default_link(self) -> Link:
        return IdentityLink()

    def sample_dispersion(self) -> jnp.ndarray:
        return numpyro.sample('sigma', dist.HalfNormal(self.dispersion_prior))

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        if self._sigma is None:
            raise RuntimeError("Dispersion parameter not set. Call sample_dispersion first.")
        sigma = numpyro.deterministic('_sigma_det', numpyro.subsample(self._sigma, event_dim=0))
        return numpyro.sample(name, dist.Normal(mu, sigma), obs=obs)

    def set_dispersion(self, sigma: jnp.ndarray) -> None:
        """Set the dispersion parameter.

        Args:
            sigma: Standard deviation parameter
        """
        self._sigma = sigma


class Binomial(Family):
    """Binomial (Bernoulli) family with logit link as canonical."""

    def _default_link(self) -> Link:
        return LogitLink()

    def sample_dispersion(self) -> None:
        return None

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        return numpyro.sample(name, dist.Bernoulli(probs=mu), obs=obs)


class Poisson(Family):
    """Poisson family with log link as canonical."""

    def _default_link(self) -> Link:
        return LogLink()

    def sample_dispersion(self) -> None:
        return None

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        return numpyro.sample(name, dist.Poisson(rate=mu), obs=obs)


class NegativeBinomial(Family):
    """Negative Binomial family with log link as canonical."""

    def __init__(self, link: Optional[Link] = None, dispersion_prior: float = 5.0):
        super().__init__(link)
        self._phi: Optional[jnp.ndarray] = None
        self.dispersion_prior = dispersion_prior

    def _default_link(self) -> Link:
        return LogLink()

    def sample_dispersion(self) -> jnp.ndarray:
        return numpyro.sample('phi', dist.HalfNormal(self.dispersion_prior))

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        if self._phi is None:
            raise RuntimeError("Dispersion parameter not set. Call sample_dispersion first.")
        phi = numpyro.deterministic('_phi_det', numpyro.subsample(self._phi, event_dim=0))
        return numpyro.sample(name, dist.NegativeBinomial2(mean=mu, concentration=phi), obs=obs)

    def set_dispersion(self, phi: jnp.ndarray) -> None:
        """Set the dispersion parameter.

        Args:
            phi: Concentration parameter
        """
        self._phi = phi


class Gamma(Family):
    """Gamma family with log link as canonical."""

    def __init__(self, link: Optional[Link] = None, dispersion_prior: float = 5.0):
        super().__init__(link)
        self._alpha: Optional[jnp.ndarray] = None
        self.dispersion_prior = dispersion_prior

    def _default_link(self) -> Link:
        return LogLink()

    def sample_dispersion(self) -> jnp.ndarray:
        return numpyro.sample('alpha', dist.HalfNormal(self.dispersion_prior))

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        if self._alpha is None:
            raise RuntimeError("Dispersion parameter not set. Call sample_dispersion first.")
        alpha = numpyro.deterministic('_alpha_det', numpyro.subsample(self._alpha, event_dim=0))
        rate = alpha / mu
        return numpyro.sample(name, dist.Gamma(alpha, rate), obs=obs)

    def set_dispersion(self, alpha: jnp.ndarray) -> None:
        """Set the shape parameter.

        Args:
            alpha: Shape/concentration parameter
        """
        self._alpha = alpha


class OrderedLogistic(Family):
    """Ordered (Ordinal) Logistic Regression family using proportional odds model.

    For ordinal outcomes with K ordered categories (0, 1, ..., K-1).
    Uses cumulative logit link with ordered cutpoints.
    """

    def __init__(self, num_categories: int, link: Optional[Link] = None, dispersion_prior: float = 2.0):
        """Initialize ordered logistic family.

        Args:
            num_categories: Number of ordinal categories (K >= 2)
            link: Link function (included for API compatibility, not used)

        Raises:
            ValueError: If num_categories < 2
        """
        if num_categories < 2:
            raise ValueError(f"num_categories must be >= 2, got {num_categories}")
        self.num_categories = num_categories
        super().__init__(link)
        self._cutpoints: Optional[jnp.ndarray] = None
        self.dispersion_prior = dispersion_prior

    def _default_link(self) -> Link:
        return LogitLink()

    def sample_dispersion(self) -> jnp.ndarray:
        """Sample ordered cutpoints (thresholds) for the K-1 category boundaries.

        Returns:
            Ordered cutpoints array of shape (K-1,)
        """
        cutpoints = numpyro.sample(
            'cutpoints',
            dist.TransformedDistribution(
                dist.Normal(0.0, self.dispersion_prior).expand([self.num_categories - 1]),
                dist.transforms.OrderedTransform()
            )
        )
        return cutpoints

    def sample_likelihood(
            self,
            name: str,
            mu: jnp.ndarray,
            obs: Optional[jnp.ndarray] = None
    ) -> jnp.ndarray:
        """Sample from ordered categorical distribution.

        Args:
            name: Name for the sample site
            mu: Linear predictor (not transformed through link)
            obs: Observed ordinal categories as integers in [0, K-1]

        Returns:
            Sampled category indices
        """
        if self._cutpoints is None:
            raise RuntimeError("Cutpoints not set. Call sample_dispersion first.")

        cutpoints = self._cutpoints
        num_observations = mu.shape[0]

        cumulative_probs = jax.nn.sigmoid(cutpoints[None, :] - mu[:, None])

        probs_below = jnp.concatenate(
            [jnp.zeros((num_observations, 1)), cumulative_probs],
            axis=1
        )
        probs_above = jnp.concatenate(
            [cumulative_probs, jnp.ones((num_observations, 1))],
            axis=1
        )
        category_probs = probs_above - probs_below

        return numpyro.sample(name, dist.Categorical(probs=category_probs), obs=obs)

    def set_dispersion(self, cutpoints: jnp.ndarray) -> None:
        """Set the ordered cutpoints.

        Args:
            cutpoints: Ordered cutpoints array of shape (K-1,)
        """
        self._cutpoints = cutpoints
