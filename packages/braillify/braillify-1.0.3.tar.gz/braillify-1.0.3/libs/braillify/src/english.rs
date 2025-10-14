use phf::phf_map;

use crate::unicode::decode_unicode;

pub static ENGLISH_MAP: phf::Map<char, u8> = phf_map! {
    'a' => decode_unicode('⠁'),
    'b' => decode_unicode('⠃'),
    'c' => decode_unicode('⠉'),
    'd' => decode_unicode('⠙'),
    'e' => decode_unicode('⠑'),
    'f' => decode_unicode('⠋'),
    'g' => decode_unicode('⠛'),
    'h' => decode_unicode('⠓'),
    'i' => decode_unicode('⠊'),
    'j' => decode_unicode('⠚'),
    'k' => decode_unicode('⠅'),
    'l' => decode_unicode('⠇'),
    'm' => decode_unicode('⠍'),
    'n' => decode_unicode('⠝'),
    'o' => decode_unicode('⠕'),
    'p' => decode_unicode('⠏'),
    'q' => decode_unicode('⠟'),
    'r' => decode_unicode('⠗'),
    's' => decode_unicode('⠎'),
    't' => decode_unicode('⠞'),
    'u' => decode_unicode('⠥'),
    'v' => decode_unicode('⠧'),
    'w' => decode_unicode('⠺'),
    'x' => decode_unicode('⠭'),
    'y' => decode_unicode('⠽'),
    'z' => decode_unicode('⠵'),
};
/// 제28항 로마자는 ｢통일영어점자 규정｣에 따라 다음과 같이 적는다.
pub fn encode_english(text: char) -> Result<u8, String> {
    if let Some(code) = ENGLISH_MAP.get(&text.to_ascii_lowercase()) {
        return Ok(*code);
    }
    Err("Invalid English character".to_string())
}
