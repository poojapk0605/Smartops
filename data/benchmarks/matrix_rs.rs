fn main() {
    let n: usize = 150;
    let mut a = vec![vec![1i32; n]; n];
    let mut b = vec![vec![2i32; n]; n];
    let mut c = vec![vec![0i32; n]; n];

    for i in 0..n {
        for k in 0..n {
            for j in 0..n {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    println!("{}", c[n - 1][n - 1]);
}
