import pytest
import xnum.params
from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Modi tests"
MODI_DIGITS = "𑙐𑙑𑙒𑙓𑙔𑙕𑙖𑙗𑙘𑙙"


CONVERSION_CASES = {
    NumeralSystem.ARABIC_INDIC: "٠١٢٣٤٥٦٧٨٩",
    NumeralSystem.ENGLISH: "0123456789",
    NumeralSystem.ENGLISH_FULLWIDTH: "０１２３４５６７８９",
    NumeralSystem.ENGLISH_SUBSCRIPT: "₀₁₂₃₄₅₆₇₈₉",
    NumeralSystem.ENGLISH_SUPERSCRIPT: "⁰¹²³⁴⁵⁶⁷⁸⁹",
    NumeralSystem.ENGLISH_DOUBLE_STRUCK: "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    NumeralSystem.ENGLISH_BOLD: "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    NumeralSystem.ENGLISH_MONOSPACE: "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    NumeralSystem.ENGLISH_SANS_SERIF: "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
    NumeralSystem.ENGLISH_SANS_SERIF_BOLD: "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    NumeralSystem.PERSIAN: "۰۱۲۳۴۵۶۷۸۹",
    NumeralSystem.HINDI: "०१२३४५६७८९",
    NumeralSystem.BENGALI: "০১২৩৪৫৬৭৮৯",
    NumeralSystem.THAI: "๐๑๒๓๔๕๖๗๘๙",
    NumeralSystem.KHMER: "០១២៣៤៥៦៧៨៩",
    NumeralSystem.BURMESE: "၀၁၂၃၄၅၆၇၈၉",
    NumeralSystem.TIBETAN: "༠༡༢༣༤༥༦༧༨༩",
    NumeralSystem.GUJARATI: "૦૧૨૩૪૫૬૭૮૯",
    NumeralSystem.ODIA: "୦୧୨୩୪୫୬୭୮୯",
    NumeralSystem.TELUGU: "౦౧౨౩౪౫౬౭౮౯",
    NumeralSystem.KANNADA: "೦೧೨೩೪೫೬೭೮೯",
    NumeralSystem.GURMUKHI: "੦੧੨੩੪੫੬੭੮੯",
    NumeralSystem.LAO: "໐໑໒໓໔໕໖໗໘໙",
    NumeralSystem.NKO: "߀߁߂߃߄߅߆߇߈߉",
    NumeralSystem.MONGOLIAN: "᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙",
    NumeralSystem.SINHALA_LITH: "෦෧෨෩෪෫෬෭෮෯",
    NumeralSystem.MYANMAR_SHAN: "႐႑႒႓႔႕႖႗႘႙",
    NumeralSystem.LIMBU: "᥆᥇᥈᥉᥊᥋᥌᥍᥎᥏",
    NumeralSystem.VAI: "꘠꘡꘢꘣꘤꘥꘦꘧꘨꘩",
    NumeralSystem.OL_CHIKI: "᱐᱑᱒᱓᱔᱕᱖᱗᱘᱙",
    NumeralSystem.BALINESE: "᭐᭑᭒᭓᭔᭕᭖᭗᭘᭙",
    NumeralSystem.NEW_TAI_LUE: "᧐᧑᧒᧓᧔᧕᧖᧗᧘᧙",
    NumeralSystem.SAURASHTRA: "꣐꣑꣒꣓꣔꣕꣖꣗꣘꣙",
    NumeralSystem.JAVANESE: "꧐꧑꧒꧓꧔꧕꧖꧗꧘꧙",
    NumeralSystem.CHAM: "꩐꩑꩒꩓꩔꩕꩖꩗꩘꩙",
    NumeralSystem.LEPCHA: "᱀᱁᱂᱃᱄᱅᱆᱇᱈᱉",
    NumeralSystem.SUNDANESE: "᮰᮱᮲᮳᮴᮵᮶᮷᮸᮹",
    NumeralSystem.DIVES_AKURU: "𑥐𑥑𑥒𑥓𑥔𑥕𑥖𑥗𑥘𑥙",
    NumeralSystem.MODI: MODI_DIGITS,
    NumeralSystem.TAKRI: "𑛀𑛁𑛂𑛃𑛄𑛅𑛆𑛇𑛈𑛉",
    NumeralSystem.NEWA: "𑑐𑑑𑑒𑑓𑑔𑑕𑑖𑑗𑑘𑑙",
    NumeralSystem.TIRHUTA: "𑓐𑓑𑓒𑓓𑓔𑓕𑓖𑓗𑓘𑓙",
    NumeralSystem.SHARADA: "𑇐𑇑𑇒𑇓𑇔𑇕𑇖𑇗𑇘𑇙",
    NumeralSystem.KHUDAWADI: "𑋰𑋱𑋲𑋳𑋴𑋵𑋶𑋷𑋸𑋹",
    NumeralSystem.CHAKMA: "𑄶𑄷𑄸𑄹𑄺𑄻𑄼𑄽𑄾𑄿",
}


def test_modi_digits():

    assert MODI_DIGITS == xnum.params.MODI_DIGITS
    assert list(map(int, MODI_DIGITS)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


@pytest.mark.parametrize("target,expected", CONVERSION_CASES.items())
def test_modi_to_other_systems(target, expected):

    assert convert(
        MODI_DIGITS,
        source=NumeralSystem.MODI,
        target=target,
    ) == expected

    assert convert(
        f"abc {MODI_DIGITS} abc",
        source=NumeralSystem.MODI,
        target=target,
    ) == f"abc {expected} abc"
