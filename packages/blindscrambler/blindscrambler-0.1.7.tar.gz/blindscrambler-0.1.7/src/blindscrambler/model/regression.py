# Author metadata

__Name__ = "Syed Raza"
__email__ = "sar0033@uah.edu"

# import statements
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Tuple, Optional
import warnings

# add a linear Regression class:
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
        """

        # the main variables 
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.tolerance = tolerance

        # Model parameters
        self.w_0 = nn.Parameter(torch.randn(1, requires_grad=True))  # intercept
        self.w_1 = nn.Parameter(torch.randn(1, requires_grad=True))  # slope

        # training data storage
        self.X_train = None
        self.y_train = None 

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
        self.w0_history = []
        self.w1_history = []

    def forward(self, X: torch.tensor) -> torch.tensor:
        """
        """
        return self.w_1 * X + self.w_0
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LinearRegression':
        """
        """
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
            # Track parameter history (after update)
            with torch.no_grad():
                self.w0_history.append(float(self.w_0.item()))
                self.w1_history.append(float(self.w_1.item()))
            
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
    
    def analysis_plot(self, w_0: Optional[float] = None, w_1: Optional[float] = None):
        """
        Create a 2x2 analysis figure showing:
        - Original data and fitted regression line
        - Training loss over epochs
        - Intercept (w_0) trajectory over epochs
        - Slope (w_1) trajectory over epochs

        Args:
            w_0: Intercept to plot final fit; if None, uses current self.w_0
            w_1: Slope to plot final fit; if None, uses current self.w_1
        """
        if self.X_train is None or self.y_train is None:
            raise ValueError("No training data found. Fit the model before plotting.")

        # Resolve parameters for plotting
        if w_0 is None:
            w_0 = float(self.w_0.detach().cpu().item())
        if w_1 is None:
            w_1 = float(self.w_1.detach().cpu().item())

        X_np = self.X_train.detach().cpu().numpy().reshape(-1)
        y_np = self.y_train.detach().cpu().numpy().reshape(-1)

        # Build line for fit
        x_line = np.linspace(X_np.min(), X_np.max(), 200)
        y_line = w_1 * x_line + w_0

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # 1) Data + fit
        ax = axes[0, 0]
        ax.scatter(X_np, y_np, color='tab:blue', alpha=0.7, label='Data')
        ax.plot(x_line, y_line, color='tab:red', label=f'Fit: y={w_1:.3f}x+{w_0:.3f}')
        ax.set_title('Data and Fitted Line')
        ax.set_xlabel('X')
        ax.set_ylabel('y')
        ax.legend()

        # 2) Loss history
        ax = axes[0, 1]
        if len(self.loss_history) > 0:
            ax.plot(range(1, len(self.loss_history) + 1), self.loss_history, color='tab:green')
        ax.set_title('Training Loss')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('MSE Loss')
        ax.grid(True, linestyle='--', alpha=0.3)

        # 3) w_0 history
        ax = axes[1, 0]
        if len(self.w0_history) > 0:
            ax.plot(range(1, len(self.w0_history) + 1), self.w0_history, color='tab:purple')
        ax.axhline(w_0, color='gray', linestyle='--', alpha=0.6, label='Final w_0')
        ax.set_title('w_0 (Intercept) over Epochs')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('w_0')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)

        # 4) w_1 history
        ax = axes[1, 1]
        if len(self.w1_history) > 0:
            ax.plot(range(1, len(self.w1_history) + 1), self.w1_history, color='tab:orange')
        ax.axhline(w_1, color='gray', linestyle='--', alpha=0.6, label='Final w_1')
        ax.set_title('w_1 (Slope) over Epochs')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('w_1')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)

        plt.tight_layout()
        return fig, axes
