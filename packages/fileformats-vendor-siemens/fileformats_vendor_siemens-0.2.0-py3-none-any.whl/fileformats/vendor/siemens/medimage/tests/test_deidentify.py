import pytest
from fileformats.core.exceptions import FileFormatsExtrasError
from fileformats.vendor.siemens.medimage import SyngoMi_Vr20b_Sinogram


def test_raw_pet_data_deidentify():
    raw_pet = SyngoMi_Vr20b_Sinogram.sample()
    with pytest.raises(FileFormatsExtrasError):
        raw_pet.deidentify()
