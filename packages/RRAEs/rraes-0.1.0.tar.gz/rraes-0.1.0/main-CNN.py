""" Example script to train an RRAE with CNN encoder/decoder on images. """
import RRAEs.config # Include this in all your scripts
from RRAEs.AE_classes import *
from RRAEs.training_classes import RRAE_Trainor_class
import jax.random as jrandom
from RRAEs.utilities import get_data

if __name__ == "__main__":
    # Step 1: Get the data - replace this with your own data of the same shape.
    problem = "2d_gaussian_shift_scale"

    (
        x_train,
        x_test,
        p_train,
        p_test,
        y_train,
        y_test,
        pre_func_inp,
        pre_func_out,
        kwargs,
    ) = get_data(problem, train_size=10, test_size=1,)

    # C is channels, D0 is width, D1 is height, and Ntr is the number of training samples.
    print(f"Shape of data is {x_train.shape} (C x D0 x D1 x Ntr).")

    # Step 2: Specify the model to use, Strong_RRAE_CNN is ours (recommended).
    method = "RRAE"

    model_cls = RRAE_CNN

    loss_type = "RRAE"  # Specify the loss type, according to the model chosen.

    # Step 3: Specify the archietectures' parameters:
    latent_size = 200  # latent space dimension
    k_max = 64  # number of features in the latent space (after the truncated SVD).
    
    # Step 4: Define your trainor, with the model, data, and parameters.
    # Use RRAE_Trainor_class for the Strong RRAEs, and Trainor_class for other architetures.
    trainor = RRAE_Trainor_class(
        x_train,
        model_cls,
        latent_size=latent_size,
        height=x_train.shape[1],
        width=x_train.shape[2],
        channels=x_train.shape[0],
        k_max=k_max,
        folder=f"{problem}",
        file=f"{method}_{problem}_test.pkl",
        norm_in="None",
        norm_out="None",
        out_train=x_train,
        kwargs_enc={
            "width_CNNs": [32, 64, 128],
            "kernel_conv": 3,
            "stride": 2,
            "padding": 1,
        },
        kwargs_dec={
            "width_CNNs": [32, 8],
            "kernel_conv": 3,
            "stride": 2,
            "padding": 1,
            # "final_activation": lambda x: jnn.sigmoid(x), # x of shape (C, D, D)
        },
        key=jrandom.PRNGKey(500),
    )

    # Step 5: Define the kw arguments for training. When using the Strong RRAE formulation,
    # you need to specify training kw arguments (first stage of training with SVD to
    # find the basis), and fine-tuning kw arguments (second stage of training with the
    # basis found in the first stage).
    training_kwargs = {
        "step_st": [2, 2],  # Increase those to train well
        "batch_size_st": [64, 64],
        "lr_st": [1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8],
        "print_every": 1,
        # "save_every": 789,
        "loss_type": loss_type,
        "save_losses": True # if you want to save losses to plot them later
    }

    ft_kwargs = {
        "step_st": [0], # Increase if you want to fine tune
        "batch_size_st": [20],
        "lr_st": [1e-4, 1e-6, 1e-7, 1e-8],
        "print_every": 100,
        # "save_every": 50,
    }

    # Step 6: Train the model and get the predictions.
    trainor.fit(
        x_train,
        y_train,
        training_key=jrandom.key(50),
        training_kwargs=training_kwargs,
        ft_kwargs=ft_kwargs,
        pre_func_inp=pre_func_inp,
        pre_func_out=pre_func_out,
    )

    # NOTE: the code does not overwrite the loss files, it gives every new file
    # an index (e.g. all_losses_0, all_losses_1, etc.), if you run the model
    # multiple times without deleting the loss file, consider changing idx
    # below to specify the file of which training you want to plot
    # trainor.plot_training_losses(idx=0) # to plot both training and validation losses

    preds = trainor.evaluate(
        x_train, y_train, x_test, y_test, None, pre_func_inp, pre_func_out
    )
    # NOTE: preds are not saved so uncomment last line if you want to save/plot etc.

    trainor.save_model(kwargs=kwargs)

    # Uncomment the following line if you want to hold the session to check your
    # results in the console.
    # pdb.set_trace()
