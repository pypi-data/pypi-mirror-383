from __future__ import annotations

from typing import Any

import torch
from torch import Tensor
from torch.distributions import Wishart as TorchWishart

from tensorcontainer.tensor_distribution.base import TensorDistribution


class TensorWishart(TensorDistribution):
    """
    Creates a Wishart distribution parameterized by a symmetric positive definite matrix.

    Args:
        df (Tensor): The degrees of freedom of the distribution.
        covariance_matrix (Tensor | None): The covariance matrix of the distribution.
        precision_matrix (Tensor | None): The precision matrix of the distribution.
        scale_tril (Tensor | None): The lower-triangular Cholesky factor of the scale matrix.
        validate_args (bool | None): Whether to validate the arguments.
    """

    df: Tensor
    # Note: Matrix parameters are not annotated as class attributes because they have
    # event dimensions that are incompatible with batch shape validation

    def __init__(
        self,
        df: Tensor,
        covariance_matrix: Tensor | None = None,
        precision_matrix: Tensor | None = None,
        scale_tril: Tensor | None = None,
        validate_args: bool | None = None,
    ) -> None:
        # Validate that exactly one of the matrix parameters is provided
        num_params = sum(
            p is not None for p in [covariance_matrix, precision_matrix, scale_tril]
        )
        if num_params != 1:
            raise ValueError(
                "Expected exactly one of `covariance_matrix`, `precision_matrix`, "
                f"`scale_tril` to be specified, but got {num_params}."
            )

        self.df = df
        self._covariance_matrix = covariance_matrix
        self._precision_matrix = precision_matrix
        self._scale_tril = scale_tril

        # For Wishart, we need to use the df tensor as the primary shape reference
        # since the matrix parameters have additional event dimensions
        super().__init__(df.shape, df.device, validate_args)

    def dist(self) -> TorchWishart:
        """
        Returns the underlying torch.distributions.Distribution instance.
        """
        return TorchWishart(
            df=self.df,
            covariance_matrix=self._covariance_matrix,
            precision_matrix=self._precision_matrix,
            scale_tril=self._scale_tril,
            validate_args=self._validate_args,
        )

    @classmethod
    def _unflatten_distribution(cls, attributes: dict[str, Any]) -> TensorWishart:
        return cls(
            df=attributes["df"],
            covariance_matrix=attributes.get("_covariance_matrix"),
            precision_matrix=attributes.get("_precision_matrix"),
            scale_tril=attributes.get("_scale_tril"),
            validate_args=attributes.get("_validate_args"),
        )

    @property
    def dtype(self) -> torch.dtype:
        """Return the dtype of the distribution parameters."""
        return self.df.dtype

    @property
    def covariance_matrix(self) -> Tensor:
        return self.dist().covariance_matrix

    @property
    def precision_matrix(self) -> Tensor:
        return self.dist().precision_matrix

    @property
    def scale_tril(self) -> Tensor:
        return self.dist().scale_tril
