"""
NumPyro GLM Toolkit

A production-ready Generalized Linear Model interface for NumPyro with statsmodels-like API.
Supports standard GLM families, ordinal regression, Patsy formulas, and ArviZ diagnostics.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import jax
import jax.numpy as jnp

logger = logging.getLogger(__name__)


class Link(ABC):
    """Abstract base class for GLM link functions."""

    @abstractmethod
    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        """Transform mean parameter to linear predictor scale.

        Args:
            mu: Mean parameter on the response scale

        Returns:
            Linear predictor eta = g(mu)
        """
        pass

    @abstractmethod
    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        """Transform linear predictor to mean parameter scale.

        Args:
            eta: Linear predictor

        Returns:
            Mean parameter mu = g^{-1}(eta)
        """
        pass

    @abstractmethod
    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        """Compute derivative of link function with respect to mu.

        Args:
            mu: Mean parameter on the response scale

        Returns:
            Derivative dg/dmu
        """
        pass


class IdentityLink(Link):
    """Identity link function: g(mu) = mu"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        return mu

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        return eta

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        return jnp.ones_like(mu)


class LogLink(Link):
    """Log link function: g(mu) = log(mu)"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        return jnp.log(mu)

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        return jnp.exp(eta)

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        return 1.0 / mu


class LogitLink(Link):
    """Logit link function: g(mu) = log(mu / (1 - mu))"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        return jnp.log(mu / (1.0 - mu))

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        return jax.nn.sigmoid(eta)

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        return 1.0 / (mu * (1.0 - mu))


class ProbitLink(Link):
    """Probit link function: g(mu) = Phi^{-1}(mu) where Phi is standard normal CDF"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        from jax.scipy.special import ndtri
        return ndtri(mu)

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        from jax.scipy.special import ndtr
        return ndtr(eta)

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        from jax.scipy.special import ndtri
        sqrt_2pi = jnp.sqrt(2.0 * jnp.pi)
        z = ndtri(mu)
        return sqrt_2pi * jnp.exp(0.5 * z ** 2)


class InverseLink(Link):
    """Inverse link function: g(mu) = 1/mu"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        return 1.0 / mu

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        return 1.0 / eta

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        return -1.0 / (mu ** 2)


class SqrtLink(Link):
    """Square root link function: g(mu) = sqrt(mu)"""

    def link(self, mu: jnp.ndarray) -> jnp.ndarray:
        return jnp.sqrt(mu)

    def inverse(self, eta: jnp.ndarray) -> jnp.ndarray:
        return eta ** 2

    def derivative(self, mu: jnp.ndarray) -> jnp.ndarray:
        return 0.5 / jnp.sqrt(mu)
