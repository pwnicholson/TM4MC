import tempfile
from collections import Counter
import types

import wmtt4mc


def _block(namespaced_name, properties=None):
    props = properties or {}
    return types.SimpleNamespace(namespaced_name=namespaced_name, properties=props)


def test_reason_needs_real_palette_entry():
    assert wmtt4mc._reason_needs_real_palette_entry("variant", True) is False
    assert wmtt4mc._reason_needs_real_palette_entry("wiki_base_color", True) is False
    assert wmtt4mc._reason_needs_real_palette_entry("generic_palette_fallback", True) is False
    assert wmtt4mc._reason_needs_real_palette_entry("unknown", False) is True


def test_wiki_base_colors_for_common_blocks():
    cases = [
        ("minecraft:grass_block", (127, 178, 56)),
        ("minecraft:stone", (112, 112, 112)),
        ("minecraft:water", (64, 64, 255)),
        ("minecraft:oak_log", (143, 119, 72)),
        ("minecraft:oak_leaves", (0, 124, 0)),
        ("minecraft:sand", (247, 233, 163)),
        ("minecraft:clay", (164, 168, 184)),
        ("minecraft:acacia_planks", (216, 127, 51)),
        ("minecraft:birch_log", (255, 252, 245)),
        ("minecraft:dark_oak_planks", (102, 76, 51)),
        ("minecraft:deepslate", (100, 100, 100)),
        ("minecraft:nether_bricks", (112, 2, 0)),
        ("minecraft:cherry_leaves", (242, 127, 165)),
        ("minecraft:leaves|cherry", (242, 127, 165)),
        ("minecraft:wood|oak", (162, 130, 78)),
    ]

    for block_id, expected in cases:
        rgb, _, known, _ = wmtt4mc.classify_block(_block(block_id))
        assert rgb == expected, f"{block_id} should map to {expected}, got {rgb}"
        assert known is True


def test_plant_variant_palette_mapping():
    plants = [
        ("universal_minecraft:plant[plant_type='dandelion']", (230, 210, 60)),
        ("universal_minecraft:plant[plant_type='poppy']", (200, 60, 60)),
        ("universal_minecraft:plant[plant_type='oxeye_daisy']", (235, 235, 235)),
        ("universal_minecraft:double_plant[half='upper',plant_type='peony']", (230, 140, 170)),
        ("universal_minecraft:plant[plant_type='allium']", (175, 90, 190)),
    ]
    for raw, expected in plants:
        rgb, _, known, reason = wmtt4mc.classify_block(raw)
        assert rgb == expected
        assert known is True
        assert reason == 'variant'


def test_banner_color_mapping():
    banners = [
        ("universal_minecraft:banner[color='yellow',rotation='2']", (249, 198, 40)),
        ("universal_minecraft:banner[color='white',rotation='2']", (235, 235, 235)),
        ("universal_minecraft:banner[color='black',rotation='3']", (30, 30, 30)),
    ]
    for raw, expected in banners:
        rgb, _, known, reason = wmtt4mc.classify_block(raw)
        assert rgb == expected
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback')


def test_material_specific_stairs_and_slabs_map_to_palette_variants():
    cases = [
        ("universal_minecraft:stairs[facing='north',half='bottom',material='oak',shape='straight']", (162, 130, 78)),
        ("universal_minecraft:slab[material='spruce',type='bottom']", (129, 86, 49)),
        ("universal_minecraft:stairs[facing='south',half='bottom',material='stone_brick',shape='straight']", (112, 112, 112)),
    ]
    for raw, expected in cases:
        rgb, _, known, reason = wmtt4mc.classify_block(raw)
        assert rgb == expected, f"{raw} should map to {expected}, got {rgb}"
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback', 'variant')


def test_pink_petals_direct_ids_use_known_palette_color():
    rgb, _, known, reason = wmtt4mc.classify_block(_block("minecraft:pink_petals"))
    assert rgb == (242, 127, 165)
    assert known is True
    assert reason in ('palette', 'variant', 'wiki_base_color', 'generic_palette_fallback')


def test_stair_and_slab_ids_do_not_match_air_token():
    cases = [
        ("minecraft:oak_stairs", (143, 119, 72)),
        ("minecraft:stone_brick_stairs", (112, 112, 112)),
        ("minecraft:stairs", (140, 130, 120)),
    ]
    for block_id, expected in cases:
        rgb, _, known, reason = wmtt4mc.classify_block(_block(block_id))
        assert rgb == expected, f"{block_id} should map to {expected}, got {rgb}"
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback', 'wiki_base_color')


def test_quartz_and_wool_stairs_and_slabs_have_palette_entries():
    cases = [
        ("minecraft:quartz_stairs", (255, 252, 245)),
        ("minecraft:quartz_slab", (255, 252, 245)),
        ("minecraft:white_wool_stairs", (234, 236, 237)),
        ("minecraft:orange_wool_slab", (241, 118, 20)),
        ("minecraft:black_wool_stairs", (30, 30, 30)),
    ]
    for block_id, expected in cases:
        rgb, _, known, reason = wmtt4mc.classify_block(_block(block_id))
        assert rgb == expected, f"{block_id} should map to {expected}, got {rgb}"
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback')


def test_wall_variants_and_nether_blocks_have_expected_palette_colors():
    wall_cases = [
        ("minecraft:andesite_wall", (112, 112, 112)),
        ("minecraft:blackstone_wall", (25, 25, 25)),
        ("minecraft:brick_wall", (153, 51, 51)),
        ("minecraft:polished_sulfur_wall", (229, 229, 51)),
        ("minecraft:polished_cinnabar_wall", (153, 51, 51)),
        ("minecraft:stone_brick_wall", (112, 112, 112)),
    ]
    for block_id, expected in wall_cases:
        rgb, _, known, reason = wmtt4mc.classify_block(_block(block_id))
        assert rgb == expected, f"{block_id} should map to {expected}, got {rgb}"
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback')

    nether_cases = [
        ("minecraft:netherrack", (112, 2, 0)),
        ("minecraft:nether_bricks", (112, 2, 0)),
        ("minecraft:red_nether_bricks", (112, 2, 0)),
    ]
    for block_id, expected in nether_cases:
        rgb, _, known, reason = wmtt4mc.classify_block(_block(block_id))
        assert rgb == expected, f"{block_id} should map to {expected}, got {rgb}"
        assert known is True
        assert reason in ('palette', 'wiki_base_color', 'generic_palette_fallback')


def test_sulfur_and_cinnabar_palette_entries():
    cases = [
        ("minecraft:polished_sulfur", (232, 196, 52)),
        ("minecraft:polished_sulfur_wall[wall_connection_type_east='none',wall_connection_type_north='none',wall_connection_type_south='none',wall_connection_type_west='short',wall_post_bit='1']", (220, 180, 48)),
        ("minecraft:polished_cinnabar_wall[wall_connection_type_east='short',wall_connection_type_north='short',wall_connection_type_south='short',wall_connection_type_west='none',wall_post_bit='1']", (190, 55, 55)),
    ]
    for raw, expected in cases:
        rgb, _, known, reason = wmtt4mc.classify_block(raw)
        assert rgb == expected
        assert known is True
        assert reason in ('palette', 'generic_palette_fallback')


def test_cherry_leaves_variant_properties():
    block = _block("minecraft:leaves", {"leaves": "cherry"})
    rgb, _, known, reason = wmtt4mc.classify_block(block)
    assert rgb == (242, 127, 165)
    assert known is True
    assert reason == "variant"


def test_run_raw_ids_log_includes_color():
    raw_counts = Counter({
        "universal_minecraft:plant[plant_type=\"dandelion\"]": 1,
        "universal_minecraft:banner[color=\"yellow\",rotation=\"2\"]": 1,
    })
    with tempfile.TemporaryDirectory() as tmpdir:
        out_png = os.path.join(tmpdir, "frame.png")
        log_path = os.path.join(tmpdir, "run_raw_ids.log")
        wmtt4mc._append_unique_raw_ids_to_runlog(out_png, raw_counts)
        with open(log_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        assert any("dandelion" in ln and "rgb(" in ln and "#" in ln for ln in lines)
        assert any("yellow" in ln and "rgb(" in ln and "#" in ln for ln in lines)


if __name__ == "__main__":
    test_reason_needs_real_palette_entry()
    test_wiki_base_colors_for_common_blocks()
    print("Wiki palette mapping regression tests passed.")
