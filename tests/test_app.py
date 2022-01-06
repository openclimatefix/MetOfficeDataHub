from metofficeamd.app import MetOfficeAMD


def test_init():
    _ = MetOfficeAMD()


def test_download_all():

    amd = MetOfficeAMD()
    amd.download_all_files()


def test_load_all_files():

    amd = MetOfficeAMD()
    amd.download_all_files()
    amd.load_all_files()
