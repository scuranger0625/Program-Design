#include <stdio.h>

int main() {
    int a, b, N;
    scanf("%d %d %d", &a, &b, &N);

    long long active[30] = {0};

    /*
        active[i] 表示第 i 週「已經 active」的病毒總數。

        題目規則：
        1. 一開始 a 隻病毒在 Week 1 醒來，但還不能算 active。
        2. 它們要成長 2 週。
        3. 到 Week 3 才變成 active。
        4. active 的病毒需要 1 full week 生產。
           例如：
           Week 3 active
           Week 4 生出新病毒
        5. 新病毒再成長 2 週。
           例如：
           Week 4 出生
           Week 5 成長第 1 週
           Week 6 變 active
    */

    if (N == 1 || N == 2) {
        printf("0\n");
        return 0;
    }

    active[1] = 0;   // Week 1：剛醒來，還在成長，不 active
    active[2] = 0;   // Week 2：還在成長，不 active
    active[3] = a;   // Week 3：一開始的 a 隻病毒變 active

    /*
        DP 關係式：

        active[i] = active[i - 1] + b * active[i - 3]

        active[i - 1]：
            上一週已經 active 的病毒，這週仍然 active。

        b * active[i - 3]：
            第 i-3 週已經 active 的病毒，
            會在第 i-2 週生出新病毒，
            這些新病毒經過 2 週成長，
            到第 i 週變 active。
    */
    for (int i = 4; i <= N; i++) {
        active[i] = active[i - 1] + b * active[i - 3];
    }

    printf("%lld\n", active[N]);

    return 0;
}