use crate::unicode::decode_unicode;
use phf::phf_map;

pub static JONGSEONG_MAP: phf::Map<char, &'static [u8]> = phf_map! {
    'ㄱ' => &[decode_unicode('⠁')],
    'ㄲ' => &[decode_unicode('⠁'), decode_unicode('⠁')],
    'ㄳ' => &[decode_unicode('⠁'), decode_unicode('⠄')],
    'ㄴ' => &[decode_unicode('⠒')],
    'ㄵ' => &[decode_unicode('⠒'), decode_unicode('⠅')],
    'ㄶ' => &[decode_unicode('⠒'), decode_unicode('⠴')],
    'ㄷ' => &[decode_unicode('⠔')],
    'ㄸ' => &[decode_unicode('⠔'), decode_unicode('⠔')],
    'ㄹ' => &[decode_unicode('⠂')],
    'ㄺ' => &[decode_unicode('⠂'), decode_unicode('⠁')],
    'ㄻ' => &[decode_unicode('⠂'), decode_unicode('⠢')],
    'ㄼ' => &[decode_unicode('⠂'), decode_unicode('⠃')],
    'ㄽ' => &[decode_unicode('⠂'), decode_unicode('⠄')],
    'ㄾ' => &[decode_unicode('⠂'), decode_unicode('⠦')],
    'ㄿ' => &[decode_unicode('⠂'), decode_unicode('⠲')],
    'ㅀ' => &[decode_unicode('⠂'), decode_unicode('⠴')],
    'ㅁ' => &[decode_unicode('⠢')],
    'ㅂ' => &[decode_unicode('⠃')],
    'ㅃ' => &[decode_unicode('⠃'), decode_unicode('⠃')],
    'ㅄ' => &[decode_unicode('⠃'), decode_unicode('⠄')],
    'ㅅ' => &[decode_unicode('⠄')],
    'ㅆ' => &[decode_unicode('⠌')],
    'ㅇ' => &[decode_unicode('⠶')],
    'ㅈ' => &[decode_unicode('⠅')],
    'ㅉ' => &[decode_unicode('⠠'), decode_unicode('⠅')],
    'ㅊ' => &[decode_unicode('⠆')],
    'ㅋ' => &[decode_unicode('⠖')],
    'ㅌ' => &[decode_unicode('⠦')],
    'ㅍ' => &[decode_unicode('⠲')],
    'ㅎ' => &[decode_unicode('⠴')],
};

pub fn encode_jongseong(text: char) -> Result<&'static [u8], String> {
    if let Some(code) = JONGSEONG_MAP.get(&text) {
        return Ok(code);
    }
    Err("Invalid Korean jongseong character".to_string())
}

// pub fn decode_jongseong(code: u8) -> char {
//     JONGSEONG_MAP.get_by_right(&code).unwrap().clone()
// }

#[cfg(test)]
mod test {
    use super::*;
    #[test]
    pub fn test_encode_jongseong() {
        assert_eq!(encode_jongseong('ㄱ').unwrap(), vec![decode_unicode('⠁')]);
        assert_eq!(encode_jongseong('ㄴ').unwrap(), vec![decode_unicode('⠒')]);
        assert_eq!(encode_jongseong('ㄷ').unwrap(), vec![decode_unicode('⠔')]);
        assert_eq!(encode_jongseong('ㄹ').unwrap(), vec![decode_unicode('⠂')]);
        assert_eq!(encode_jongseong('ㅁ').unwrap(), vec![decode_unicode('⠢')]);
        assert_eq!(encode_jongseong('ㅂ').unwrap(), vec![decode_unicode('⠃')]);
        assert_eq!(encode_jongseong('ㅅ').unwrap(), vec![decode_unicode('⠄')]);
        assert_eq!(encode_jongseong('ㅇ').unwrap(), vec![decode_unicode('⠶')]);
        assert_eq!(encode_jongseong('ㅈ').unwrap(), vec![decode_unicode('⠅')]);
        assert_eq!(encode_jongseong('ㅊ').unwrap(), vec![decode_unicode('⠆')]);
        assert_eq!(encode_jongseong('ㅋ').unwrap(), vec![decode_unicode('⠖')]);
        assert_eq!(encode_jongseong('ㅌ').unwrap(), vec![decode_unicode('⠦')]);
        assert_eq!(encode_jongseong('ㅍ').unwrap(), vec![decode_unicode('⠲')]);
        assert_eq!(encode_jongseong('ㅎ').unwrap(), vec![decode_unicode('⠴')]);
    }
}
