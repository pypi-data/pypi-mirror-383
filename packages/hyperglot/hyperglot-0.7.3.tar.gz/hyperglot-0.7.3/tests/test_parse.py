"""
Tests for basic parsing and decomposition methods
"""
import os
import pytest
from hyperglot.parse import (parse_chars, parse_font_chars, parse_marks,
                             decompose_fully,
                             character_list_from_string,
                             sort_by_character_type,
                             remove_mark_base,
                             list_unique,
                             join_variants, get_joining_type,
                             drop_inheritance_tags)


def test_parse_chars():
    # Verify composites get decomposed correctly and their order is as expected

    # def parse_chars(characters, decompose=True, retain_decomposed=False):
    assert ["a", "̈"] == parse_chars("ä", decompose=True)
    assert ["ä", "a", "̈"] == parse_chars("ä", decompose=True,
                                          retain_decomposed=True)
    assert ["ä"] == parse_chars("ä", decompose=False)

    # This tests the decomposing will add first letter components, then mark
    # components (order!)
    assert ["â", "å", "a", "̂", "̊"] == parse_chars("â å",
                                                    retain_decomposed=True)
    assert ["a", "̂", "̊"] == parse_chars("â å", retain_decomposed=False)

    assert ["ĳ", "i", "j"] == parse_chars("ĳ", retain_decomposed=True)
    assert ["i", "j"] == parse_chars("ĳ", retain_decomposed=False)

    # Check basic splitting
    assert 5 == len(parse_chars("abcde"))
    assert 5 == len(parse_chars("a b c d e"))

    # Check whitespace separation
    assert ["a", "b", "c"] == parse_chars("abc")
    assert ["a", "b", "c"] == parse_chars("a   bc")

    # Check whitespaces get stripped
    # Non breaking, em space
    for uni in ["00A0", "2003"]:
        assert ["a", "b"] == parse_chars("a" + chr(int(uni, 16)) + "b")

    # Check "whitespace" control characters do not get stripped
    # joiners, directional overwrites
    for uni in ["200D", "200E", "200F"]:
        unichr = chr(int(uni, 16))
        assert ["a", unichr, "b"] == parse_chars("a" + unichr + "b")

    assert " " not in parse_chars("a   bc")
    assert " " not in parse_chars(
        "a ą b c d e ę g h i į j k l ł m n o ǫ s t w x y z ' ´")
    
    # Check characters get fully decomposed, e.g. all marks decomposed instead
    # of Acircumflex + tildecomb
    assert parse_chars("Ẫ", decompose=True) == ["A", chr(0x0302), chr(0x0303)]


def test_character_list_from_string():
    # Check list formation from (whitespace separated) input string with
    assert ["a", "b", "c"] == character_list_from_string("abc")
    assert ["a", "b", "c"] == character_list_from_string("a b c")
    assert ["a", "b", "c"] == character_list_from_string("a  b  c")
    assert ["a", "b", "c"] == character_list_from_string("a a b a c")
    assert ["ä", "b", "c"] == character_list_from_string("äbc")
    assert ["ä", "b", "c"] == character_list_from_string("ä b c")
    assert ["g̃"] == character_list_from_string("g̃")
    assert ["a", "g̃", "c"] == character_list_from_string("ag̃c")
    assert ["a", "g̃", "c"] == character_list_from_string("a g̃ c")

    assert ["a", "b", "c", "g̃"] == character_list_from_string("abcg̃")
    assert ["a", "b", "c", "g̃"] == character_list_from_string("abcg̃")
    # Any spaces will be removed, a combing mark appended to last glyph
    assert ["a", "b", "c", "g̃"] == character_list_from_string("a b c g  ̃")

    rus_aux = "А́ Е́ И́ О́ У́ Ы́ Э́ ю́ я́ а́ е́ и́ о́ у́ ы́ э́"
    rus_aux_li = rus_aux.split(" ")
    assert rus_aux_li == character_list_from_string(rus_aux, normalize=False)


def test_list_unique():
    assert ["a", "b", "c"] == list_unique(["a", "a", "b", "c"])


def test_parse_font_chars():
    eczar = os.path.abspath("tests/Eczar-v1.004/otf/Eczar-Regular.otf")
    chars = parse_font_chars(eczar)

    # Obviously this changes if the test file ever gets updated!
    assert len(chars) == 479

    # Just some basic sanity checks
    assert "Ä" in chars
    assert "अ" in chars


def test_sort_by_character_type():
    # Test sorting, Letters first, Marks second, rest after, and secondary sort
    # by ASC unicode
    expected = ["A", "Z", "a", "z", "̇", ".", "1"]
    assert sort_by_character_type(expected) == expected


def test_remove_mark_base():
    assert remove_mark_base("◌̀ ◌́ ◌̆") == "̀ ́ ̆"
    assert remove_mark_base("Д Л Ѐ Ѝ в г д ж з и й ѝ к л п п т т ц ч ш щ ю д л ◌̆") == "Д Л Ѐ Ѝ в г д ж з и й ѝ к л п п т т ц ч ш щ ю д л ̆"  # noqa


def test_parse_marks():
    assert parse_marks("ä ö å") == ['̈', '̊']
    assert parse_marks("A B C") == []
    assert parse_marks("") == []
    # assert parse_marks(["ä", "ö", "å"]) == ['̈', '̊']
    # assert parse_marks(["A", "B"]) == []

    assert parse_marks(
        "А́ Е́ И́ О́ У́ Ы́ Э́ ю́ я́ а́ е́ и́ о́ у́ ы́ э́ ю́ я́") == ["́"]

    assert ['̀', '̂', '̃', '̄', '̆', '̈', '̊', '̧'] == parse_marks(
        "À Â Å Æ Ç È Ê Ë Ì Î Ï Ñ Ò Ô Ø Ù Û Ÿ Ā Ă Ē Ĕ Ī Ĭ Ō Ŏ Œ Ū Ŭ ß à â å æ ç è ê ë ì î ï ñ ò ô ø ù û ÿ ā ă ē ĕ ī ĭ ō ŏ œ ū ŭ")  # noqa
    assert ['́', '̃', '̈', '̌'] == parse_marks(
        "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Á Ã Ä É Í Ó Õ Ö Ú Ü Č Š Ũ a b c d e f g h i j k l m n o p q r s t u v w x y z á ã ä é í ó õ ö ú ü č š ũ")  # noqa


def test_get_joining_type():
    # See we're getting expected values

    assert get_joining_type("A") == ""

    # Arabic Alef only joins on the right, so other character followed by Alef
    assert get_joining_type("ا") == "R"

    # Arabic seen joins on both sides
    assert get_joining_type("س") == "D"

    # Zero width joiner should have joining type
    assert get_joining_type("\u200C") == ""

    # Zero width non-joiner should not have joining type
    assert get_joining_type("\u200D") == "C"

    with pytest.raises(ValueError):
        get_joining_type(1) == ""


def test_join_variants():
    # Not a character with joining
    assert [] == join_variants("A")

    assert [] != join_variants("ن")
    # Noon should have isol, left, both and right joined versions
    assert 3 == len(join_variants("ن"))
    # Alef should have isol and "right" joined versions
    assert 1 == len(join_variants("ا"))

    # Check that right joined alef is returned in input order ZWJ + alef, e.g.
    # when rendered RTL that sequence will result in alef form being joined on
    # the right, i.e. final form.
    assert ['\u200d\u0627'] == join_variants("ا")

    # Zero width non-joiner should have no variants since it is not joining
    assert [] == join_variants("\u200C")

    # Zero width joiner just causes joining, but itself has no variants
    assert [] == join_variants("\u200D")

    with pytest.raises(ValueError):
        join_variants(1) == ""


def test_decompose_fully():
    assert decompose_fully("A") == ["A"]
    assert decompose_fully("Ä") == ["A", chr(0x0308)]
    
    # For multiple chars decompose each
    assert decompose_fully("A" + chr(0x0308)) == ["A", chr(0x0308)]
    assert decompose_fully("AA") == ["A", "A"]
    assert decompose_fully("ÄÄ") == ["A", chr(0x0308), "A", chr(0x0308)]

    # Decompose iteratively
    assert decompose_fully("Ẫ") == ["A", chr(0x0302), chr(0x0303)]


def test_inheritance_tags():

    # Returns tuple of:
    # - pruned original
    # - original with placeholders where to re-insert tags
    # - tags to insert (should always be trimed to <iso...> without spaces and neat)

    assert drop_inheritance_tags("A B <eng> C D") == ("A B C D", "A B %s C D", ["<eng>"])
    assert drop_inheritance_tags({ "eng": None }) == ("", "%s", ["<eng>"])
    assert drop_inheritance_tags('<eng>') == ("", "%s", ["<eng>"])
    assert drop_inheritance_tags('< eng >') == ("", "%s", ["<eng>"])
    assert drop_inheritance_tags('<  eng   Latin historical >') == ("", "%s", ["<eng Latin historical>"])

    assert drop_inheritance_tags("0") == ("0", "0", [])
    assert drop_inheritance_tags(0) == ("0", "0", [])
