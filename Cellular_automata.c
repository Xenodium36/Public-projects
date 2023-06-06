#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>

#define LIVE "#"
#define DEAD " "
#define LEN 201

char states[8][4] = {"111", "110", "101", "100", "011", "010", "001", "000"};
char rule[9];
char stateBefore[LEN];
char stateAfter[LEN];
char stateBeforePrint[LEN];
char stateAfterPrint[LEN];


int kbhit(void)
{
    struct termios oldt, newt;
    int ch;
    int oldf;
 
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
 
    ch = getchar();
 
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);
 
    if(ch != EOF)
    {
        ungetc(ch, stdin);
        return 1;
    }
 
    return 0;
}

void createRule(char c){
    switch (c)
    {
    // rule 30
    case '1':
        strcpy(rule, "00011110");
        return;
    //rule 126
    case '2':
        strcpy(rule, "01111110");
        return;
    //rule  54
    case '3':
        strcpy(rule, "00110110");
        return;
    //rule 150
    case '4':
        strcpy(rule, "10010110");
        return;
    //rule 60
    case '5':
        strcpy(rule, "00111100");
        return;
    //rule 158
    case '6':
        strcpy(rule, "10011110");
        return;
    default:
        break;
    }

}

void generateStart(){
    char *c = "0";
    char *p = DEAD;
    for (int i = 0; i < LEN; i++)
    {   
        if (i == 100)
        {
            c = "1";  p = LIVE;
            strcat(stateBefore, c);
            strcat(stateBeforePrint, p);
            c = "0"; p = DEAD;
            continue;
        }
        
        strcat(stateBefore, c);
        strcat(stateBeforePrint, p);
    }
}

void generateStartRandom()
{
    char *c;
    char *p;
    for (int i = 0; i < LEN; i++)
    {   
        if (rand() > 1150000000) {
            c = "1";
            p = LIVE;
        }
        else {
            c = "0";
            p = DEAD;
        }
        strcat(stateBefore, c);
        strcat(stateBeforePrint, p);
    }
}


int main(){
    char c;
    char state[3];
    int count = 0;
    bool run = true;
    bool expanding = false;
    memset(state, 0, 3);
    srand(time(NULL));
    

    printf("Welcome to simulation of 1D cellular automat\n");
	printf("Once the simulation is running, press q to end it...\n");
    printf("Pick your rule:\n\t1: rule 30\n\t2: rule 126\n\t3: rule 54\n\t4: rule 150\n\t5: rule 60\n\t6: rule 158\n\t7: write your own rule\n\t8: exit program\n");

    printf("Write number 1 - 8: ");
    while (true)
    {
        c = getchar();
        if(c > '0' && c <= '7'){
            break;
        }else if(c == '8'){
            printf("Exiting...\n");
            return 0;
        }else{
            printf("Wrong input. Write number between 1 - 8: ");
        }       
    }
    
    if (c == '7'){ 
        printf("Insert your own rule (sequence of 0/1 of size 7), or enter 9 for exit: ");
        c = getchar();
        while (run){    
            for (int i = 0; i < 7; i++)
            {   
                c = getchar();
                if (c == '0' || c == '1'){
                    strncat(rule, &c, 1);
                }else if(c == '9'){
                    printf("Exiting...\n");
                    exit(0);
                }else{
                    printf("Invalid symbol in rule... Write it again please: ");
                    run = true;
                    break;
                }
                run = false;
            }  
        }
        c = '0';
        strcat(rule, &c);
    }else{
        createRule(c);
    }

    printf("Select start:\n\t1: random start (sample size is fixed to 200)\n\t2: 1 alive cell(expanding to 200 cells)\n\t3: exit program\n");
	printf("Write number 1 - 3: ");
    while (c != '\n'){
        c = getchar();
    }
    while (true){
        c = getchar();
        if (c == '1'){
            generateStartRandom();
            break;
        } else if (c == '2'){
            generateStart();
            expanding = true;
            break;
        } else if (c == '3'){
            printf("Exiting...\n");
            return 0;
        } else{
            printf("Wrong input. Write number between 1 - 3: ");
        } 
    }
  
    
     
    printf("%s", stateBeforePrint);
    while(true){
        if (expanding == true && 100 == count++) 
            break;
        for (int i = -1; i < 199; i++)
        {   
            if(i == -1){
                strncat(state, &stateBefore[strlen(stateBefore)-1], 1);
                strncat(state, &stateBefore[0], 2);
            }else if(i == 198){
                strncat(state, &stateBefore[i], 2);
                strncat(state, &stateBefore[0], 1);
            }else{
                strncpy(state, &stateBefore[i], 3);
            }         
            for (int j = 0; j < 8; j++)
            {
                if(strcmp(state, states[j]) == 0){
                    strncat(stateAfter, &rule[j], 1);
                    if(rule[j] == '1') strcat(stateAfterPrint, LIVE);
                    else strcat(stateAfterPrint, DEAD);
                    break;
                }
            }       
            memset(state, 0, 3); 
        }
        usleep(150000);
        printf("\n%s", stateAfterPrint);  
        strcpy(stateBefore, stateAfter);
        strcpy(stateBeforePrint, stateAfterPrint);
        memset(stateAfter, 0, 201); 
        memset(stateAfterPrint, 0, 201);
        if (kbhit()){
            c = getchar();
            if (c == 'q') 
                break;
        }
    }
    printf("\nExiting program...\n");
    return 0;
}