from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Any, Union, Tuple, TYPE_CHECKING

import arviz as az
import jax
import pandas as pd
import patsy
from jax import numpy as jnp, random
from numpyro.infer import MCMC, Predictive

from jaxglm.families import Family, OrderedLogistic

if TYPE_CHECKING:
    from jaxglm.model import GLM

logger = logging.getLogger(__name__)

@dataclass
class GLMResults:
    """Container for GLM fitting results with diagnostics and prediction methods."""

    mcmc: MCMC
    posterior_samples: Dict[str, jnp.ndarray]
    posterior_samples_by_chain: Dict[str, jnp.ndarray]
    family: Family
    design_matrix: jnp.ndarray
    response: jnp.ndarray
    design_info: Optional[patsy.DesignInfo] = None
    formula: Optional[str] = None
    _inference_data: Optional[az.InferenceData] = None
    _glm_instance: Optional['GLM'] = None

    def summary(
            self,
            var_names: Optional[list[str]] = None,
            hdi_prob: float = 0.94,
            kind: str = 'stats'
    ) -> az.InferenceData:
        """Print summary statistics for posterior samples.

        Args:
            var_names: List of variable names to summarize. If None, summarizes all.
            hdi_prob: Probability mass for highest density interval
            kind: Type of summary - 'stats', 'diagnostics', or 'all'

        Returns:
            ArviZ InferenceData object
        """
        logger.info(f"Generating {kind} summary for GLM results")

        print(f"\n{'=' * 70}")
        if self.formula:
            print(f"Formula: {self.formula}")
        print(f"GLM Family: {self.family.__class__.__name__}")
        print(f"Link Function: {self.family.link.__class__.__name__}")
        print(f"{'=' * 70}\n")

        coefficient_names = None
        if self.design_info is not None:
            coefficient_names = self.design_info.column_names

        inference_data = self.to_inference_data()

        if kind in ['stats', 'all']:
            summary_df = az.summary(
                inference_data,
                var_names=var_names,
                hdi_prob=hdi_prob,
                kind='stats'
            )

            if coefficient_names and 'beta' in summary_df.index:
                beta_mask = summary_df.index.str.startswith('beta[')
                beta_indices = summary_df.index[beta_mask]
                if len(beta_indices) > 0:
                    rename_map = {}
                    for idx in beta_indices:
                        param_index = int(idx.split('[')[1].split(']')[0])
                        if param_index < len(coefficient_names):
                            rename_map[idx] = f"beta[{coefficient_names[param_index]}]"
                    summary_df = summary_df.rename(index=rename_map)

            print(summary_df)

        if kind in ['diagnostics', 'all']:
            print(f"\n{'=' * 70}")
            print("MCMC Diagnostics")
            print(f"{'=' * 70}\n")

            diagnostics_df = az.summary(
                inference_data,
                var_names=var_names,
                kind='diagnostics'
            )
            print(diagnostics_df)

        return inference_data

    def to_inference_data(self) -> az.InferenceData:
        """Convert MCMC results to ArviZ InferenceData format.

        Returns:
            ArviZ InferenceData object with coordinates and dimensions
        """
        if self._inference_data is None:
            # Set up coordinates
            if self.design_info is not None:
                coords = {"beta_dim": self.design_info.column_names}
            else:
                num_features = self.design_matrix.shape[1]
                coords = {"beta_dim": [f"x{i}" for i in range(num_features)]}

            # Add cutpoints for ordered logistic
            if isinstance(self.family, OrderedLogistic):
                num_cutpoints = self.family.num_categories - 1
                coords['cutpoints_dim'] = [f"cutpoint_{i}" for i in range(num_cutpoints)]

            # Set up dimensions
            dims = {'beta': ['beta_dim']}
            if isinstance(self.family, OrderedLogistic):
                dims['cutpoints'] = ['cutpoints_dim']

            # Create InferenceData from samples organized by chain
            self._inference_data = az.from_dict(
                posterior=self.posterior_samples_by_chain,
                coords=coords,
                dims=dims,
            )
            logger.debug("Created InferenceData object")

        return self._inference_data

    def _plot_with_inference_data(
            self,
            plot_func: callable,
            var_names: Optional[list[str]] = None,
            **kwargs
    ) -> Any:
        """Helper method for plotting functions.

        Args:
            plot_func: ArviZ plotting function to call
            var_names: Variables to plot
            **kwargs: Additional arguments for plotting function

        Returns:
            Matplotlib axes object
        """
        inference_data = self.to_inference_data()
        return plot_func(inference_data, var_names=var_names, **kwargs)

    def plot_trace(self, var_names: Optional[list[str]] = None, **kwargs) -> Any:
        """Generate trace plots for MCMC samples.

        Args:
            var_names: Variables to plot. If None, plots main model parameters (beta, cutpoints).
            **kwargs: Additional arguments passed to az.plot_trace

        Returns:
            Matplotlib axes object
        """
        if var_names is None:
            var_names = ['beta']
            if isinstance(self.family, OrderedLogistic):
                var_names.append('cutpoints')

        logger.info(f"Generating trace plots for variables: {var_names}")
        return self._plot_with_inference_data(az.plot_trace, var_names, **kwargs)

    def plot_posterior(
            self,
            var_names: Optional[list[str]] = None,
            hdi_prob: float = 0.94,
            **kwargs
    ) -> Any:
        """Generate posterior distribution plots.

        Args:
            var_names: Variables to plot. If None, plots main model parameters (beta, cutpoints).
            hdi_prob: Probability mass for highest density interval
            **kwargs: Additional arguments passed to az.plot_posterior

        Returns:
            Matplotlib axes object
        """
        if var_names is None:
            var_names = ['beta']
            if isinstance(self.family, OrderedLogistic):
                var_names.append('cutpoints')

        logger.info(f"Generating posterior plots for variables: {var_names}")
        return self._plot_with_inference_data(
            az.plot_posterior,
            var_names,
            hdi_prob=hdi_prob,
            **kwargs
        )

    def plot_forest(
            self,
            var_names: Optional[list[str]] = None,
            hdi_prob: float = 0.94,
            **kwargs
    ) -> Any:
        """Generate forest plot for coefficient estimates.

        Args:
            var_names: Variables to plot. If None, plots main model parameters (beta, cutpoints).
            hdi_prob: Probability mass for highest density interval
            **kwargs: Additional arguments passed to az.plot_forest

        Returns:
            Matplotlib axes object
        """
        if var_names is None:
            var_names = ['beta']
            if isinstance(self.family, OrderedLogistic):
                var_names.append('cutpoints')

        logger.info(f"Generating forest plot for variables: {var_names}")
        return self._plot_with_inference_data(
            az.plot_forest,
            var_names,
            hdi_prob=hdi_prob,
            **kwargs
        )
    def loo(self) -> az.ELPDData:
        """Compute Leave-One-Out cross-validation information criterion.

        Returns:
            ArviZ ELPDData object containing LOO-CV results
        """
        inference_data = self.to_inference_data()
        logger.info("Computing LOO cross-validation")
        return az.loo(inference_data)

    def waic(self) -> az.ELPDData:
        """Compute Widely Applicable Information Criterion.

        Returns:
            ArviZ ELPDData object containing WAIC results
        """
        inference_data = self.to_inference_data()
        logger.info("Computing WAIC")
        return az.waic(inference_data)

    def predict(
            self,
            data: Optional[Union[jnp.ndarray, pd.DataFrame]] = None,
            prediction_type: str = 'response',
            return_sites: Tuple[str, ...] = ('y',),
            rng_key: Optional[jax.random.PRNGKey] = None
    ) -> Union[jnp.ndarray, Dict[str, jnp.ndarray]]:
        """Generate predictions from posterior samples.

        Args:
            data: New data for predictions. DataFrame if using formula, array otherwise.
                 If None, uses training data.
                 Note: For array input, should NOT include intercept column - it will be added automatically.
            prediction_type: Type of prediction:
                - 'response': Mean/probabilities (posterior mean of mean parameter)
                - 'link': Linear predictor scale
                - 'samples': All posterior samples of mean parameter
                - 'predictive': Full posterior predictive samples (includes observation noise)
            return_sites: Sites to return when prediction_type='predictive'
            rng_key: JAX random key for stochastic predictions

        Returns:
            Predictions as array or dict depending on prediction_type

        Raises:
            ValueError: If prediction_type is invalid or GLM instance unavailable
        """
        if data is None:
            design_matrix_new = self.design_matrix
        elif isinstance(data, pd.DataFrame) and self.design_info is not None:
            design_matrix_new = jnp.array(
                patsy.build_design_matrices([self.design_info], data)[0]
            )
        else:
            design_matrix_new = jnp.array(data)

            # Add intercept if the model was fit with one and data doesn't already have it
            if self._glm_instance is not None and self._glm_instance.fit_intercept:
                # Check if intercept already present (first column is all ones)
                if design_matrix_new.shape[1] == self.design_matrix.shape[1]:
                    # Already has correct number of columns, assume it's formatted correctly
                    pass
                else:
                    # Need to add intercept
                    num_obs = design_matrix_new.shape[0]
                    design_matrix_new = jnp.column_stack([jnp.ones(num_obs), design_matrix_new])

        if rng_key is None:
            rng_key = random.PRNGKey(1)

        logger.debug(
            f"Generating {prediction_type} predictions for "
            f"{design_matrix_new.shape[0]} observations"
        )

        if prediction_type == 'predictive':
            if self._glm_instance is None:
                raise ValueError(
                    "GLM instance not available. Cannot generate posterior predictive samples."
                )

            predictive = Predictive(self._glm_instance._model, self.posterior_samples)
            samples = predictive(rng_key, X=design_matrix_new, y=None)

            if return_sites == ('y',):
                return samples['y']
            else:
                return {site: samples[site] for site in return_sites if site in samples}

        elif prediction_type in ['response', 'link', 'samples']:
            beta_samples = self.posterior_samples['beta']
            linear_predictor = jnp.dot(design_matrix_new, beta_samples.T)

            if prediction_type == 'link':
                return jnp.mean(linear_predictor, axis=1)

            if isinstance(self.family, OrderedLogistic):
                cutpoints = self.posterior_samples['cutpoints']

                def compute_category_probs(
                        eta_sample: jnp.ndarray,
                        cutpoints_sample: jnp.ndarray
                ) -> jnp.ndarray:
                    cumulative_probs = jax.nn.sigmoid(
                        cutpoints_sample[None, :] - eta_sample[:, None]
                    )

                    num_obs = eta_sample.shape[0]
                    probs_below = jnp.concatenate(
                        [jnp.zeros((num_obs, 1)), cumulative_probs],
                        axis=1
                    )
                    probs_above = jnp.concatenate(
                        [cumulative_probs, jnp.ones((num_obs, 1))],
                        axis=1
                    )

                    return probs_above - probs_below

                all_probs = jax.vmap(compute_category_probs, in_axes=(1, 0))(
                    linear_predictor, cutpoints
                )

                if prediction_type == 'samples':
                    return all_probs
                else:
                    return jnp.mean(all_probs, axis=0)
            else:
                mean_parameter = self.family.link.inverse(linear_predictor)

                if prediction_type == 'response':
                    return jnp.mean(mean_parameter, axis=1)
                elif prediction_type == 'samples':
                    return mean_parameter
        else:
            raise ValueError(
                f"prediction_type must be 'response', 'link', 'samples', or 'predictive', "
                f"got {prediction_type}"
            )
    def predict_interval(
            self,
            data: Optional[Union[jnp.ndarray, pd.DataFrame]] = None,
            prob: float = 0.94
    ) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
        """Generate prediction intervals from posterior samples.

        Args:
            data: New data for predictions. If None, uses training data.
            prob: Probability mass for interval

        Returns:
            Tuple of (mean, lower_bound, upper_bound) arrays
        """
        samples = self.predict(data, prediction_type='samples')

        lower_percentile = (1.0 - prob) / 2.0
        upper_percentile = 1.0 - lower_percentile

        mean = jnp.mean(samples, axis=1 if samples.ndim == 2 else 0)
        lower = jnp.quantile(samples, lower_percentile, axis=1 if samples.ndim == 2 else 0)
        upper = jnp.quantile(samples, upper_percentile, axis=1 if samples.ndim == 2 else 0)

        logger.debug(f"Generated {prob * 100}% prediction intervals")

        return mean, lower, upper
