fn score(input: Vec<f64>) -> f64 {
    let var0: f64;
    if (input[12]) <= (9.845000267028809_f64) {
        if (input[5]) <= (6.959500074386597_f64) {
            if (input[6]) <= (96.20000076293945_f64) {
                var0 = 25.093162393162395_f64;
            } else {
                var0 = 50.0_f64;
            }
        } else {
            var0 = 38.074999999999996_f64;
        }
    } else {
        if (input[12]) <= (15.074999809265137_f64) {
            var0 = 20.518439716312056_f64;
        } else {
            var0 = 14.451282051282046_f64;
        }
    }
    let var1: f64;
    if (input[12]) <= (9.650000095367432_f64) {
        if (input[5]) <= (7.437000036239624_f64) {
            if (input[7]) <= (1.47284996509552_f64) {
                var1 = 50.0_f64;
            } else {
                var1 = 26.7965317919075_f64;
            }
        } else {
            var1 = 44.21176470588236_f64;
        }
    } else {
        if (input[12]) <= (17.980000495910645_f64) {
            var1 = 19.645652173913035_f64;
        } else {
            var1 = 12.791919191919195_f64;
        }
    }
    ((var0) + (var1)) * (0.5_f64)
}
