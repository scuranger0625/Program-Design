#include <stdio.h>

#define MAXN 1005

int a[MAXN];      // # 原始陣列
int b[MAXN];      // # 這次 peak 產生的山
int ans[MAXN];    // # 最佳答案的山

int main() {
    int n;
    scanf("%d", &n);

    // # 讀入原始陣列
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }

    long long best_sum = -1;

    // # 每個位置都試一次當 peak
    for (int peak = 0; peak < n; peak++) {

        // # 先把 peak 自己放進去
        b[peak] = a[peak];

        // # 往左處理
        for (int i = peak - 1; i >= 0; i--) {
            if (a[i] < b[i + 1]) {
                b[i] = a[i];
            } else {
                b[i] = b[i + 1];
            }
        }

        // # 往右處理
        for (int i = peak + 1; i < n; i++) {
            if (a[i] < b[i - 1]) {
                b[i] = a[i];
            } else {
                b[i] = b[i - 1];
            }
        }

        // # 計算這次 mountain 的總和
        long long sum = 0;
        for (int i = 0; i < n; i++) {
            sum += b[i];
        }

        // # 如果更好，就更新答案
        if (sum > best_sum) {
            best_sum = sum;
            for (int i = 0; i < n; i++) {
                ans[i] = b[i];
            }
        }
    }

    // # 輸出最大總和
    printf("%lld\n", best_sum);

    // # 輸出最佳 mountain
    for (int i = 0; i < n; i++) {
        printf("%d", ans[i]);
        if (i != n - 1) {
            printf(" ");
        }
    }
    printf("\n");

    return 0;
}
