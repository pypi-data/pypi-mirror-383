from __future__ import annotations
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from typing import Iterable
import pandas as pd
from nerdd_module import Model
from nerdd_module.preprocessing import FilterByWeight
from nerdd_module.preprocessing import Sanitize
from rdkit.Chem import MolFromSmiles
from rdkit.Chem import MolToSmiles
from trialblazer.trialblazer import Trialblazer

if TYPE_CHECKING:
    from rdkit.Chem import Mol

__all__ = ["TrialblazerModel"]


class TrialblazerModel(Model):
    def __init__(self):
        super().__init__(
            preprocessing_steps=[
                Sanitize(),
                FilterByWeight(
                    min_weight=150,
                    max_weight=850,
                    remove_invalid_molecules=True,
                ),
            ],
        )

        # preload model (this takes ~30s so we save a lot of time later)
        self._models = {b: Trialblazer(M2FP_only=b) for b in [False, True]}
        for model in self._models.values():
            model.load_model()

    def _predict_mols(
        self,
        mols: list[Mol],
        fingerprints_only: bool = False,
    ) -> Iterable[dict]:
        # select model
        tb = self._models[fingerprints_only]

        # Trialblazer accepts input only as smiles
        # -> convert all molecules to smiles
        smiles = [MolToSmiles(mol) for mol in mols]

        # use ids to identify molecules later
        # Note: ids cannot be numbers, because trialblazer will throw an error
        ids = [f"mol_{i}" for i in range(len(smiles))]

        # we assign the input dataset directly, because tb.import_smiles
        # and tb.import_smiles_df have undesired side effects
        tb.smiles = pd.DataFrame({"SMILES": smiles, "chembl_id": ids})

        # run the model
        with TemporaryDirectory() as tmpdir:
            tb.prepare_testset(out_folder=tmpdir, force=True)
            tb.run_model()

        # get the results
        df = tb.get_dataframe()

        for row in df.itertuples(index=False):
            yield {
                "mol_id": int(row.id[len("mol_") :]),
                "prediction": row.prediction,
                "pred_prob_positive": row.pred_prob_positive,
                "pred_prob_negative": row.pred_prob_negative,
                "PrOCTOR_score": row.PrOCTOR_score,
                # itertuples automatically renames column names that
                # starts with a number
                "3_nearest_neighbor_score": row._8,  # noqa: SLF001
                "closest_distance_to_training": (
                    row.closest_distance_to_training
                ),
                "closest_training_mol": MolFromSmiles(
                    row.closest_training_smi,
                ),
            }
