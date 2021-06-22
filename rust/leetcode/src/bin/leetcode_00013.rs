// 13. Roman to Integer
// Easy


struct Solution {}

#[derive(Debug)]
struct Pair<> {
    s: String,
    val: i32,
}

impl Solution {
    pub fn roman_to_int(s: String) -> i32 {
        let mut s = s.as_str();
        let rules: Vec<Pair> = vec![
            Pair{s: String::from("I"), val: 1},
            Pair{s: String::from("IV"), val: 4},
            Pair{s: String::from("V"), val: 5},
            Pair{s: String::from("IX"), val: 9},
            Pair{s: String::from("X"), val: 10},
            Pair{s: String::from("XL"), val: 40},
            Pair{s: String::from("L"), val: 50},
            Pair{s: String::from("XC"), val: 90},
            Pair{s: String::from("C"), val: 100},
            Pair{s: String::from("CD"), val: 400},
            Pair{s: String::from("D"), val: 500},
            Pair{s: String::from("CM"), val: 900},
            Pair{s: String::from("M"), val: 1000},
        ];
        let mut result = 0;
        for rule in rules.iter().rev() {
            if s.is_empty() {
                break
            } 
            while let Some(remainder) = s.strip_prefix(rule.s.as_str()) {
                s = remainder;
                result += rule.val;
            }
        }
        result
    }
    
}

#[cfg(test)]
mod test {
    use super::Solution;

    #[test]
    fn test_to_test_ok() {
        assert_eq!(Solution::roman_to_int("II".to_string()), 2);
        assert_eq!(Solution::roman_to_int("III".to_string()), 3);
        assert_eq!(Solution::roman_to_int("IV".to_string()), 4);
        assert_eq!(Solution::roman_to_int("VII".to_string()), 7);
        assert_eq!(Solution::roman_to_int("IX".to_string()), 9);
        assert_eq!(Solution::roman_to_int("X".to_string()), 10);
        assert_eq!(Solution::roman_to_int("XXIV".to_string()), 24);
        assert_eq!(Solution::roman_to_int("XLV".to_string()), 45);
    }
  
}

fn main() {
    println!("{}", Solution::roman_to_int("IXIII".to_string()));
}
