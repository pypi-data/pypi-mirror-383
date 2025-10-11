#!/usr/bin/env python3

import math
import os
import random
import unittest
import warnings
from math import pi
from unittest.mock import patch

import linear_operator
import torch
from torch import optim

import gpytorch
from gpytorch.constraints import GreaterThan
from gpytorch.distributions import MultivariateNormal
from gpytorch.kernels import RFFKernel, ScaleKernel
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.means import ConstantMean
from gpytorch.priors import SmoothedBoxPrior
from gpytorch.utils.warnings import NumericalWarning


class RFFRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, num_features: int):
        assert num_features % 2 == 0, "num_features must be even"
        likelihood = GaussianLikelihood()
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = ConstantMean(constant_prior=SmoothedBoxPrior(-1e-5, 1e-5))
        self.covar_module = ScaleKernel(RFFKernel(num_samples=(num_features // 2)))

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return MultivariateNormal(mean_x, covar_x)


class LinearRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y):
        # We throw away num_features here, because it corresponds to the number of features in the data
        likelihood = GaussianLikelihood(noise_constraint=GreaterThan(1e-3))
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = ConstantMean(constant_prior=SmoothedBoxPrior(-1e-5, 1e-5))
        self.covar_module = ScaleKernel(gpytorch.kernels.LinearKernel())

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return MultivariateNormal(mean_x, covar_x)


class _AbstractTestLowRankRegression():
    num_features = 20  # Expected rank of the covariance matrix

    def setUp(self):
        if os.getenv("UNLOCK_SEED") is None or os.getenv("UNLOCK_SEED").lower() == "false":
            self.rng_state = torch.get_rng_state()
            torch.manual_seed(0)
            random.seed(0)

    def tearDown(self):
        if hasattr(self, "rng_state"):
            torch.set_rng_state(self.rng_state)

    def make_data(self):
        raise NotImplementedError

    def make_model(self, train_x, train_y):
        raise NotImplementedError

    def test_rff_mean_abs_error(self):
        # Suppress numerical warnings
        warnings.simplefilter("ignore", NumericalWarning)

        # Track all matrix sizes passed to cholesky_ex
        cholesky_sizes = []
        original_cholesky_ex = torch.linalg.cholesky_ex

        def wrapped_cholesky_ex(matrix, *args, **kwargs):
            cholesky_sizes.append(matrix.shape)
            return original_cholesky_ex(matrix, *args, **kwargs)

        with (
            patch(
                "torch.linalg.cholesky_ex",
                wraps=wrapped_cholesky_ex,
            ) as mocked_cholesky_ex,
        ):
            train_x, train_y, test_x, test_y = self.make_data()
            gp_model = self.make_model(train_x, train_y)
            mll = gpytorch.mlls.ExactMarginalLogLikelihood(gp_model.likelihood, gp_model)

            # Optimize the model
            gp_model.train()

            optimizer = optim.Adam(gp_model.parameters(), lr=0.1)
            for i in range(30):
                calls_before = mocked_cholesky_ex.call_count

                optimizer.zero_grad()
                output = gp_model(train_x)
                loss = -mll(output, train_y)
                loss.backward()
                optimizer.step()

                calls_after = mocked_cholesky_ex.call_count

                # Assert exactly one call per iteration
                self.assertEqual(
                    calls_after - calls_before,
                    1,
                    f"Expected 1 cholesky call in iteration {i}, got {calls_after - calls_before}",
                )

                # Check that we have the right LinearOperator type
                kernel = gp_model.likelihood(gp_model(train_x)).lazy_covariance_matrix.evaluate_kernel()
                if train_y.size(-1) >= self.num_features:
                    self.assertIsInstance(kernel, linear_operator.operators.LowRankRootAddedDiagLinearOperator)
                else:
                    self.assertIsInstance(kernel, linear_operator.operators.AddedDiagLinearOperator)

            for param in gp_model.parameters():
                self.assertTrue(param.grad is not None)
                self.assertGreater(param.grad.norm().item(), 0)

            # Test the model
            gp_model.eval()

            with torch.no_grad():
                calls_before = mocked_cholesky_ex.call_count

                test_dist = gp_model(test_x)
                _ = test_dist.covariance_matrix  # Force computation of covariances
                _ = test_dist.rsample(torch.Size((1000,)))  # Force sampling
                mean_abs_error = torch.mean(torch.abs(test_y - test_dist.mean))

                calls_after = mocked_cholesky_ex.call_count

                # Assert exactly two calls (mean/covar + sampling) during prediction
                self.assertEqual(
                    calls_after - calls_before,
                    2,
                    f"Expected 2 cholesky calls during prediction, got {calls_after - calls_before}",
                )

        # Check that the model makes good predictions
        self.assertLess(mean_abs_error.squeeze().item(), 0.15)

        # Check sizes of cholesky systems during training
        for idx, size in enumerate(cholesky_sizes[:-2]):
            expected_size = min(self.num_features, train_y.size(-1))
            self.assertEqual(
                size,
                torch.Size([expected_size, expected_size]),
                f"Expected tensor of size [{expected_size} x {expected_size}] for prediction call {idx}, got {size}",
            )
        # Check sizes of first prediction Cholesky system
        expected_size = min(self.num_features, train_y.size(-1))
        self.assertEqual(
            cholesky_sizes[-2],
            torch.Size([expected_size, expected_size]),
            f"Expected tensor of size [{expected_size} x {expected_size}] for prediction call {idx}, got {size}",
        )
        # Check sizes of first prediction Cholesky system
        expected_size = self.num_features
        self.assertEqual(
            cholesky_sizes[-1],
            torch.Size([expected_size, expected_size]),
            f"Expected tensor of size [{expected_size} x {expected_size}] for prediction call {idx}, got {size}",
        )


class TestRFFRegression(_AbstractTestLowRankRegression, unittest.TestCase):
    def make_data(self):
        train_x = torch.linspace(0, 1, 100)
        train_y = torch.sin(train_x * (2 * pi))
        train_y.add_(torch.randn_like(train_y), alpha=1e-2)
        test_x = torch.rand(51)
        test_y = torch.sin(test_x * (2 * pi))
        return train_x, train_y, test_x, test_y

    def make_model(self, train_x, train_y):
        return RFFRegressionModel(train_x, train_y, num_features=self.num_features)


class TestLinearRegressionSmallD(_AbstractTestLowRankRegression, unittest.TestCase):
    def make_data(self):
        # We throw away num_features here, because it corresponds to the number of RFF features,
        # not the number of dimensions in the data.
        train_x = torch.randn(100, self.num_features)
        beta = torch.randn(self.num_features)
        train_y = train_x @ beta + torch.randn_like(train_x[..., 0]) * 0.1
        test_x = torch.randn(51, self.num_features)
        test_y = test_x @ beta
        return train_x, train_y, test_x, test_y

    def make_model(self, train_x, train_y):
        return LinearRegressionModel(train_x, train_y)


class TestLinearRegressionLargeD(_AbstractTestLowRankRegression, unittest.TestCase):
    num_features = 200  # Expected # of features

    def make_data(self):
        # We throw away num_features here, because it corresponds to the number of RFF features,
        # not the number of dimensions in the data.
        feature_sizes = torch.cat([torch.ones(10), torch.full((self.num_features - 10,), 1e-4)])
        train_x = torch.randn(100, self.num_features) * feature_sizes
        beta = torch.randn(self.num_features) / math.sqrt(10)
        train_y = train_x @ beta + torch.randn_like(train_x[..., 0]) * 0.01
        test_x = torch.randn(51, self.num_features) * feature_sizes
        test_y = test_x  @ beta
        return train_x, train_y, test_x, test_y

    def make_model(self, train_x, train_y):
        return LinearRegressionModel(train_x, train_y)
