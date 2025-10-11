import logging
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial, wraps
from multiprocessing import Pool
from time import time
from typing import Callable, Generic, List, Literal, Tuple, TypeVar, Union

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")


T = TypeVar("T")
V = TypeVar("V")


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logging.info(
            "func:%r args:[%r, %r] took: %2.4f sec" % (f.__name__, args, kw, te - ts)
        )
        return result

    return wrap


class ProcessingType(Enum):
    THREAD = "THREAD"
    PROCESS = "PROCESS"
    SEQUENCE = "SEQUENCE"


def run_it(
    params: Tuple[int, T], processor: Callable[[Tuple[int, T]], V]
) -> Tuple[V, None]:
    try:
        return processor(params)
    except Exception:
        return None


class ParallelProcessing:
    def __init__(self, workers: int, processing_type: ProcessingType):
        self.workers: int = workers
        self.processing_type: ProcessingType = processing_type
        self.logger = logging.getLogger(self.__class__.__name__)

    @timing
    def run(
        self,
        processor: Callable[[Tuple[int, T]], V],
        items: List[T],
        progress_bar: bool = True,
    ) -> List[V]:
        partial_fn = partial(run_it, processor=processor)
        if self.processing_type == ProcessingType.PROCESS:
            with Pool(processes=self.workers) as pool:
                return list(
                    tqdm(
                        pool.imap(
                            partial_fn, [(idx, item) for idx, item in enumerate(items)]
                        ),
                        total=len(items),
                        disable=not progress_bar,
                    )
                )

        if self.processing_type == ProcessingType.THREAD:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                return list(
                    tqdm(
                        pool.map(
                            partial_fn, [(idx, item) for idx, item in enumerate(items)]
                        ),
                        total=len(items),
                        disable=not progress_bar,
                    )
                )

        results = []
        for idx, item in tqdm(
            enumerate(items),
            disable=not progress_bar,
        ):
            results.append(partial_fn(params=(idx, item)))
        return results

    @staticmethod
    def thread(
        workers: int,
        processor: Callable[[int, T], V],
        items: List[T],
        progress_bar: bool = True,
    ) -> List[V]:
        pp = ParallelProcessing(workers=workers, processing_type=ProcessingType.THREAD)
        return pp.run(processor=processor, items=items, progress_bar=progress_bar)

    @staticmethod
    def process(
        workers: int,
        processor: Callable[[int, T], V],
        items: List[T],
        progress_bar: bool = True,
    ) -> List[V]:
        pp = ParallelProcessing(workers=workers, processing_type=ProcessingType.PROCESS)
        return pp.run(processor=processor, items=items, progress_bar=progress_bar)

    @staticmethod
    def sequence(
        processor: Callable[[int, T], V],
        items: List[T],
        progress_bar: bool = True,
    ) -> List[V]:
        pp = ParallelProcessing(workers=0, processing_type=ProcessingType.SEQUENCE)
        return pp.run(processor=processor, items=items, progress_bar=progress_bar)
