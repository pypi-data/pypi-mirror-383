import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Tuple, Optional
from numpy.linalg import inv
import warnings

class LinearRegression:
    """
    A PyTorch-based Linear Regression implementation for one variable.
    
    Model: y = w_1 * x + w_0
    Loss: Mean Squared Error
    
    Features:
    - Gradient-based optimization using PyTorch
    - Confidence intervals for parameters w_1 and w_0
    - Visualization with confidence bands
    """
    
    def __init__(self, learning_rate: float = 0.01, max_epochs: int = 1000, 
                 tolerance: float = 1e-6):
        """
        Initialize the Linear Regression model.
        
        Args:
            learning_rate: Learning rate for gradient descent
            max_epochs: Maximum number of training epochs
            tolerance: Convergence tolerance for early stopping
        """
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.tolerance = tolerance
        
        # Model parameters
        self.w_1 = nn.Parameter(torch.randn(1, requires_grad=True))  # slope
        self.w_0 = nn.Parameter(torch.randn(1, requires_grad=True))  # intercept
        
        # Training data storage
        self.X_train = None
        self.y_train = None
        
        self.w0_history = []
        self.w1_history = []
        
        # Model statistics for confidence intervals
        self.n_samples = None
        self.residual_sum_squares = None
        self.X_mean = None
        self.X_var = None
        self.fitted = False
        
        # Loss function and optimizer
        self.criterion = nn.MSELoss()
        self.optimizer = optim.SGD([self.w_1, self.w_0], lr=self.learning_rate)
        
        # Training history
        self.loss_history = []
    
    def forward(self, X: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the linear model.
        
        Args:
            X: Input tensor of shape (n_samples,)
            
        Returns:
            Predictions tensor of shape (n_samples,)
        """
        return self.w_1 * X + self.w_0
    
    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'LinearRegression':
        """
        Fit the linear regression model to the training data.
        
        Args:
            X: Input features of shape (n_samples,)
            y: Target values of shape (n_samples,)
            X_test: (optional) Test data to compute R-squared 
            y_test: (optional) Test data to compute R-squared 
            
            
        Returns:
            self: Returns the fitted model instance
        """
        self.X_orig = X
        self.y_orig = y
        # Convert to PyTorch tensors
        self.X_train = torch.tensor(X, dtype=torch.float32)
        self.y_train = torch.tensor(y, dtype=torch.float32)
        self.n_samples = len(X)
        
        # Store statistics for confidence intervals
        self.X_mean = float(np.mean(X))
        self.X_var = float(np.var(X, ddof=1))  # Sample variance
        
        
        # Training loop
        prev_loss = float('inf')
        
        for epoch in range(self.max_epochs):
            # Zero gradients
            self.optimizer.zero_grad()
            self.w0_history.append(self.w_0.item())
            self.w1_history.append(self.w_1.item())
            
            # Forward pass
            y_pred = self.forward(self.X_train)
            
            # Compute loss
            loss = self.criterion(y_pred, self.y_train)
            
            # Backward pass
            loss.backward()
            
            # Update parameters
            self.optimizer.step()
            
            # Store loss history
            current_loss = loss.item()
            self.loss_history.append(current_loss)
            
            # Check for convergence
            if abs(prev_loss - current_loss) < self.tolerance:
                print(f"Converged after {epoch + 1} epochs")
                break
            
            prev_loss = current_loss
        
        # Compute residual sum of squares for confidence intervals
        with torch.no_grad():
            y_pred = self.forward(self.X_train)
            residuals = self.y_train - y_pred
            self.residual_sum_squares = float(torch.sum(residuals ** 2))
        
        X_test = kwargs.get("X_test")
        y_test = kwargs.get("y_test")
        
        if isinstance(X_test, np.ndarray) and isinstance(y_test, np.ndarray):
            # Add intercept column if not already present
            if X_test.ndim == 1:
                X_test = X_test.reshape(-1, 1)
                X_test_with_bias = np.c_[np.ones(X_test.shape[0]), X_test]

                # Compute closed-form betas: (X^T X)^(-1) X^T y
                betas = inv(X_test_with_bias.T.dot(X_test_with_bias)).dot(X_test_with_bias.T).dot(y_test)

                # Predictions
                y_hat = X_test_with_bias.dot(betas)

                # Errors and R²
                errors = y_test - y_hat
                sse = np.sum(errors ** 2)
                tss = np.sum((y_test - y_test.mean()) ** 2)
                r2 = 1 - sse / tss
                print()
                print("Coefficient of Determination (R²) on test data:")
                print(r2)
                
        self.fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions on new data.
        
        Args:
            X: Input features of shape (n_samples,)
            
        Returns:
            Predictions as numpy array
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        X_tensor = torch.tensor(X, dtype=torch.float32)
        
        with torch.no_grad():
            predictions = self.forward(X_tensor)
        
        return predictions.numpy()
    
    def get_parameters(self) -> Tuple[float, float]:
        """
        Get the fitted parameters.
        
        Returns:
            Tuple of (w_1, w_0) - slope and intercept
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before accessing parameters")
        
        return float(self.w_1.item()), float(self.w_0.item())
    
    def analysis_plot(self):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Linear Regression Training Progress', fontsize=16)

        # Subplot 1: Original Data and Fitted Regression Line
        axes[0, 0].scatter(self.X_train, self.y_train, alpha=0.6, label='Original Data')
        y_pred = self.w_0.detach().numpy() + self.w_1.detach().numpy() * self.X_train.detach().numpy()
        axes[0, 0].plot(self.X_orig, y_pred, color='red', label='Fitted Regression Line')
        axes[0, 0].set_title('Original Data and Fitted Line')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('y')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Subplot 2: Loss as Training Progressed
        axes[0, 1].plot(self.loss_history)
        axes[0, 1].set_title('Loss vs. Epochs')
        axes[0, 1].set_xlabel('Epochs')
        axes[0, 1].set_ylabel('Mean Squared Error')
        axes[0, 1].grid(True)

        # Subplot 3: w0 (Intercept) as Training Progressed
        axes[1, 0].plot(self.w0_history)
        axes[1, 0].set_title('$w_0$ (Intercept) vs. Epochs')
        axes[1, 0].set_xlabel('Epochs')
        axes[1, 0].set_ylabel('$w_0$')
        axes[1, 0].grid(True)

        # Subplot 4: w1 (Slope) as Training Progressed
        axes[1, 1].plot(self.w1_history)
        axes[1, 1].set_title('$w_1$ (Slope) vs. Epochs')
        axes[1, 1].set_xlabel('Epochs')
        axes[1, 1].set_ylabel('$w_1$')
        axes[1, 1].grid(True)
        
        plt.show()
    
    def parameter_confidence_intervals(self, confidence_level: float = 0.95) -> dict:
        """
        Compute confidence intervals for parameters w_1 and w_0.
        
        Args:
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            Dictionary containing confidence intervals for both parameters
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before computing confidence intervals")
        
        # Degrees of freedom
        df = self.n_samples - 2
        
        # Critical t-value
        alpha = 1 - confidence_level
        t_critical = stats.t.ppf(1 - alpha/2, df)
        
        # Standard error of regression
        mse = self.residual_sum_squares / df
        se_regression = np.sqrt(mse)
        
        # Standard error for w_1 (slope)
        se_w1 = se_regression / np.sqrt(self.n_samples * self.X_var)
        
        # Standard error for w_0 (intercept)
        se_w0 = se_regression * np.sqrt(1/self.n_samples + self.X_mean**2 / (self.n_samples * self.X_var))
        
        # Get current parameter values
        w_1_val, w_0_val = self.get_parameters()
        
        # Compute confidence intervals
        w_1_ci = (
            w_1_val - t_critical * se_w1,
            w_1_val + t_critical * se_w1
        )
        
        w_0_ci = (
            w_0_val - t_critical * se_w0,
            w_0_val + t_critical * se_w0
        )
        
        return {
            'w_1_confidence_interval': w_1_ci,
            'w_0_confidence_interval': w_0_ci,
            'confidence_level': confidence_level,
            'standard_errors': {
                'se_w1': se_w1,
                'se_w0': se_w0,
                'se_regression': se_regression
            }
        }
    
    def plot_regression_with_confidence_band(self, confidence_level: float = 0.95, 
                                           figsize: Tuple[int, int] = (10, 6),
                                           title: Optional[str] = None) -> plt.Figure:
        """
        Plot the fitted regression line with confidence band.
        
        Args:
            confidence_level: Confidence level for the band
            figsize: Figure size tuple
            title: Optional plot title
            
        Returns:
            matplotlib Figure object
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before plotting")
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Convert training data to numpy for plotting
        X_np = self.X_train.numpy()
        y_np = self.y_train.numpy()
        
        # Create prediction range
        X_range = np.linspace(X_np.min(), X_np.max(), 100)
        y_pred_range = self.predict(X_range)
        
        # Compute confidence band
        df = self.n_samples - 2
        alpha = 1 - confidence_level
        t_critical = stats.t.ppf(1 - alpha/2, df)
        
        mse = self.residual_sum_squares / df
        se_regression = np.sqrt(mse)
        
        # Standard error for predictions (confidence band)
        X_centered = X_range - self.X_mean
        se_pred = se_regression * np.sqrt(1/self.n_samples + X_centered**2 / (self.n_samples * self.X_var))
        
        # Confidence band bounds
        margin_of_error = t_critical * se_pred
        y_upper = y_pred_range + margin_of_error
        y_lower = y_pred_range - margin_of_error
        
        # Plot data points
        ax.scatter(X_np, y_np, alpha=0.6, color='blue', label='Data points')
        
        # Plot regression line
        ax.plot(X_range, y_pred_range, 'r-', linewidth=2, label='Fitted line')
        
        # Plot confidence band
        ax.fill_between(X_range, y_lower, y_upper, alpha=0.3, color='red', 
                       label=f'{int(confidence_level*100)}% Confidence band')
        
        # Get parameter values for display
        w_1_val, w_0_val = self.get_parameters()
        
        # Labels and title
        ax.set_xlabel('X')
        ax.set_ylabel('y')
        if title is None:
            title = f'Linear Regression: y = {w_1_val:.3f}x + {w_0_val:.3f}'
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def summary(self) -> dict:
        """
        Provide a summary of the fitted model.
        
        Returns:
            Dictionary containing model summary statistics
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before generating summary")
        
        w_1_val, w_0_val = self.get_parameters()
        
        # R-squared calculation
        y_mean = float(torch.mean(self.y_train))
        ss_tot = float(torch.sum((self.y_train - y_mean) ** 2))
        r_squared = 1 - (self.residual_sum_squares / ss_tot)
        
        # Adjusted R-squared
        adj_r_squared = 1 - ((1 - r_squared) * (self.n_samples - 1) / (self.n_samples - 2))
        
        # RMSE
        rmse = np.sqrt(self.residual_sum_squares / self.n_samples)
        
        return {
            'parameters': {
                'w_1 (slope)': w_1_val,
                'w_0 (intercept)': w_0_val
            },
            'model_fit': {
                'r_squared': r_squared,
                'adjusted_r_squared': adj_r_squared,
                'rmse': rmse,
                'residual_sum_squares': self.residual_sum_squares
            },
            'training_info': {
                'n_samples': self.n_samples,
                'epochs_trained': len(self.loss_history),
                'final_loss': self.loss_history[-1] if self.loss_history else None
            }
        }



# np.random.seed(42)
# torch.manual_seed(42)

# n_samples = 100
# X = np.random.uniform(-5, 5, n_samples)
# true_slope = 2.5
# true_intercept = -1.2
# noise = np.random.normal(0, 1, n_samples)
# y = true_slope * X + true_intercept + noise

# print("=== Linear Regression with PyTorch ===")
# print(f"True parameters: slope={true_slope}, intercept={true_intercept}")
# print()

# # Create and fit model
# model = LinearRegression(learning_rate=0.01, max_epochs=10)
# model.fit(X, y)

# # Get fitted parameters
# fitted_slope, fitted_intercept = model.get_parameters()
# print(f"Fitted parameters: slope={fitted_slope:.4f}, intercept={fitted_intercept:.4f}")

# # Model summary
# summary = model.summary()
# print(f"\nModel Summary:")
# print(f"R-squared: {summary['model_fit']['r_squared']:.4f}")
# print(f"RMSE: {summary['model_fit']['rmse']:.4f}")
# print(f"Training epochs: {summary['training_info']['epochs_trained']}")

# # Confidence intervals
# ci_results = model.parameter_confidence_intervals(confidence_level=0.95)
# print(f"\n95% Confidence Intervals:")
# print(f"w_1 (slope): [{ci_results['w_1_confidence_interval'][0]:.4f}, {ci_results['w_1_confidence_interval'][1]:.4f}]")
# print(f"w_0 (intercept): [{ci_results['w_0_confidence_interval'][0]:.4f}, {ci_results['w_0_confidence_interval'][1]:.4f}]")

# # Plot results
# fig = model.plot_regression_with_confidence_band(confidence_level=0.95)
# plt.show()

# # Test different confidence levels
# for conf_level in [0.90, 0.95, 0.99]:
#     ci = model.parameter_confidence_intervals(confidence_level=conf_level)
#     print(f"\n{int(conf_level*100)}% CI for slope: [{ci['w_1_confidence_interval'][0]:.4f}, {ci['w_1_confidence_interval'][1]:.4f}]")