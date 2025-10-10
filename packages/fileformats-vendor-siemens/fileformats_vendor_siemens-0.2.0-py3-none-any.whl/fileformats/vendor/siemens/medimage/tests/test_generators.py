from fileformats.vendor.siemens.medimage import (
    SyngoMi_Vr20b_ListMode,
    SyngoMi_Vr20b_CountRate,
    SyngoMi_Vr20b_Sinogram,
    SyngoMi_Vr20b_DynamicSinogramSeries,
    SyngoMi_Vr20b_Normalisation,
    SyngoMi_Vr20b_Parameterisation,
    SyngoMi_Vr20b_CtSpl,
)


def test_siemens_pet_listmode_generator():
    img = SyngoMi_Vr20b_ListMode.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_countrate_generator():
    img = SyngoMi_Vr20b_CountRate.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_sinogram_generator():
    img = SyngoMi_Vr20b_Sinogram.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_dynamics_sino_generator():
    img = SyngoMi_Vr20b_DynamicSinogramSeries.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_normalisation_generator():
    img = SyngoMi_Vr20b_Normalisation.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_petct_spl_generator():
    img = SyngoMi_Vr20b_CtSpl.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_parameterisation_generator():
    img = SyngoMi_Vr20b_Parameterisation.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"
