#include <stdio.h>
#include <stdlib.h>

long long gold[100005];

// # 回傳區間 [l, r] 的最終冠軍金額
long long solve(int l, int r) {

    // # 如果這區只有一位戰士，直接晉級
    if (l == r) {
        return gold[l];
    }

    // # 題目規則：左邊是 ceil(M/2)，右邊是 floor(M/2)
    // # 用這個 mid 可以自然做到
    int mid = (l + r) / 2;

    // # 先算左半冠軍
    long long L = solve(l, mid);

    // # 再算右半冠軍
    long long R = solve(mid + 1, r);

    // # 規則 A：差距 <= 100，左邊贏
    if (llabs(L - R) <= 100) {
        return L + R + 50;
    }

    // # 規則 B：差距 > 100，金額大的贏，拿對手一半
    if (L > R) {
        return L + R / 2;
    } else {
        return R + L / 2;
    }
}

int main() {
    int n;
    scanf("%d", &n);

    for (int i = 0; i < n; i++) {
        scanf("%lld", &gold[i]);
    }

    printf("%lld\n", solve(0, n - 1));

    return 0;
}