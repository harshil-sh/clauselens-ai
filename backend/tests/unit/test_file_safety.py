from app.services.file_safety import build_safe_filename


def test_build_safe_filename_normalizes_path_segments_and_extension() -> None:
    assert build_safe_filename(r"..\contracts\MSA Final?.DOCX") == "MSA-Final.docx"


def test_build_safe_filename_falls_back_to_upload_when_stem_is_removed() -> None:
    assert build_safe_filename("...?.pdf") == "upload.pdf"


def test_build_safe_filename_keeps_safe_characters_in_stem() -> None:
    assert build_safe_filename("vendor_agreement.v2-final.txt") == "vendor_agreement.v2-final.txt"
