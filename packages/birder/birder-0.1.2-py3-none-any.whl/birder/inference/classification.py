import sys
from collections.abc import Callable
from collections.abc import Iterator
from typing import Any
from typing import Literal
from typing import Optional
from typing import overload

import numpy as np
import numpy.typing as npt
import torch
import torch.amp
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader
from torchvision.transforms import v2
from torchvision.transforms.v2.functional import five_crop
from tqdm import tqdm

from birder.results.classification import Results
from birder.results.classification import SparseResults


def infer_image(
    net: torch.nn.Module | torch.ScriptModule,
    sample: Image.Image | str,
    transform: Callable[..., torch.Tensor],
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    device: Optional[torch.device] = None,
    **kwargs: Any,
) -> tuple[npt.NDArray[np.float32], Optional[npt.NDArray[np.float32]]]:
    """
    Perform inference on a single image

    This convenience function allows for quick, one-off classification of an image.

    Raises
    ------
    TypeError
        If the sample is neither a string nor a PIL Image object.
    """

    image: Image.Image
    if isinstance(sample, str):
        image = Image.open(sample)
    elif isinstance(sample, Image.Image):
        image = sample
    else:
        raise TypeError("Unknown sample type")

    if device is None:
        device = torch.device("cpu")

    input_tensor = transform(image).unsqueeze(dim=0).to(device)
    return infer_batch(
        net, input_tensor, return_embedding=return_embedding, tta=tta, return_logits=return_logits, **kwargs
    )


def infer_batch(
    net: torch.nn.Module | torch.ScriptModule,
    inputs: torch.Tensor,
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    **kwargs: Any,
) -> tuple[npt.NDArray[np.float32], Optional[npt.NDArray[np.float32]]]:
    embedding: Optional[npt.NDArray[np.float32]] = None
    if return_embedding is True:
        embedding_tensor: torch.Tensor = net.embedding(inputs, **kwargs)
        logits = net.classify(embedding_tensor)
        out = logits if return_logits is True else F.softmax(logits, dim=1)
        embedding = embedding_tensor.cpu().float().numpy()

    elif tta is True:
        (_, _, H, W) = inputs.size()
        crop_h = int(H * 0.8)
        crop_w = int(W * 0.8)
        tta_inputs = five_crop(inputs, size=[crop_h, crop_w])
        t = v2.Resize((H, W), interpolation=v2.InterpolationMode.BICUBIC, antialias=True)
        outs = []
        for tta_input in tta_inputs:
            logits = net(t(tta_input), **kwargs)
            outs.append(logits if return_logits is True else F.softmax(logits, dim=1))

        out = torch.stack(outs).mean(axis=0)

    else:
        logits = net(inputs, **kwargs)
        out = logits if return_logits is True else F.softmax(logits, dim=1)

    return (out.cpu().float().numpy(), embedding)


DataloaderInferenceResult = tuple[list[str], npt.NDArray[np.float32], list[int], list[npt.NDArray[np.float32]]]


# pylint: disable=too-many-locals
def infer_dataloader_iter(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    batch_callback: Optional[Callable[[list[str], npt.NDArray[np.float32], list[int]], None]] = None,
    chunk_size: Optional[float] = None,
    **kwargs: Any,
) -> Iterator[DataloaderInferenceResult]:
    """
    See infer_dataloader for full documentation.

    This function yields results in chunks and is used by infer_dataloader to
    implement both its chunked and non-chunked behavior.
    """

    if chunk_size is None:
        chunk_size = float("inf")

    net.to(device, dtype=model_dtype)
    embedding_list: list[npt.NDArray[np.float32]] = []
    out_list: list[npt.NDArray[np.float32]] = []
    labels: list[int] = []
    sample_paths: list[str] = []
    sample_count = 0
    with tqdm(total=num_samples, initial=0, unit="images", unit_scale=True, leave=False) as progress:
        for file_paths, inputs, targets in dataloader:
            batch_size = inputs.size(0)

            # Inference
            inputs = inputs.to(device, dtype=model_dtype)

            with torch.amp.autocast(device.type, enabled=amp, dtype=amp_dtype):
                (out, embedding) = infer_batch(
                    net, inputs, return_embedding=return_embedding, tta=tta, return_logits=return_logits, **kwargs
                )

            out_list.append(out)
            if embedding is not None:
                embedding_list.append(embedding)

            # Set labels and sample list
            batch_labels = list(targets.cpu().numpy())
            labels.extend(batch_labels)
            sample_paths.extend(file_paths)

            if batch_callback is not None:
                batch_callback(file_paths, out, batch_labels)

            # Update progress bar
            progress.update(n=batch_size)

            # Yield results when we reach chunk_size
            sample_count += batch_size
            if sample_count >= chunk_size:
                with tqdm.external_write_mode(file=sys.stderr):
                    yield (sample_paths, np.concatenate(out_list, axis=0), labels, embedding_list)

                # Reset for next chunk
                embedding_list = []
                out_list = []
                labels = []
                sample_paths = []
                sample_count = 0

    if len(out_list) > 0:
        yield (sample_paths, np.concatenate(out_list, axis=0), labels, embedding_list)


@overload
def infer_dataloader(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    batch_callback: Optional[Callable[[list[str], npt.NDArray[np.float32], list[int]], None]] = None,
    chunk_size: None = None,
    **kwargs: Any,
) -> DataloaderInferenceResult: ...


@overload
def infer_dataloader(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    batch_callback: Optional[Callable[[list[str], npt.NDArray[np.float32], list[int]], None]] = None,
    chunk_size: int = 0,
    **kwargs: Any,
) -> Iterator[DataloaderInferenceResult]: ...


def infer_dataloader(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    return_embedding: bool = False,
    tta: bool = False,
    return_logits: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    batch_callback: Optional[Callable[[list[str], npt.NDArray[np.float32], list[int]], None]] = None,
    chunk_size: Optional[int] = None,
    **kwargs: Any,
) -> Iterator[DataloaderInferenceResult] | DataloaderInferenceResult:
    """
    Perform inference on a DataLoader using a given neural network.

    This function runs inference on a dataset provided through a DataLoader,
    optionally returning embeddings and using mixed precision (amp).

    The function has two modes of operation:
    1. Return all results at once (when chunk_size is None)
    2. Yield results in chunks (when chunk_size is an integer)

    Parameters
    ----------
    device
        The device to run the inference on.
    net
        The model to use for inference.
    dataloader
        The DataLoader containing the dataset to perform inference on.
    return_embedding
        Whether to return embeddings along with the outputs.
    tta
        Run inference with oversampling.
    return_logits
        If True, the raw logits from the model's final layer will be returned
        instead of probabilities after a softmax operation.
    model_dtype
        The base dtype to use.
    amp
        Whether to use automatic mixed precision.
    amp_dtype
        The mixed precision dtype.
    num_samples
        The total number of samples in the dataloader.
    batch_callback
        A function to be called after each batch is processed. If provided, it
        should accept three arguments:
        - list[str]: A list of file paths for the current batch
        - npt.NDArray[np.float32]: The output array for the current batch
        - list[int]: A list of labels for the current batch
    chunk_size
        Number of samples to process before yielding results. If None, the function
        will return all results at once. If an integer, the function will yield
        results after processing approximately that many samples.
    kwargs
        Keyword arguments to pass to the model forward or embedding functions.

    Returns
    -------
    When chunk_size is None:
        A tuple containing four elements:
        - list[str]: A list of all processed file paths.
        - npt.NDArray[np.float32]: A 2D numpy array of all outputs.
        - list[int]: A list of all labels.
        - list[npt.NDArray[np.float32]]: A list of embedding arrays if
            return_embedding is True, otherwise an empty list.

    When chunk_size is an integer:
        An iterator that yields tuples, each containing:
        - list[str]: A list of file paths for the current chunk.
        - npt.NDArray[np.float32]: A 2D numpy array of outputs for the current chunk.
        - list[int]: A list of labels for the current chunk.
        - list[npt.NDArray[np.float32]]: A list of embedding arrays for the current chunk if
          return_embedding is True, otherwise an empty list.

    Examples
    --------
    Example 1: Get all results at once

    >>> device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    >>> model = YourNeuralNetwork().to(device)
    >>> test_dataset = YourDataset(data_dir='path/to/test/data')
    >>> test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    >>>
    >>> # Process all samples and get final results
    >>> file_paths, outputs, labels, embeddings = infer_dataloader(
    ...     device=device,
    ...     net=model,
    ...     dataloader=test_loader,
    ...     return_embedding=True,
    ...     num_samples=len(test_dataset),
    ... )
    >>> print(f"Processed {len(file_paths)} files")
    >>> print(f"Output shape: {outputs.shape}")

    Example 2: Process in chunks

    >>> # Process in chunks of 128 samples
    >>> results_iterator = infer_dataloader(
    ...     device=device,
    ...     net=model,
    ...     dataloader=test_loader,
    ...     chunk_size=128,
    ... )
    >>>
    >>> # Process each chunk as it becomes available
    >>> for chunk_paths, chunk_outputs, chunk_labels, chunk_embeddings in results_iterator:
    ...     # Do something with each chunk

    Notes
    -----
    - The function uses a progress bar (tqdm) to show the inference progress.
    - If 'num_samples' is not provided, the progress bar may not accurately
      reflect the total number of samples processed.
    - The batch_callback, if provided, is called after each batch is processed,
      allowing for real-time analysis or logging of results.
    """

    result_iter = infer_dataloader_iter(
        device,
        net,
        dataloader,
        return_embedding,
        tta,
        return_logits,
        model_dtype,
        amp,
        amp_dtype,
        num_samples,
        batch_callback,
        chunk_size,
        **kwargs,
    )
    if chunk_size is None:
        return next(result_iter)

    return result_iter


@overload
def evaluate(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    class_to_idx: dict[str, int],
    tta: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    sparse: Literal[False] = False,
) -> Results: ...


@overload
def evaluate(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    class_to_idx: dict[str, int],
    tta: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    sparse: Literal[True] = True,
) -> SparseResults: ...


def evaluate(
    device: torch.device,
    net: torch.nn.Module | torch.ScriptModule,
    dataloader: DataLoader,
    class_to_idx: dict[str, int],
    tta: bool = False,
    model_dtype: torch.dtype = torch.float32,
    amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    num_samples: Optional[int] = None,
    sparse: bool = False,
) -> Results | SparseResults:
    (sample_paths, outs, labels, _) = infer_dataloader(
        device, net, dataloader, tta=tta, model_dtype=model_dtype, amp=amp, amp_dtype=amp_dtype, num_samples=num_samples
    )
    if sparse is True:
        return SparseResults(sample_paths, labels, list(class_to_idx.keys()), outs)

    return Results(sample_paths, labels, list(class_to_idx.keys()), outs)
