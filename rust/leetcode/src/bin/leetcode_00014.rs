// 14. Longest Common Prefix
// Easy
// 
// Faster solution
// Runtime: 0 ms, faster than 100.00% of Rust online submissions for Longest Common Prefix.
// Memory Usage: 2.1 MB, less than 79.84% of Rust online submissions for Longest Common Prefix.

use std::{collections::HashMap};


impl Solution {
    pub fn longest_common_prefix(strs: Vec<String>) -> String {
        let mut prefix_counter: HashMap<String, usize> = HashMap::new();
        for s in strs.iter() {
            // println!("{}", s);
            for (i, _) in s.chars().enumerate() {
                let prefix = &s[..i+1];
                match prefix_counter.get_mut(prefix) {
                    Some(x) => {
                        *x += 1;
                    }
                    None => {
                        prefix_counter.insert(prefix.to_owned(), 1);
                    }
                }
            }
        }
        let mut best_string = String::from("");
        for (k, v) in prefix_counter.iter() {
            // println!("{} {}", k, v);
            if *v == strs.len() && best_string.len() < k.len() {
                best_string = (*k).clone();
            }
        }
        best_string
    }
}

#[allow(unused)]
struct Solution {}

#[cfg(test)]
mod test {
    use super::Solution;
    #[test]
    fn test_1() {
        
        let input: Vec<String> = vec![
            "aab".to_string(), "aac".to_string(), "aaaa".to_string(), "aab12".to_string(),
        ];
        assert_eq!(Solution::longest_common_prefix(input), "aa".to_string());
    }    
}


fn main() {
}