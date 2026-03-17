#include <stdio.h>
#include <string.h>

char s[10];   // s: 原始字符串 例如 abc
int used[10]; // used: 用來標記字元是否已經被使用過
char perm[10]; // perm: 目前DFS走到這一層所形成的字串
int n; // n: 字串長度

void dfs(int depth) {
    if (depth == n){
        perm[depth] = '\0'; // 在字串結尾添加終止符號
        printf("%s\n", perm); // 輸出當前的排列
        return;
    }


    for(int i=0; i<n; i++){
        // 如果當前字元沒有被使用過   ! 為 Logical NOT 運算符，表示取反，即當 used[i] 為 0（未使用）時，條件成立
        if (!used[i]) {
            used[i] = 1; // 標記當前字元為已使用
            perm[depth] = s[i]; // 將當前字元加入到 perm 中
            dfs(depth + 1); // 繼續遞迴，進入下一層
            used[i] = 0; // dfs回溯後，將當前字元標記為未使用，讓下一次迴圈可以再次使用這個字元
        }
    }

}

int main() {

    scanf("%d", &n); // 讀取輸入的字串長度
    scanf("%s", s); // 讀取輸入的字串
    dfs(0); // 從深度0開始進行DFS
    return 0;

}
