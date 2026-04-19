#include <stdio.h>

int n,k;
int path[20];

void dfs(int start,int depth){
    if(depth==k){
        for (int i=0; i<k ;i++) {
            printf("%d",path[i]); // 如果選滿 k 個 → 印出
            if (i != k-1){
                printf(" ");
            }

        }
        printf("\n");
        return;
    }

    
    for(int i=start; i<=n; i++){  // 從 start 開始選
        path[depth]=i;            // 選 i
        dfs(i+1,depth+1);         // 下一層只能選更大的
        }
    }
int main(){
    scanf("%d %d",&n,&k);
    dfs(1, 0); // 從 1 開始，還沒選任何數
    return 0;
}
