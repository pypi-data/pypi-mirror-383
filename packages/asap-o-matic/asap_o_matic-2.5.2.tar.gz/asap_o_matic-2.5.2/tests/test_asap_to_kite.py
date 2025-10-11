import hashlib
import importlib.resources as ir
from importlib.resources.abc import Traversable
from pathlib import Path

import fastq as fq
import pytest
from asap_o_matic import asap_to_kite


@pytest.fixture
def read1_file() -> Traversable:
    return ir.files("tests").joinpath("data", "cellranger", "test_S_S3_R1_001.fastq.gz")


@pytest.fixture
def read2_file() -> Traversable:
    return ir.files("tests").joinpath("data", "cellranger", "test_S_S3_R2_001.fastq.gz")


@pytest.fixture
def read3_file() -> Traversable:
    return ir.files("tests").joinpath("data", "cellranger", "test_S_S3_R3_001.fastq.gz")


@pytest.fixture
def expected_read1() -> Traversable:
    return ir.files("tests").joinpath("data", "kite_results", "expected_read1.fastq")


@pytest.fixture
def expected_read2() -> Traversable:
    return ir.files("tests").joinpath("data", "kite_results", "expected_read2.fastq")


def test_asap_to_kite(read1_file: Path, read2_file: Path, read3_file: Path, expected_read1: Path, expected_read2: Path, tmp_path: Path) -> None:
    new_read1 = tmp_path.joinpath("new_read1.fastq")
    new_read2 = tmp_path.joinpath("new_read2.fastq")
    for a, b, c in zip(fq.read(str(read1_file)), fq.read(str(read2_file)), fq.read(str(read3_file)), strict=True):
        # unclear on why, but pyright gets the types mixed up here? thus the ignores
        asap_to_kite(
            read1=a,  # pyright: ignore[reportArgumentType]
            read2=b,  # pyright: ignore[reportArgumentType]
            read3=c,  # pyright: ignore[reportArgumentType]
            rc_R2=False,
            conjugation="TotalSeqB",
            new_read1_handle=str(new_read1),
            new_read2_handle=str(new_read2),
        ) # type: ignore
    assert compare_files(new_read1, expected_read1)
    assert compare_files(new_read2, expected_read2)


def compare_files(file_handle_1: Path, file_handle_2: Path, return_hashes: bool = False) -> bool | tuple[str, str]:
    file1_hash = hashlib.sha256()
    file2_hash = hashlib.sha256()
    with file_handle_1.open("rb") as read1, file_handle_2.open("rb") as read2:
        while True:
            read1_data = read1.read(32768)
            read2_data = read2.read(32768)
            if not (read1_data and read2_data):
                break
            file1_hash.update(read1_data)
            file2_hash.update(read2_data)
    if return_hashes:
        return file1_hash.hexdigest(), file2_hash.hexdigest()
    else:
        return file1_hash.hexdigest() == file2_hash.hexdigest()
