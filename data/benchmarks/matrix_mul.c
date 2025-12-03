#include <stdio.h>
#define N 100

int main() {
    static int a[N][N], b[N][N], c[N][N];

    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            a[i][j] = i + j;
            b[i][j] = i * j;
            c[i][j] = 0;
        }

    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            for (int k = 0; k < N; k++)
                c[i][j] += a[i][k] * b[k][j];

    printf("%d\n", c[N-1][N-1]);
    return 0;
}
