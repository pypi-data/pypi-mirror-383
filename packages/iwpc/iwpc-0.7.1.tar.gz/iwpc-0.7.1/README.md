# IWPC #

This package implements the methods described in the research paper https://arxiv.org/abs/2405.06397 for estimating a 
lower bound on the divergence between any two distributions, p and q, using samples from each distribution.

Install using `pip install iwpc`

The machine learning code in this package is organised using the fantastic [PyTorch Lightning](https://lightning.ai/docs/pytorch/stable/)
package. Some familiarity with the structure of lightning is recommended.

The plots shown in the [original divergences paper](https://arxiv.org/abs/2405.06397) may be reproduced by running [parity_example.py](examples%2Fparity_example.py)

# Basic Usage #

The most basic usage of this package is for calculating an estimator for a lower bound on an f-divergence (such as the 
KL-divergence) between two distribution, p and q. Each example below assumes one is provided with a set of samples from
drawn from distribution p and from distribution q labelled 0 and 1 respectively.

## [calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py) ##

The example script [continuous_example_2D.py](examples%2Fcontinuous_example_2D.py) shows the most basic usage of the [calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py) function
run on the components of 2D vectors drawn from the distribution `N(r | 1.0, 0.1) * (1 + eps * cos(theta)) / 2 / pi` for
the two values `eps = 0.` and `eps = 0.2`. The script shows how to calculate estimates for lower bounds on both the Kullback-Leibler
divergence and the Jensen-Shannon divergence between the two distributions and compares these to numerically integrated
values. At the most basic level, all [calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py) requires is a [LightningDataModule](https://lightning.ai/docs/pytorch/stable/data/datamodule.html), in this case an
instance of [BinaryPandasDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_data_module.py), to provide the data and an instance of [FDivergenceEstimator](src%2Fiwpc%2Fmodules%2Ffdivergence_base.py), in this case an
instance of [GenericNaiveVariationalFDivergenceEstimator](src%2Fiwpc%2Fmodules%2Fnaive.py), to provide the machine learning model.

### [BinaryPandasDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_data_module.py) ###

Given two Pandas data frames containing the samples from p and q, the [BinaryPandasDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_data_module.py) class provides a
convenient wrapper that casts the data into the form expected by [calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py). In addition to the two 
dataframes, the [BinaryPandasDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_data_module.py) requires the user to specify which features columns to use, the two
cartesian components 'x' and 'y' in this case, as well as the name of a weight column if one exists. By default, all
data modules in this package provide a 50-50 train-validation split.

### [GenericNaiveVariationalFDivergenceEstimator](src%2Fiwpc%2Fmodules%2Fnaive.py) ###

For generic data without any specific structures to inspire the topology of the machine learning model, the [LightningModule](https://lightning.ai/docs/pytorch/stable/common/lightning_module.html)
subclass [GenericNaiveVariationalFDivergenceEstimator](src%2Fiwpc%2Fmodules%2Fnaive.py) provides a generic N to 1 dimensional
function approximator needed for the divergence calculation. The only information required is the number of training 
features and a [DifferentiableFDivergence](src%2Fiwpc%2Fdivergences%2Fbase.py) instance to tell the module which divergence to calculate.

### Output ###

The calculate_divergence trains the provided LightningDataModule while logging, by default, to a `lightning_logs` directory 
placed into the same directory as the main script. A subdirectory is created inside the `lightning_logs` directory each time the
[calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py) function is run which contains the training results, logs,
and model checkpoints for the given run. The progress of the training may be monitored in your browser using
`tensorboard --logdir .../lightning_logs`. [calculate_divergence](src%2Fiwpc%2Fcalculate_divergence.py) returns an
instance of [DivergenceResult](src%2Fiwpc%2Fcalculate_divergence.py) which contains the final divergence lower bound estimate, 
its error, as well as the best version of the trained model and some other useful properties.

The script renders these results as a function of the number of samples provided in two plots:

![KL-divergence-sample-size.png](images%2FKL-divergence-sample-size.png)

## [run_reweight_loop](src%2Fiwpc%2Freweight_loop.py) ##

The example script [example_reweight_loop.py](examples%2Fexample_reweight_loop.py) shows a more sophisticated
implementation of the divergence framework. Typically, datasets are too large to fit into memory at once and so
complicated that machine learning models tend to get caught up in local minima when training. To alleviate these two
problems this script demonstrates the usage of [PandasDirDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_directory_data_module.py)
for splitting datasets up into manageable chunks dynamically loaded into memory, and the [run_reweight_loop](src%2Fiwpc%2Freweight_loop.py)
function that iteratively reweights the data when training stagnates and restarts training afresh to allow the network
to focus on other features. The data in this example was drawn from the same distribution as the previous example, so
the reweight loop is most certainly overkill for the given data complexity, however the reweighting procedure has been
very useful within our own work with significantly more complicated data.

### [PandasDirDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_directory_data_module.py) ###

The [PandasDirDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_directory_data_module.py) class provides an extremely
generic implementation of a dataset which is stored on disk in separate pickle files containing Pandas dataframes that
are automatically and efficiently loaded into memory as needed. See the [PandasDirDataModule](src%2Fiwpc%2Fdata_modules%2Fpandas_directory_data_module.py)
docstring for more information. This DataModule is recommended, even when working with smaller datasets, as the data is
stored in a convenient portable form with relevant metadata.

### [BinnedDfAccumulator](src%2Fiwpc%2Faccumulators%2Fbinned_Df_accumulator.py) ###

Once trained to find a difference between p and q, the natural question becomes, _how exactly is the machine learning 
model telling the two distributions apart_. This is an extremely important question as the conclusion that some difference
exists is typically uninformative, as the network is free to pick up on **any** differences between p and q, including
those we might deem uninteresting. The [BinnedDfAccumulator](src%2Fiwpc%2Faccumulators%2Fbinned_Df_accumulator.py) class assists in this process by calculating the 
degree to which the obtained degree of divergence can be explained by the marginal distribution in a given set of
variables alone, as well as how the degree of divergence changes as a function of these values. Although the 
[BinnedDfAccumulator](src%2Fiwpc%2Faccumulators%2Fbinned_Df_accumulator.py) is generically written for any number of dimensions, the plotting features are only
implemented in 1D and 2D currently. As a result, the examples given in [example_reweight_loop.py](examples%2Fexample_reweight_loop.py) are 1D and 2D.

The first plot below shows how the divergence behaves as a function of the radius, r, of the samples. For 1D plots, the
top left plot shows the (weighted) distribution of the variable in the validation dataset. Since the radius of the
samples from p and q were drawn from the same gaussian, these two histograms unsurprisingly show no signs of
disagreement and the estimated divergence in r alone is consistent with 0. The top right plot shows an estimate, derived
from the same network trained in the reweight loop, of the divergence of the distributions of the samples which landed
within each bin. In this case, since the only other variable orthogonal to r is theta, this amounts to the divergence in
the theta distributions at each fixed value of r. This plot suggests that the divergence is constant as a function of r,
once again unsurprising given the form of p and q.

![divergence_vs_r.png](images%2Fdivergence_vs_r.png)

The source of the divergence is obvious in the theta plots below. The estimate of the marginalised divergence
(ie the divergence attributable to the theta distribution alone) is consistent with the global divergence, confirming
this to be the only source of divergence between p and q. This is also clearly visible in the top right as the divergence
conditioned on theta is consistent with 0 in all cases. The bottom left and bottom right plots confirm that the network
has in fact learnt the features in the data. The full explanation of how these plots are calculated is a little involved,
but suffice to say, they demonstrate the ways in which the network believes the distributions look in the given variable.
The error bars on the 'learned' quantities indicate uncertainty on how well we are able to reconstruct what the network
believes the distribution to be. These should not be interpreted as error-bars indicating how far the truth may be from
what the network has learnt, and these 'learned' quantities may well demonstrate hallucinations.

![divergence_vs_theta.png](images%2Fdivergence_vs_theta.png)

The 2D plot in theta and r is mostly redundant in this case, but we can clearly see many of the features discussed in 
the 1D plots. Top left shows the ratio of the two distributions in validation. Top right shows the divergence within
each bin. Bottom left shows an estimate for what the net believes the ratio of the two distributions is, and
the bottom right is simple a histogram of the p distribution in the validation dataset.

![divergence_vs_r_theta.png](images%2Fdivergence_vs_r_theta.png)

# Other Utilities

## Encoding layers

See [Encoding](src%2Fiwpc%2Fencodings%2Fencoding_base.py) docstring.

TODO: Elaborate

## Multidimensional Function Visualisers

See [MultidimensionalFunctionVisualiser](src%2Fiwpc%2Fvisualise%2Fmultidimensional_function_visualiser.py) docstring and [multidimensional_function_visualiser_example.py](examples%2Fmultidimensional_function_visualiser_example.py).
Multidimensional function visualisers are extremely useful for verifying the output of a learnt function which is typically high-dimensional.

TODO: Elaborate

# Help and Suggestions #

For any suggestions or questions please reach out to [Jeremy J. H. Wilkinson](mailto:jero.wilkinson@gmail.com).

If this tool has been helpful in your research, please consider citing https://arxiv.org/abs/2405.06397.