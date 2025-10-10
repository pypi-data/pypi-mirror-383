from __future__ import annotations

import logging
from typing import Optional

import jax
import numpyro
import pandas as pd
import patsy
from jax import numpy as jnp, random
from numpyro import distributions as dist
from numpyro.infer import NUTS, MCMC

from jaxglm.families import Family, Gaussian, OrderedLogistic
from jaxglm.results import GLMResults
logger = logging.getLogger(__name__)

class GLM:
    """Generalized Linear Model with Bayesian inference via NumPyro.

    Supports standard GLM families (Gaussian, Binomial, Poisson, etc.) with flexible
    link functions, ordinal regression, Patsy formula interface, and ArviZ diagnostics.

    Examples:
        Array-based interface:
            >>> model = GLM(y, X, family=Binomial())
            >>> results = model.fit()
            >>> predictions = results.predict(X_new)

        Formula-based interface:
            >>> model = GLM.from_formula("y ~ x1 + x2 + x1:x2", data=df, family=Poisson())
            >>> results = model.fit()
            >>> results.summary()
    """

    def __init__(
            self,
            response: jnp.ndarray,
            design_matrix: jnp.ndarray,
            family: Optional[Family] = None,
            prior_scale: float = 10.0,
            fit_intercept: bool = True
    ):
        """Initialize GLM.

        Args:
            response: Response variable of shape (n_samples,)
            design_matrix: Design matrix of shape (n_samples, n_features)
            family: GLM family specification. Defaults to Gaussian().
            prior_scale: Scale parameter for Normal priors on coefficients
            fit_intercept: Whether to add intercept column to design matrix
        """
        if family is None:
            family = Gaussian()
            logger.info("No family specified, defaulting to Gaussian")

        self.response = jnp.ravel(jnp.array(response))
        self.family = family
        self.prior_scale = prior_scale
        self.fit_intercept = fit_intercept
        self.design_info: Optional[patsy.DesignInfo] = None
        self.formula: Optional[str] = None

        if fit_intercept:
            num_observations = design_matrix.shape[0]
            self.design_matrix = jnp.column_stack([jnp.ones(num_observations), design_matrix])
            logger.debug("Added intercept column to design matrix")
        else:
            self.design_matrix = jnp.array(design_matrix)

        self.num_features = self.design_matrix.shape[1]
        logger.info(
            f"Initialized GLM with {self.num_features} features and "
            f"{self.design_matrix.shape[0]} observations"
        )

    @classmethod
    def from_formula(
            cls,
            formula: str,
            data: pd.DataFrame,
            family: Optional[Family] = None,
            prior_scale: float = 10.0
    ) -> 'GLM':
        """Create GLM from Patsy formula string.

        Args:
            formula: Patsy formula (e.g., "y ~ x1 + x2 + x1:x2")
            data: DataFrame containing variables referenced in formula
            family: GLM family specification. Defaults to Gaussian().
            prior_scale: Scale parameter for Normal priors on coefficients

        Returns:
            GLM instance configured with formula

        Examples:
            >>> model = GLM.from_formula("y ~ x1 + x2", data=df, family=Binomial())
            >>> model = GLM.from_formula("count ~ C(group) * age", data=df, family=Poisson())
        """
        if family is None:
            family = Gaussian()
            logger.info("No family specified, defaulting to Gaussian")

        logger.info(f"Parsing formula: {formula}")
        response_matrix, design_matrix = patsy.dmatrices(
            formula,
            data,
            return_type='dataframe'
        )

        glm_instance = cls(
            response=jnp.array(response_matrix.values.ravel()),
            design_matrix=jnp.array(design_matrix.values),
            family=family,
            prior_scale=prior_scale,
            fit_intercept=False
        )

        glm_instance.design_info = design_matrix.design_info
        glm_instance.formula = formula

        logger.info(
            f"Created GLM from formula with {len(design_matrix.columns)} terms"
        )

        return glm_instance

    def _model(self, X: jnp.ndarray, y: Optional[jnp.ndarray] = None) -> None:
        """NumPyro model definition for GLM.

        Args:
            X: Design matrix of shape (n_samples, n_features)
            y: Response variable of shape (n_samples,). None for predictions.
        """
        beta = numpyro.sample(
            'beta',
            dist.Normal(0.0, self.prior_scale).expand([self.num_features])
        )

        dispersion = self.family.sample_dispersion()
        if dispersion is not None:
            if hasattr(self.family, 'set_dispersion'):
                self.family.set_dispersion(dispersion)

        linear_predictor = jnp.dot(X, beta)

        if isinstance(self.family, OrderedLogistic):
            mean_parameter = linear_predictor
        else:
            mean_parameter = self.family.link.inverse(linear_predictor)

        self.family.sample_likelihood('y', mean_parameter, obs=y)

    def fit(
            self,
            num_warmup: int = 1000,
            num_samples: int = 2000,
            num_chains: int = 4,
            rng_key: Optional[jax.random.PRNGKey] = None,
            progress_bar: bool = True
    ) -> GLMResults:
        """Fit GLM using NUTS sampler.

        Args:
            num_warmup: Number of warmup/adaptation iterations per chain
            num_samples: Number of posterior samples to draw per chain
            num_chains: Number of independent MCMC chains to run
            rng_key: JAX random key. If None, uses key 0.
            progress_bar: Whether to display progress bar during sampling

        Returns:
            GLMResults object containing posterior samples and diagnostics
        """
        if rng_key is None:
            rng_key = random.PRNGKey(0)

        logger.info(
            f"Fitting GLM with {num_chains} chains, "
            f"{num_warmup} warmup and {num_samples} sampling iterations"
        )

        kernel = NUTS(self._model)
        mcmc = MCMC(
            kernel,
            num_warmup=num_warmup,
            num_samples=num_samples,
            num_chains=num_chains,
            progress_bar=progress_bar
        )

        mcmc.run(rng_key, X=self.design_matrix, y=self.response)

        logger.info("MCMC sampling completed successfully")

        posterior_samples = mcmc.get_samples()
        posterior_samples_by_chain = mcmc.get_samples(group_by_chain=True)

        return GLMResults(
            mcmc=mcmc,
            posterior_samples=posterior_samples,
            posterior_samples_by_chain=posterior_samples_by_chain,
            family=self.family,
            design_matrix=self.design_matrix,
            response=self.response,
            design_info=self.design_info,
            formula=self.formula,
            _glm_instance=self
        )
