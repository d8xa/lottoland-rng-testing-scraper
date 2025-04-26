import time
import random
from typing import Iterator

import pandas as pd
from pathlib import Path


def backoff_generator(total_samples: int, wait_min: float = 4.0, wait_max: float = 10.0) -> Iterator[float]:
    """Generates sleep times with clustered click patterns and exponential backoff"""

    remaining = total_samples
    
    while remaining > 0:
        base_wait = random.uniform(wait_min, wait_max)
        
        # Determine current cluster size (1-3 quick clicks)
        cluster_size = min(random.randint(1, 3), remaining)
        
        # Yield quick intervals for cluster
        for _ in range(cluster_size):
            yield random.uniform(0.4, 1.2)
            remaining -= 1
        
        # Yield backoff period if more samples remain
        if remaining > 0:
            yield base_wait
            base_wait = min(15, base_wait * 1.3)  # Exponential backoff with cap
            remaining -= 1


def sample(scraper, n: int):
    """Collect n samples with realistic timing patterns"""

    for delay in backoff_generator(n):
        time.sleep(delay)
        scraper.get_quicktip()


def read_sample(path: Path | str) -> pd.DataFrame:
    if path.exists() and path.is_file():
        df = pd.read_csv(path, index_col=None)
    return df


def write_sample(df: pd.DataFrame, path: Path | str) -> None:
    if len(df) > 0:
        path.parent.mkdir(exist_ok=True, parents=True)
        df.to_csv(path, index=False)


def read_samples(folder: Path | str) -> pd.DataFrame:
    return pd.concat(
        (pd.read_csv(file) for file in folder.iterdir() if file.suffix == '.csv'),
        ignore_index=True
    )


def new_sample_filepath(data_dir: Path | str) -> Path:
    n_current = len([p for p in data_dir.iterdir() if p.suffix == '.csv'])
    return data_dir / f'sample-{n_current+1}.csv'