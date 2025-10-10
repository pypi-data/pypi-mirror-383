from fileformats.vendor.siemens.medimage import SyngoMi_Vr20b_Sinogram


def test_siemens_load_pydicom():

    sino = SyngoMi_Vr20b_Sinogram.sample()
    assert sino.metadata["PatientName"] == "FirstName^LastName"
