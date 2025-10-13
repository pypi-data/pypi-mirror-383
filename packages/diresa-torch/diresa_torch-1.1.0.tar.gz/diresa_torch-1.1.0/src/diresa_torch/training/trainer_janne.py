import torch
from typing import Literal, Optional, Dict, overload
import logging
from torch.utils.data import DataLoader
from diresa_torch.arch.models import Diresa
from operator import add
from copy import deepcopy


def __compute_losses(outputs, targets, criteria, loss_weights):
    """
    Helper function to compute losses given outputs, targets, criteria and weights.

    :param outputs: Model outputs (tuple of 3 elements: reconstructed, latent, distance)
    :param targets: Target values (tuple of 3 elements: data, None, None)
    :param criteria: List of loss functions [ReconstructionLoss, CovarianceLoss, DistanceLoss]
    :param loss_weights: Weighting factor for the different losses
    :return: Tuple of (individual_losses, total_weighted_loss)
    """
    individual_losses = [c(o, t) for c, o, t in zip(criteria, outputs, targets)]
    weighted_losses = [w * l for w, l in zip(loss_weights, individual_losses)]
    total_weighted_loss = torch.stack(weighted_losses).sum()

    return individual_losses, total_weighted_loss


def __set_non_trainable(model):
    for param in model.parameters():
        param.requires_grad = False


def __loss_string_repr(criteria, suffix=""):
    """
    Helper functions producing string criteria of
    losses. String repr is used to log each loss with an
    understandable name.
    """
    # Ordering of loss ouput values
    # Use class name without the last () as name for the loss
    loss_names = [f"{c}"[:-2] for c in criteria] + ["WeightedLoss"]

    # Criteria list can change depending on training mode.
    # When runing normal criteria[0] is Reconstruction loss (and len(criteria == 3))
    # During staged training, when encoder is trained
    # criteria[0] is LatentCovLoss (and len(criteria == 2)).
    # When decoder is is trained criteria[0] is Recon (and len(criteria == 1))
    if len(criteria) == 3 or len(criteria) == 1:
        loss_names[0] = "Recon" + loss_names[0]

    # add "train" suffix for output
    loss_names = list(map(lambda x: x + suffix, loss_names))
    return loss_names


def __evaluate(
    produce_output: callable,
    produce_target: callable,
    test_loader: DataLoader,
    criteria: list,
    device: torch.device,  # device is still required here as this function does not have access to model
    loss_weights: list = [1.0, 1.0, 1.0],
    loss_suffix: str = "_eval",
) -> Dict[str, float]:
    """
    Evaluate DIRESA (does not track gradient) by computing all three losses (reconstruction, covariance, distance) with help of the ``produce_output`` and ``produce_input`` functions. Those functions are provided as lambdas which makes it easier to match the outputs, targets and criteria together for evaluation purposes.

    :param produce_output: callable function producing outputs from model. Takes as input batch data.
    :param produce_target: callable function producing target values for criterion. Takes as input batch data.
    :param test_loader: Test data loader
    :param criteria: List of loss functions, depends on what part is being evaluated.
    :param device: Device to evaluate on
    :param loss_weights: Weighting factor for the different losses (in order [Reconstruction, Covariance, Distance])
    :param suffix: Appends a suffix to the loss as __eval can be used for validation during training or evaluation (when passing in test set)

    :return: Dictionary with average losses: individual losses + weighted total loss
    """
    total_losses = [0.0] * (len(criteria) + 1)
    num_batches = 0

    loss_names = __loss_string_repr(criteria, loss_suffix)

    with torch.no_grad():
        for _, data in enumerate(test_loader):
            data = data.to(device)

            outputs = produce_output(data)

            targets = produce_target(data)

            # outputs_losses, loss = _compute_losses(outputs, target, criteria, loss_weights)
            outputs_losses, loss = __compute_losses(
                outputs, targets, criteria, loss_weights
            )

            # Accumulate losses
            all_losses = outputs_losses + [loss]
            total_losses = list(
                map(add, total_losses, [loss.item() for loss in all_losses])
            )
            num_batches += 1

    avg_losses = [loss / num_batches for loss in total_losses]

    result = {name: avg_loss for name, avg_loss in zip(loss_names, avg_losses)}

    return result


def train_diresa(
    model: Diresa,
    train_loader: DataLoader,
    criteria: list,
    optimizer: torch.optim.Optimizer,
    num_epochs: int = 10,
    val_loader: Optional[DataLoader] = None,
    callbacks: Optional[list] = None,  # Not IMPL at the moment
    loss_weights: list = [1.0, 1.0, 1.0],
    staged_training: bool = False,
) -> dict[str, dict[str, list[float]]]:
    """
    Trains `model`. Needs to provide multiple loss function in order to train de different parts of the model.
    CovarianceLoss and DistanceLoss are used to produce an interpretable latent space
    while ReconstructionLoss is used to produce an output.
    Reconstruction loss is also used for the ordering of latent components (De Paepe, 2025, Appendix D).

    :param model: The model to train
    :param train_loader: Training data loader
    :param criterion: List of Loss function. With order [ReconstructionLoss, CovarianceLoss, DistanceLoss]
    :param optimizer: Optimizer
    :param num_epochs: Number of epochs
    :param val_loader: Optional validation loader
    :param callbacks: Optional list of callback functions
    :param loss_weights: Weighting factor for the different losses. With order [ReconstructionLoss, CovarianceLoss, DistanceLoss]
    :param staged_trainig: If set to True will train the encoder and the decoder separately for ``num_epochs`` each.

    :return Dict with training (losses, metrics) and validation (if val_loader is provided).
    """
    assert (
        callbacks is None
    ), "Callbacks are not tested at the moment. Remove param or set to None"

    def __train_for_epochs(
        produce_output: callable,
        produce_target: callable,
        criteria,
        loss_weights,
        device,
        prepend_log="DIRESA",
    ):
        """
        Nested function for training loop. Factors out common functionalities for training,
        while providing custom informations about what loss to train for used to differentiate
        between staged training and full training.

        :param produce_output: callable function producing outputs from model. Takes as input batch data.
        :param produce_target: callable function producing target values for criterion. Takes as input batch data.
        :param criteria: List of loss functions
        :param loss_weights: weights for each loss function
        :param device: hardware device used.
        :param prepend_log: String to prepend to logging output
        """
        assert len(criteria) == len(
            loss_weights
        ), "Number of criteria and their associated weights does not match"

        loss_names = __loss_string_repr(criteria, "_train")
        history = {name: [] for name in loss_names}

        for epoch in range(num_epochs):
            # each criterion loss + combined weighted loss
            epoch_loss = [0.0] * (len(criteria) + 1)
            num_batches = 0

            for _, data in enumerate(train_loader):
                data = data.to(device)
                target = produce_target(data)
                outputs = produce_output(data)

                optimizer.zero_grad()
                outputs_losses, loss = __compute_losses(
                    outputs, target, criteria, loss_weights
                )

                # accumulates gradient in each tensor -> Backprop
                # backpropagated loss in weighted sum of each loss.
                loss.backward()

                optimizer.step()

                # add weighted loss to final losses
                all_losses = outputs_losses + [loss]
                epoch_loss = list(
                    map(add, epoch_loss, [loss.item() for loss in all_losses])
                )
                num_batches += 1

                if callbacks:
                    raise NotImplementedError
                    # for callback in callbacks:
                    #     callback(epoch, batch_idx, loss.item())

            avg_loss = list(map(lambda loss: loss / num_batches, epoch_loss))

            for name, loss in zip(loss_names, avg_loss):
                history[name].append(loss)

            # val loader is defined in exterior function
            if val_loader:
                val_dict = __evaluate(
                    produce_output,
                    produce_target,
                    val_loader,
                    criteria,
                    device,
                    loss_weights,
                    loss_suffix="_val",
                )
                for name, loss in val_dict.items():
                    if name in history:
                        history[name].append(loss)
                    else:
                        history[name] = [loss]

            # print out last entry in history for each epoch
            log_str = ", ".join(
                [f"{name}: {values[-1]:.4e}" for name, values in history.items()]
            )
            logging.info(f"{prepend_log}: Epoch {epoch + 1}/{num_epochs} - {log_str}")

        return history

    # End of nested function

    # takes the device onto which the first tensor is registered
    device = next(model.parameters()).device

    if staged_training:
        # train encoder, cov and dist loss
        hist_encoder = __train_for_epochs(
            produce_output=lambda data: model._encode_with_distance(data.x),
            produce_target=lambda _: (None, None),
            criteria=criteria[1:],  # cov and dist criteria
            loss_weights=loss_weights[1:],  # cov and dist weights
            device=device,
            prepend_log="Encoder",
        )

        # freeze encoder weights
        __set_non_trainable(model.base_encoder)

        # train decoder, only rec loss
        hist_decoder = __train_for_epochs(
            produce_output=lambda data: model.base_decoder(model.base_encoder(data.x)),
            produce_target=lambda data: data.y,
            criteria=criteria[:1],
            loss_weights=loss_weights[:1],
            device=device,
            prepend_log="Decoder",
        )

        hist = {"Encoder": hist_encoder, "Decoder": hist_decoder}
        return hist

    else:
        # data is produced by forward pass of model.
        hist_diresa = __train_for_epochs(
            lambda data: model(data.x),
            lambda data: (data.y, None, None),
            criteria,
            loss_weights,
            device=device,
            prepend_log="Encoder_Decoder",
        )

        # To keep consitency with staged training where encoder
        # and decoder losses are accessed via a key, the same is done
        # when all weights are trained simultaneously.
        hist = {"Encoder_Decoder": hist_diresa}
        return hist


def evaluate_diresa(
    model: Diresa,
    test_loader: DataLoader,
    criteria: list,
    loss_weights: list = [1.0, 1.0, 1.0],
) -> Dict[str, float]:
    """
    Evaluates `model` using `test_loader`

    :param produce_output: callable function producing outputs from model. Takes as input batch data.
    :param produce_target: callable function producing target values for criterion. Takes as input batch data.
    :param test_loader: Test data loader
    :param criteria: List of loss functions [ReconstructionLoss, CovarianceLoss, DistanceLoss]
    :param loss_weights: Weighting factor for the different losses

    :return: Dictionary with averaged losses: individual criterion loss + weighted total loss
    """
    assert (
        len(criteria) == 3
    ), "Need to provide 3 criteria for DIRESA evaluation, namely [ReconstructionLoss, CovarianceLoss, DistanceLoss]"

    device: torch.device = next(model.parameters()).device

    eval_dict = __evaluate(
        # model.forward(data) produces (reconstruced, latent, dist)
        lambda data: model.forward(data.x),
        lambda data: (data.y, None, None),
        test_loader=test_loader,
        device=device,
        criteria=criteria,
        loss_weights=loss_weights,
        loss_suffix="_eval",
    )
    log_str = ", ".join([f"{name}: {value:.4e}" for name, value in eval_dict.items()])
    logging.info(log_str)
    return eval_dict


def predict_diresa(model: Diresa, data_loader: DataLoader) -> torch.Tensor:
    """
    predict_diresa is the reconstructed dataset from `data_loader` passed through `model`.
    Provides faster inference as distance and covariance are not computed for inference.

    :param model: model to use to produce a prediction
    :param data_loader: data to be reconstructed.
    """

    device = next(model.parameters()).device

    predictions = []

    with torch.no_grad():
        for _, data in enumerate(data_loader):
            data = data.to(device)
            outputs = model.fast_eval(data.x)
            predictions.append(outputs.cpu())

    return torch.cat(predictions, dim=0)


def __set_components_to_mean(latent: torch.Tensor, retain_idx: int):
    """
    Sets all latent components to mean except the ones in the list (which are kept untouched)

    :param latent: latent dataset
    :param retain: components not in this list are set to mean
    :return: latent dataset with all components set to mean except the ones in the list
    """

    with torch.no_grad():
        mean_values = latent.mean(dim=0, keepdim=True)
        mask = torch.tensor(
            [i != retain_idx for i in range(latent.shape[1])],
            dtype=torch.bool,
            device=latent.device,
        )
        result = torch.where(mask, mean_values, latent)
    return result


def __r2_score(y: torch.Tensor, y_pred: torch.Tensor):
    """
    :param y: original dataset
    :param y_pred: predicted dataset
    :return: R2 score between y and y_pred
    """
    error = torch.sum(torch.square(y - y_pred))
    var = torch.sum(torch.square(y - torch.mean(y, dim=0)))
    r2 = 1.0 - error / var
    return r2.item()  # Convert to Python scalar


# # TODO: Should move this to another file called types.py
# # As order_diresa either returns an new object or None, in order
# # to help the type checker we provide type hints.
@overload
def order_diresa(
    model: Diresa, data_loader: DataLoader, *, inplace: Literal[True]
) -> None: ...


# need one overload for when we use the default (inplace is not provided meaning it is set to true)
@overload
def order_diresa(model: Diresa, data_loader: DataLoader) -> None: ...


@overload
def order_diresa(
    model: Diresa, data_loader: DataLoader, *, inplace: Literal[False]
) -> Diresa: ...


# NOTE: Could rewrite all map functions using tensor operations or numpy instead of python builtin sequence operations
# NOTE: Return type is set to None when ordering change is made in place (i.e. changed
# directly in the model passed as reference).
def order_diresa(model: Diresa, data_loader: DataLoader, inplace=True):
    """
    Sets ordering of the OrderingLayer.
    Limitations: assumes a flat latent space (rank of latent is 2).

    By default will set ordering in place in the provided model and return None.
    If `inplace` is set to false will return a new model for which the ordering has been set while leaving the original model passed as a parameter untouched.


    :param model: The model on which to produce the ordering
    :param data_loader: The data_loader from which to produce the ordering
    :param inplace: If true returns a copy of the diresa object with new ordering, leaving the model passed as parameter untouched
    """
    r2_scores = []

    logging.info(f"Batch size for ordering is {data_loader.batch_size}")

    device = next(model.parameters()).device

    with torch.no_grad():
        # produce r2 per batch
        for _, data in enumerate(data_loader):
            data = data.to(device)
            # NOTE: Might need to encapsulate ordering in
            # a function working by batch for testing.
            latent = model.base_encoder(data.x)
            assert len(latent.shape) == 2, "Latent space is not flattend"

            # 2. Produce l latent samples for wich every latent dimensions is averaged except the l-th one.
            averaged = map(
                lambda i: __set_components_to_mean(latent, i),
                range(latent.shape[1]),
            )

            # 3. Produce l decoded samples from l latent samples
            decoded = map(lambda latent: model.base_decoder(latent), averaged)

            # 4. Compute R2 by comparing l decoded with orginal x
            r2 = list(map(lambda pred: __r2_score(data.y, pred), decoded))

            r2_scores.append(r2)

        r2_scores = torch.tensor(r2_scores, device=device).mean(dim=0)

        logging.info(
            f"Ordered R2 scores are: {list(map(lambda x: x.item(), sorted(r2_scores, reverse=True)))}"
        )

        ordering = torch.argsort(r2_scores, descending=True)

        if inplace:
            model.ordering_layer.order = ordering
            return None
        else:
            new_model: Diresa = deepcopy(model)
            new_model.ordering_layer.order = ordering
            return new_model
