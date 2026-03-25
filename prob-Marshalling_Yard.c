#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int id;                 // 車廂編號
    struct Node *prev;      // 前一個節點
    struct Node *next;      // 下一個節點
} Node;

Node *pos[200001];          // pos[x] 直接找到編號 x 的車廂節點

// 把節點 x 從目前位置拆下來
void remove_node(Node *x) {
    x->prev->next = x->next;
    x->next->prev = x->prev;
}

// 把節點 x 插到節點 y 的後面
void insert_after(Node *y, Node *x) {
    x->next = y->next;
    x->prev = y;
    y->next->prev = x;
    y->next = x;
}

int main() {
    int n, q;
    scanf("%d %d", &n, &q);

    // 建立假頭(head)與假尾(tail)，方便操作
    Node *head = (Node *)malloc(sizeof(Node));
    Node *tail = (Node *)malloc(sizeof(Node));
    head->prev = NULL;
    head->next = tail;
    tail->prev = head;
    tail->next = NULL;

    // 初始串列：head <-> 1 <-> 2 <-> ... <-> n <-> tail
    Node *cur = head;
    for (int i = 1; i <= n; i++) {
        Node *node = (Node *)malloc(sizeof(Node));
        node->id = i;

        // 接到目前尾端
        node->prev = cur;
        node->next = tail;
        cur->next = node;
        tail->prev = node;

        pos[i] = node;      // 記住編號 i 的節點位置
        cur = node;
    }

    // 處理 q 次操作
    for (int i = 0; i < q; i++) {
        char op;
        scanf(" %c", &op);

        if (op == 'F') {
            int x;
            scanf("%d", &x);

            Node *X = pos[x];

            // 若已經在最前面，照做也沒差；直接拆再插
            remove_node(X);
            insert_after(head, X);
        }
        else if (op == 'B') {
            int x;
            scanf("%d", &x);

            Node *X = pos[x];

            // 插到最後面 = 插到 tail->prev 的後面
            remove_node(X);
            insert_after(tail->prev, X);
        }
        else if (op == 'A') {
            int x, y;
            scanf("%d %d", &x, &y);

            Node *X = pos[x];
            Node *Y = pos[y];

            // 先拆掉 x，再插到 y 後面
            remove_node(X);
            insert_after(Y, X);
        }
    }

    // 輸出最後結果（從左到右）
    Node *p = head->next;
    while (p != tail) {
        printf("%d", p->id);
        if (p->next != tail) {
            printf(" ");
        }
        p = p->next;
    }
    printf("\n");

    return 0;
}
