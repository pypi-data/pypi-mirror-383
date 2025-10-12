import json
import os
from pathlib import Path

import numpy as np
import polars as pl
from phylogenie import load_newick
from phylogenie.utils import get_node_depths
from tqdm import tqdm

from bella_companion.utils import submit_job

THIS_DIR = Path(__file__).parent


def run_beast():
    base_output_dir = Path(os.environ["BELLA_BEAST_OUTPUT_DIR"])
    output_dir = base_output_dir / "fbd-empirical"
    os.makedirs(output_dir, exist_ok=True)

    data_dir = THIS_DIR / "data"
    tree_file = data_dir / "trees.nwk"
    change_times_file = data_dir / "change_times.csv"

    trees = load_newick(str(tree_file))
    assert isinstance(trees, list)
    change_times = (
        pl.read_csv(change_times_file, has_header=False).to_series().to_numpy()
    )
    time_predictor = " ".join(list(map(str, np.repeat([0, *change_times], 4))))
    body_mass_predictor = " ".join(["0", "1", "2", "3"] * (len(change_times) + 1))

    job_ids = {}
    for i, tree in enumerate(tqdm(trees)):
        process_length = max(get_node_depths(tree).values())
        command = " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                f"-D types=0,1,2,3",
                f'-D startTypePriorProbs="0.25 0.25 0.25 0.25"',
                f"-D birthRateUpper=5",
                f"-D deathRateUpper=5",
                f"-D samplingRateUpper=5",
                f'-D samplingRateInit="2.5 2.5 2.5 2.5 2.5 2.5 2.5"',
                f"-D migrationRateUpper=5",
                f'-D migrationRateInit="2.5 0 0 2.5 2.5 0 0 2.5 2.5 0 0 2.5"',
                f'-D nodes="16 8"',
                f'-D layersRange="0,1,2"',
                f"-D treeFile={tree_file}",
                f"-D treeIndex={i}",
                f"-D changeTimesFile={change_times_file}",
                f"-D samplingChangeTimesFile={data_dir / 'sampling_change_times.csv'}",
                f"-D typeTraitFile={data_dir / 'body_mass.csv'}",
                f"-D processLength={process_length}",
                f'-D timePredictor="{time_predictor}"',
                f'-D bodyMassPredictor="{body_mass_predictor}"',
                f"-prefix {output_dir}{os.sep}",
                str(Path(os.environ["BELLA_BEAST_CONFIGS_DIR"]) / "fbd-empirical.xml"),
            ]
        )
        job_ids[i] = submit_job(
            command,
            Path(os.environ["BELLA_SBATCH_LOG_DIR"]) / "fbd-empirical" / str(i),
            mem_per_cpu="12000",
        )

    with open(base_output_dir / "fbd_empirical_job_ids.json", "w") as f:
        json.dump(job_ids, f)
