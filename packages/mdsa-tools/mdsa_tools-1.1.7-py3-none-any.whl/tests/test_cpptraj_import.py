import numpy as np

def test_importer_file_creation(importer):
    rep=importer.create_systems_rep()
    print(rep)
    return

# tests/test_cpptraj_import_extra.py
import io
from pathlib import Path
import numpy as np
import pytest
import mdtraj as md

from mdsa_tools.Cpptraj_import import cpptraj_hbond_import



def test_extract_headers_parses_pairs(tmp_path):
    # Header + one data row (cpptraj-style)
    text = "#Frame HB_1@N_2@O HB_2@N_3@O HB_2@N_2@O\n0  1 0 1\n"
    f = tmp_path / "hbonds.dat"
    f.write_text(text)

    # similar to the other one Empty something
    obj = object.__new__(cpptraj_hbond_import)
    out = obj.extract_headers(str(f))
    assert out == [(1, 2), (2, 3), (2, 2)]


def test_extract_headers_missing_file_raises(tmp_path):
    obj = object.__new__(cpptraj_hbond_import)
    with pytest.raises(FileNotFoundError):
        obj.extract_headers(str(tmp_path / "does_not_exist.dat"))


def test_extract_headers_bad_token_raises(tmp_path):
    text = "#Frame HB_X@N_2@O HB_2@N_3@O\n0  1 0\n"
    f = tmp_path / "bad.dat"
    f.write_text(text)

    obj = object.__new__(cpptraj_hbond_import)
    with pytest.raises(ValueError):
        obj.extract_headers(str(f))


