use phf::phf_map;

use crate::unicode::decode_unicode;
// 1 2 3 4 5 6 7 8 9 0
// #a #b #c #d #e #f #g #h

pub static NUMBER_MAP: phf::Map<char, u8> = phf_map! {
    '1' => decode_unicode('⠁'),
    '2' => decode_unicode('⠃'),
    '3' => decode_unicode('⠉'),
    '4' => decode_unicode('⠙'),
    '5' => decode_unicode('⠑'),
    '6' => decode_unicode('⠋'),
    '7' => decode_unicode('⠛'),
    '8' => decode_unicode('⠓'),
    '9' => decode_unicode('⠊'),
    '0' => decode_unicode('⠚'),
};

pub fn encode_number(text: char) -> Result<u8, String> {
    if let Some(code) = NUMBER_MAP.get(&text) {
        return Ok(*code);
    }
    Err("Invalid number character".to_string())
}
