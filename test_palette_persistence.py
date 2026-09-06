import json
from pathlib import Path

import tm4mc


def test_generated_palette_uses_rgb_overrides_schema(tmp_path):
    palette_path = tmp_path / "palette.json"
    source_palette = json.loads(
        Path(__file__).resolve().with_name("palette.json").read_text(encoding="utf-8")
    )

    tm4mc.ensure_palette_json(str(palette_path))

    data = json.loads(palette_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert isinstance(data["rgb_overrides"], dict)
    assert data["rgb_overrides"]
    assert data["rgb_overrides"] == source_palette["rgb_overrides"]
    assert "palette" not in data

    _, loaded, _ = tm4mc._pal_load_file(str(palette_path))
    assert loaded