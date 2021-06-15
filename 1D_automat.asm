;Autor: Dominik Haršaník
;Login: xharsa01
;Pravidlo 30
;Verzia:1.0
;Dátum: 29.04.2020
;Program vykresluje simulaciu 1D celulárneho automatu. Vstup je bezznamienkové 32 bitové èíslo, pokia¾ je èíslo menšie ako 10, nastaví 
;sa hodnota 10, pokia¾ je väèšie ako 100, nastaví sa hodnota 100.
;Program si na zaèiatku sám náhodne vygeneruje poèiatoèný stav buniek pomocou použitia C funkcií.
;Ascii znak è. 7 = živá bunka -> 1 v poli
;Ascii znak è. 8 = màtva bunka -> 0 v poli

%include "rw32-2020.inc"

extern _time        ;inicializacia C funkcie "time"
extern _srand       ;inicializacia C funkcie "srand"
extern _rand        ;inicializacia C funkcie "rand"

section .data
    size dd 256     ;inicializacia premennej "size" o velkosti 32bitov hodnotou 256
    pole_pred times 101 db 0    ;inicializacia pola o velkosti 101 a velkosti jednej hodnoty 8bitov hodnotou "0", 
    pole_po times 101 db 0  ;inicializacia druheho pola o velkosti 101 a velkosti jednej hodnoty 8bitov hodnotou "0"
    cmp_in db 111b, 110b, 101b, 100b, 011b, 010b, 001b, 000b    ;pole na porovnavanie hodnot tych 3 buniek vedla seba
    cmp_out db 0,0,0,1,1,1,1,0      ;pravidlo 30, teoreticky, ak sa prepise na pravidlo 60/90/120, malo by to tiez fungovat
section .bss
    ; zde budou vase neinicializovane data

section .text
_main:
    push ebp
    mov ebp, esp
    sub esp, 4  ;omyl, mala byt povodne lokalna premenna, nechce sa mi odstranovat, potom to nefunguje, nemam na to dostatok casu
    mov edi, pole_pred  ;zadanie adresy pola "pole_pred" do edi
    mov esi, pole_po    ;zadanie adresy pola "pole_po" do esi
    
    call ReadUInt32     ;Nacitanie bezznamienkoveho cisla zo vstupu do eax
    call WriteNewLine   ;vypisanie noveho riadku
    cmp eax, 10         ;porovnananie zadaneho cisla s konstantou 10
    jb below            ;pokial je mensie, skoc na "below", inac pokracuj
    cmp eax, 100        ;porovnananie zadaneho cisla s konstantou 100
    ja above            ;pokial je vacsie, skoc na "above", inac pokracuj
    
    mov [size], eax     ;nastav premennu "size" na zadavne cislo
    jmp ok              ;skoc na "ok"
  below:
    mov [size], dword 10    ;nastav "size" na 10
    jmp ok              ;skoc na ok
  above:
    mov [size], dword 100   ;nastav "size" na 100
    
  ok:
    push dword[size]    ;zadanie premennej funkcii
    call PrintRandom    ;volanie funkcie (riadok 279)
    add esp, 4  ;odstranenie pushnutej premennej zo zasobniku
        
    xor eax, eax        ;vynulovanie eax
    mov ebx, [size]     ;presunutie velkosti pola do registru ebx
    mov ecx, cmp_in     ;presunutie adresy pola cmp_in do registru ecx
    mov edx, cmp_out    ;presunutie adresy pola cmp_out do registru ecx  
 while1: ;cyklus "while1", cize vzdy prebehne za ucelom nekonecneho vypisovania riadkov

    call porovnanie ;zavolanie funkcie porovnanie, vysvetlenie nad funkciou
    call vypis  ;zavolanie funkcie vypis, vysvetlenie nad funkciou
    
    call copy_arr   ;zavolanie funkcie copy_arr, vysvetlenie nad funkciou
      
    call WriteNewLine       ;vypisanie noveho riadku
    jmp while1      ;jump na "while1", vzdy prebehne
    
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec programu
        
;############################################################################
;############################################################################
;############################################################################
;############################################################################
;funkcia na porovnanie buniek
;na zaciatku manualne porovnam predposlednu-poslednu-prvu a zapisem hodnotu do poslednej bunky
; a poslednu-prvu-druhu a zapisem do prvej bunky, cize kruhove pole
;nenapadol ma ziadny iny sposob narychlo
;potom v cykle porovnam zvysne moznosti
;Funkcionalita:
;pozre sa na bunku pred, ak zije, zapise 1 do lokalnej premennej a shift do lava, ak je mrtva, iba shift,
;cize dostanem hodnoty 0-7 v lokalnej premennej, danu hodnotu porovnavam s hodnotou v poli pole_pred 
porovnanie:
    push ebp    ;zaloha stareho dna zasobniku
    mov ebp, esp ; ebp sa stava novym dnom zasobniku
    sub esp, 12      ;odpocitanie od dna zasobniku za ucelom vytvorenia 2 32b lokalnych premennych
    mov [ebp - 4], dword 0  ;vytvorenie lokalnej premennej a priradenie jej hodnoty 0
    mov [ebp - 8], dword 0  ;vytvorenie lokalnej premennej a priradenie jej hodnoty 0
    
    mov al, byte [edi + ebx - 2]    ;prekopirovanie predposlednej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0a   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0a(nahodny nazov)
    add [ebp - 8], byte 1 ;ak je ziva, k lokalnej premennej sa pripocita 1 
  je_0a:
    mov al, byte [edi + ebx - 1]    ;prekopirovanie poslednej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0b   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0b(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp last1   ;skoc na odkaz last1
  je_0b:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  last1:
    mov al, byte [edi]  ;prekopirovanie prvej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0c   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0c(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp comp1   ;skoc na odkaz comp1
  je_0c:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  comp1:
    xor eax, eax ;vynulovanie eax za ucelom jeho buduceho pouzitia
    mov al, [ebp - 8]   ;presunutie stavu 3 buniek do registru al
    call pos    ;zavolanie funkcie pos
    push ecx    ;zaloha povodneho ecx za ucelom dalsieho pouzitia
    mov cl, byte [edx + eax]    ;nakopirovanie hodnoty z pole_po na indexe eax, co je zisteni index vo funkcii pos
    mov [esi + ebx - 1], cl     ;nakopirovanie daneho stavu do pole_po na posledny index
    xor al, al  ;vynulovanie al
    mov [ebp - 8], dword 0  ;vynulovanie lokalnej premennej
    pop ecx ;obnovenie povodneho ecx, cize adresy na pole
     
    mov al, byte [edi + ebx - 1]    ;prekopirovanie poslednej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0d   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0d(nahodny nazov)
    add [ebp - 8], byte 1
  je_0d:
    mov al, byte [edi]  ;prekopirovanie prvej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0e   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0e(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp last2   ;skoc na odkaz last2
  je_0e:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  last2:
    mov al, byte [edi + 1]  ;prekopirovanie druhej hodnoty pola "pole_pred" do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0f   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0f(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp comp2   ;skoc na odkaz comp2
  je_0f:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  comp2:
    xor eax, eax    ;vynulovanie eax za ucelom jeho buduceho pouzitia
    mov al, [ebp - 8]   ;presunutie stavu 3 buniek do registru al
    call pos    ;zavolanie funkcie pos
    push ecx    ;zaloha povodneho ecx za ucelom dalsieho pouzitia
    mov cl, byte [edx + eax]    ;nakopirovanie hodnoty z pole_po na indexe eax, co je zisteni index vo funkcii pos
    mov [esi], cl   ;nakopirovanie stavu bunky z indexu eax do pole_po
    xor al, al  ;vynulovanie eax
    mov [ebp - 8], dword 0  ;vynulovanie lokalnej premennej
    pop ecx ;obnovenie povodneho ecx, cize adresy na pole
    
   
    push ebx    ;zaloha povodneho ebx za ucelom dalsieho pouzitia
    sub ebx, 3  ;znizenie [size] o 3, kedze prehladavam bunku a dalsie 2 po nej
  for1:     ;cyklus na prehladavanie pola s informaciou o bunkach      
    push edx    ;zaloha povodneho edx za ucelom dalsieho pouzitia
    mov edx, [ebp - 4]  ;pocitadlo, priradenie 0
    mov al, byte [edi + edx]    ;prekopirovanie hodnoty pola "pole_pred" na indexe edx do al
    cmp al, 1  ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0g   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0g(nahodny nazov)
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
  je_0g:
    mov al, byte [edi + edx + 1] ;prekopirovanie hodnoty pola "pole_pred" na indexe edx + 1 do al
    cmp al, 1 ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0h   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0h(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp last3   ;skoc na odkaz last3
  je_0h:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  last3:
    mov al, byte [edi + edx + 2]    ;prekopirovanie hodnoty pola "pole_pred" na indexe edx + 2do al
    cmp al, 1   ;porovnanie stavu danej bunky s 1, cize ci je ziva
    jne je_0i   ;ak je mrtva, teda hodnota je 0, tak skoci na je_0i(nahodny nazov)
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
    add [ebp - 8], byte 1   ;ak je ziva, k lokalnej premennej sa pripocita 1 
    jmp comp3   ;skoc na odkaz comp3
  je_0i:
    shl byte [ebp - 8], 1   ;posun lokalnu premennu o 1 bit dolava
  comp3:
    xor eax, eax    ;vynulovanie eax
    mov al, [ebp - 8]   ;presunutie stavu 3 buniek do registru al
    call pos    ;zavolanie funkcie pos
    mov [ebp - 12], edx ;nedostatok registrov, preto zaloha edx do lokalnej premennej
    pop edx ;obnovenie povodneho edx, cize adresy na pole
    push ecx    ;zaloha povodneho ecx za ucelom dalsieho pouzitia
    mov cl, byte [edx + eax]    ;nakopirovanie hodnoty z pole_pred na indexe eax, co je zisteni index vo funkcii pos
    push edx    ;zaloha povodneho edx za ucelom dalsieho pouzitia
    mov edx, [ebp - 12] ;prekopirovanie z lokalnej premennej naspat do edx
    mov [esi + edx + 1], cl ;nakopirovanie hodnoty z cl do pole_po na indexe edx + 1
    xor al, al  ;vynulovanie al
    mov [ebp - 8], dword 0  ;vynulovanie lokalnej premennej 
    pop edx ;obnovenie povodneho edx, cize adresy na pole
    pop ecx ;obnovenie povodneho ecx, cize adresy na pole
        
    add [ebp - 4], byte 1   ;pripocitanie 1 k lokalnej premennej
    cmp [ebp - 4], ebx     ;porovnanie lokalnej premennej s registrom ebx, cime mojim poctom buniek v 1 riadku
    jng for1                ;prebehne, kym sa ebx a lokalna premenna nerovnaju
    
    pop ebx ;obnovenie povodneho ebx, cize velkosti pola
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec funkcie
    
;############################################################################
;############################################################################
;############################################################################
;############################################################################
;funkcia len zisti poziciu stavu 3 buniek v poli pole_in, za ucelom zistenia indexy stavu novej bunky v poli pole_out
pos:
    push ebp    ;zaloha stareho dna zasobniku
    mov ebp, esp ; ebp sa stava novym dnom zasobniku
    push ebx    ;zaloha ebx, za ucelom pouzitia vo funkcii 
    mov ebx, dword -1   ;nastavenie pocitadla/ebx na -1 ako pocitadlo pre cyklus
  for2:
    add ebx, dword 1    ;incrementacia pocitadla/ebx o 1
    cmp al,[ecx + ebx]  ;porovnanie zisteneho stavu trojice buniek so stavmi v poli cmp_in a zistenie indexu
    jne for2    ;skok prebehne, kym sa tie hodnoty nerovnaju
    
    mov al, bl  ;ulozenie indexu do al 
    pop ebx     ;obnovenie povodnej hodnoty z ebx
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec funkcie
    
;############################################################################
;############################################################################
;############################################################################
;############################################################################
;funkcia vypisuje pretransformovane hodnoty z pole_po na vystup
vypis:
    push ebp    ;zaloha stareho dna zasobniku
    mov ebp, esp ; ebp sa stava novym dnom zasobniku
    push edx    ;zaloha edx, za ucelom pouzitia vo funkcii
    push ebx    ;zaloha ebx, za ucelom pouzitia vo funkcii
    mov edx, - 1    ;nastavenie pocitadla/edx na -1 ako pocitadlo pre cyklus
    sub ebx, 1  ;znicenie [size] o 1 kvoli korektnosti cyklu
  for3:
    add edx, 1  ;incrementacia pocitadla/edx o 1
    mov al, [esi + edx] ;presun hodnoty z pole_po na indexe pocitadla do al
    cmp al, 1   ;porovnanie danej hodnoty s 
    jne mrtva   ;pokial sa nerovna , bunka je mrtva a skoci na odkaz mrtva
    mov al, 7   ;pokial je ziva, nastavi sa ascii hodnota 7
    jmp ziva    ;a skoci na odkaz ziva
  mrtva: 
    mov al, 8  ;pokial je mrtva, nastavi sa ascii hodnota 8
  ziva:
    call WriteChar  ;vypise sa ascii znak na vystup, berie si to z al
    cmp edx, ebx    ;porovnanie pocitadla s velkostou pola
    jb for3 ;kym, je mensie, skoci na for3
    
    xor al, al  ;vynulovanie registru al, aby sa nezmenil
    pop ebx ;obnovenie ebx
    pop edx ;obnovenie edx
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec funkcie
    
    
;############################################################################
;############################################################################
;############################################################################
;############################################################################
;funkcia prekopiruje hodnoty z pole_pred do pole_po
;nechcel som pouzit rep movsb, pretoze to kopirovalo adresy, nie hodnoty
copy_arr:
    push ebp    ;zaloha stareho dna zasobniku
    mov ebp, esp ; ebp sa stava novym dnom zasobniku
    push eax    ;zaloha eax, za ucelom pouzitia vo funkcii
    push edx    ;zaloha edx, za ucelom pouzitia vo funkcii
    xor edx, edx    ;vynulovanie edx
    mov eax, -1     ;nastavenie eax na -1 ako pocitadlo pre cyklus
    
  for4:
    add eax, 1  ;incrementacia pocitadla/eax o 1
    mov dl, byte [esi + eax]    ;presun hodnoty z pola_pred na indexe eax do dl
    mov [edi + eax], dl ;presun do pole_pred na index eax z dl
    cmp eax, ebx    ;porovnanie pocitadla s velkostou pola 
    jb for4 ;kym je mensie, skoci
    
    pop edx ;obnovenie edx
    pop eax ;obnovenie eax
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec funkcie

;############################################################################
;############################################################################
;############################################################################
;############################################################################
;funkcia generuje random cisla, pokial je mensie ako 10000, tak nastavi 0, inak nastavi 1
PrintRandom:
    push ebp    ;zaloha stareho dna zasobniku
    mov ebp, esp ; ebp sa stava novym dnom zasobniku
    call _time  ;volanie C funkcie "time", funcia si berie pushnutu premennu, vystup je v eax 
    
    push eax    ;zadanie premennej funkcii
    call _srand ;volanie C funkcie "srand", funcia si berie pushnutu premennu,
    add esp, 4  ;odstranenie pushnutej premennej zo zasobniku
  
    mov ecx, -1 ;nastavenie ecx hodnoty pre cyklus na -1
    dec dword [ebp + 8] ;decrementacia pusnutej premennej o 1, cize v podstate dec eax/[size], 1
 for: 
    add ecx, 1  ;incrementacia ecx pre chod cyklu
    push ecx    ;zadanie premennej funkcii
    call _rand  ;volanie C funkcie "rand", funcia si berie pushnutu premennu, vygenerovane cislo je v eax
    pop ecx     ;odstranenie premennej 
    cmp eax, 12000 ;porovnanie vystupu funkcie "rand" s cislom 12000 (nahodne urcene podla toho, ake cisla mi to generovalo) 
    ja vacsie   ;pokial je vacsie ako 12000, skoci na odkaz vacsie
    mov eax, 0  ;pokial je mensie, nastavi 0
    jmp copy    ;a preskoci skok vacsie 
  vacsie:
    mov eax, 1  ;pokial je vacsie, nastavi 1
  copy:
    mov [edi + ecx], eax    ;prekopirovanie danej hodnoty do pola "pole_pred" na index urceny hodnotou ecx
    
    cmp ecx, [ebp + 8]  ;porovnanie pocitadla ecx s mojou zadanou velkostou na vstupe
    jb for ;pokial je mensie, skoci na cysklus for
    
    mov esp, ebp ;obnovenie dna zasobniku
    pop ebp ;obnovenie stareho dna
    ret ;koniec funkcie
