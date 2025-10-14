#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
On-line Dynamic Time Warping
"""

import time
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import progressbar
from numpy.typing import NDArray

from matchmaker.base import OnlineAlignment
from matchmaker.dp.dtw_loop import oltw_arzt_loop
from matchmaker.features.audio import FRAME_RATE, QUEUE_TIMEOUT, WINDOW_SIZE
from matchmaker.utils import (
    CYTHONIZED_METRICS_W_ARGUMENTS,
    CYTHONIZED_METRICS_WO_ARGUMENTS,
    distances,
)
from matchmaker.utils.distances import Metric, vdist
from matchmaker.utils.misc import (
    MatchmakerInvalidOptionError,
    MatchmakerInvalidParameterTypeError,
    RECVQueue,
    set_latency_stats,
)

STEP_SIZE: int = 5
START_WINDOW_SIZE: Union[float, int] = 0.25


class OnlineTimeWarpingArzt(OnlineAlignment):
    """
    Fast On-line Time Warping

    Parameters
    ----------
    reference_features : np.ndarray
        A 2D array with dimensions (`n_timesteps`, `n_features`) containing the
        features of the reference the input is going to be aligned to.

    window_size : int
        Size of the window for searching the optimal path in the cumulative
        cost matrix.

    step_size : int
        Size of the step

    distance_func : str, tuple (str, dict) or callable
        Distance function for computing pairwise distances.

    start_window_size: int
        Size of the starting window size.

    Attributes
    ----------
    reference_features : np.ndarray
        See description above.

    window_size : int
        See description above.

    step_size : int
        See description above.

    input_features : list
        List with the input features (updates every time there is a step).

    current_position : int
        Index of the current position.

    warping_path : list
        List of tuples containing the current position and the corresponding
        index in the array of `reference_features`.

    positions : list
        List of the positions for each input.
    """

    DEFAULT_DISTANCE_FUNC: str = "Manhattan"
    distance_func: Callable[[NDArray[np.float32]], NDArray[np.float32]]
    vdist: Callable[[NDArray[np.float32]], NDArray[np.float32]]

    def __init__(
        self,
        reference_features: NDArray[np.float32],
        window_size: int = WINDOW_SIZE,
        step_size: int = STEP_SIZE,
        distance_func: Union[
            str,
            Callable,
            Tuple[str, Dict[str, Any]],
        ] = DEFAULT_DISTANCE_FUNC,
        start_window_size: int = START_WINDOW_SIZE,
        current_position: int = 0,
        frame_rate: int = FRAME_RATE,
        queue: Optional[RECVQueue] = None,
        **kwargs,
    ) -> None:
        super().__init__(reference_features=reference_features)

        self.input_features: List[NDArray[np.float32]] = None
        self.queue = queue or RECVQueue()

        if not (isinstance(distance_func, (str, tuple)) or callable(distance_func)):
            raise MatchmakerInvalidParameterTypeError(
                parameter_name="distance_func",
                required_parameter_type=(str, tuple, Callable),
                actual_parameter_type=type(distance_func),
            )

        # Set local cost function
        if isinstance(distance_func, str):
            if distance_func not in CYTHONIZED_METRICS_WO_ARGUMENTS:
                raise MatchmakerInvalidOptionError(
                    parameter_name="distance_func",
                    valid_options=CYTHONIZED_METRICS_WO_ARGUMENTS,
                    value=distance_func,
                )
            # If distance_func is a string
            self.distance_func = getattr(distances, distance_func)()

        elif isinstance(distance_func, tuple):
            if distance_func[0] not in CYTHONIZED_METRICS_W_ARGUMENTS:
                raise MatchmakerInvalidOptionError(
                    parameter_name="distance_func",
                    valid_options=CYTHONIZED_METRICS_W_ARGUMENTS,
                    value=distance_func[0],
                )
            # distance_func is a tuple with the arguments to instantiate
            # the cost
            self.distance_func = getattr(distances, distance_func[0])(
                **distance_func[1]
            )

        elif callable(distance_func):
            # If the local cost is a callable
            self.distance_func = distance_func

        # A callable to compute the distance between the rows of matrix and a vector
        if isinstance(self.distance_func, Metric):
            self.vdist = vdist
        else:
            # TODO: Speed this up somehow instead of list comprehension
            self.vdist = lambda X, y, lcf: np.array([lcf(x, y) for x in X]).astype(
                np.float32
            )

        self.N_ref: int = self.reference_features.shape[0]
        self.frame_rate = frame_rate
        self.window_size: int = window_size * self.frame_rate
        self.step_size: int = step_size
        self.start_window_size: int = int(np.round(start_window_size * frame_rate))
        self.init_position: int = current_position
        self.current_position: int = current_position
        self.positions: List[int] = []
        self._warping_path: List = []
        self.global_cost_matrix: NDArray[np.float32] = (
            np.ones((reference_features.shape[0] + 1, 2), dtype=np.float32) * np.inf
        ).astype(np.float32)
        self.input_index: int = 0
        self.go_backwards: bool = False
        self.update_window_index: bool = False
        self.restart: bool = False
        self.is_following: bool = False
        self.last_queue_update = time.time()
        self.latency_stats: Dict[str, float] = {
            "total_latency": 0,
            "total_frames": 0,
            "max_latency": 0,
            "min_latency": float("inf"),
        }

    @property
    def warping_path(self) -> NDArray[np.int32]:
        wp = (np.array(self._warping_path).T).astype(np.int32)
        return wp

    def __call__(self, input: NDArray[np.float32]) -> int:
        self.step(input)
        return self.current_position

    def run(self, verbose: bool = True) -> Generator[int, None, NDArray[np.float32]]:
        """Run the online alignment process.

        Parameters
        ----------
        verbose : bool, optional
            Whether to show progress bar, by default True

        Yields
        ------
        int
            Current position in the reference sequence

        Returns
        -------
        NDArray[np.float32]
            The warping path as a 2D array where each column contains
            (reference_position, input_position)
        """
        self.reset()

        if verbose:
            pbar = progressbar.ProgressBar(max_value=self.N_ref, redirect_stdout=True)

        while self.is_still_following():
            features, f_time = self.queue.get(timeout=QUEUE_TIMEOUT)
            self.last_queue_update = time.time()
            self.input_features = (
                np.concatenate((self.input_features, features))
                if self.input_features is not None
                else features
            )
            self.step(features)

            if verbose:
                pbar.update(int(self.current_position))

            latency = time.time() - self.last_queue_update
            self.latency_stats = set_latency_stats(
                latency, self.latency_stats, self.input_index
            )
            yield self.current_position

        if verbose:
            pbar.finish()

        return self.warping_path

    def is_still_following(self):
        # TODO: check stopping if the follower is stuck.
        return self.current_position <= self.N_ref - 2

    def reset(self) -> None:
        self.current_position = self.init_position
        self.positions = []
        self._warping_path: List = []
        self.global_cost_matrix = (
            np.ones((self.reference_features.shape[0] + 1, 2), dtype=np.float32)
            * np.inf
        )
        self.input_index = 0
        self.update_window_index = False

    def get_window(self) -> Tuple[int, int]:
        w_size = self.window_size
        if self.window_index < self.start_window_size:
            w_size = self.start_window_size
        window_start = max(self.window_index - w_size, 0)
        window_end = min(self.window_index + w_size, self.N_ref)
        return window_start, window_end

    @property
    def window_index(self) -> int:
        return self.current_position

    def step(self, input_features: NDArray[np.float32]) -> None:
        """
        Update the current position and the warping path.
        """
        min_costs = np.inf
        min_index = max(self.window_index - self.step_size, 0)

        window_start, window_end = self.get_window()
        # compute local cost beforehand as it is much faster (~twice as fast)
        window_cost = self.vdist(
            self.reference_features[window_start:window_end],
            input_features.squeeze(),
            self.distance_func,
        )

        self.global_cost_matrix, min_index, min_costs = oltw_arzt_loop(
            global_cost_matrix=self.global_cost_matrix,
            window_cost=window_cost,
            window_start=window_start,
            window_end=window_end,
            input_index=self.input_index,
            min_costs=min_costs,
            min_index=min_index,
        )

        # adapt current_position: do not go backwards,
        # but also go a maximum of N steps forward

        if self.input_index == 0:
            # enforce the first time step to stay at the
            # initial position
            self.current_position = min(
                max(self.current_position, min_index),
                self.current_position,
            )
        else:
            self.current_position = min(
                max(self.current_position, min_index),
                self.current_position + self.step_size,
            )

        self._warping_path.append((self.current_position, self.input_index))
        # update input index
        self.input_index += 1


if __name__ == "__main__":
    pass
