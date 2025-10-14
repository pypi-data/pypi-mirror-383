from whitepossum import LinearRegression
import polars as pl
import numpy as np
import torch



hdyroPowerData = pl.read_csv("Hydropower.csv")
BCRdata = hdyroPowerData.get_column("BCR")
APdata = hdyroPowerData.get_column("AnnualProduction")

hydroPowerModel = LinearRegression(learning_rate=0.5, max_epochs=100)

hydroPowerModel = hydroPowerModel.fit(BCRdata.to_numpy(), APdata.to_numpy())


print(hydroPowerModel.get_parameters())

# Model summary
summary = hydroPowerModel.summary()
print(f"\nModel Summary:")
print(f"R-squared: {summary['model_fit']['r_squared']:.4f}")
print(f"RMSE: {summary['model_fit']['rmse']:.4f}")
print(f"Training epochs: {summary['training_info']['epochs_trained']}")


print()
# hydroPowerModel.forward()
print("Prediction of AnnualProduction for BCR of 0.5")
print("Using LinearRegression.predict:")
# print()
print(hydroPowerModel.predict(np.array([0.5])))
print()
print("Using LinearRegression.forward:")
print(hydroPowerModel.forward(torch.Tensor([0.5])))

hydroPowerModel = hydroPowerModel.fit(BCRdata.to_numpy(), APdata.to_numpy(), X_test=BCRdata.to_numpy(), y_test=APdata.to_numpy())

print("Plots")

hydroPowerModel.analysis_plot()