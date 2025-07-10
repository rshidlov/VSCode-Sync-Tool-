from vscode_sync import presets


def test_presets_structure():
    assert isinstance(presets.PRESETS, dict)
    for _, value in presets.PRESETS.items():
        assert "extensions" in value
        assert "settings" in value
        assert isinstance(value["extensions"], list)
        assert isinstance(value["settings"], dict)


def test_presets_content():
    for preset in presets.PRESETS.values():
        for ext in preset["extensions"]:
            assert isinstance(ext, str)
        for k, _ in preset["settings"].items():
            assert isinstance(k, str)
