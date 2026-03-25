#include <stdio.h>

#define MAX 10005

// parent[i] = i 的父節點
int parent[MAX];

// 找根節點（路徑壓縮）
int find_set(int x) {
    if (parent[x] != x) {
        parent[x] = find_set(parent[x]);
    }
    return parent[x];
}

// 合併兩個集合
void union_set(int a, int b) {
    int rootA = find_set(a);
    int rootB = find_set(b);

    if (rootA != rootB) {
        parent[rootB] = rootA;
    }
}

int main() {
    int n, m;
    scanf("%d %d", &n, &m);

    int sx, sy, ex, ey;
    scanf("%d %d %d %d", &sx, &sy, &ex, &ey);

    char grid[105][105];

    // 讀地圖
    for (int i = 0; i < n; i++) {
        scanf("%s", grid[i]);
    }

    // 如果起點或終點是牆，直接不可能
    if (grid[sx][sy] == '#' || grid[ex][ey] == '#') {
        printf("NO\n");
        return 0;
    }

    // 初始化並查集
    // 總共有 n*m 個格子，編號 0 ~ n*m-1
    for (int i = 0; i < n * m; i++) {
        parent[i] = i;
    }

    // 掃整張圖，把相鄰且可走的格子 union 起來
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {

            // 牆不能參與連通
            if (grid[i][j] == '#') {
                continue;
            }

            int current_id = i * m + j;

            // 檢查下方
            if (i + 1 < n && grid[i + 1][j] != '#') {
                int down_id = (i + 1) * m + j;
                union_set(current_id, down_id);
            }

            // 檢查右方
            if (j + 1 < m && grid[i][j + 1] != '#') {
                int right_id = i * m + (j + 1);
                union_set(current_id, right_id);
            }
        }
    }

    // 起點編號
    int start_id = sx * m + sy;

    // 終點編號
    int end_id = ex * m + ey;

    // 判斷是否在同一個集合
    if (find_set(start_id) == find_set(end_id)) {
        printf("YES\n");
    } else {
        printf("NO\n");
    }

    return 0;
}
