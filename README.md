# Mini Roguelike (PgZero)

Um pequeno roguelike em visão superior, feito com **PgZero**.  
Você controla a heroína numa grade de tiles, desviando de inimigos que patrulham seus territórios. Alcance a **porta verde** para vencer!

---

## 🎮 Gameplay

- O mapa é uma grade (grid) de paredes `#` e chão `.`
- O **herói** se move suavemente de **célula em célula**, com **animação de sprite** para `idle` e `walk`
- Existem **múltiplos inimigos** (slimes) com **animação**, que se movem aleatoriamente **apenas dentro de seus territórios**
- Se o herói colidir com um inimigo:
  - Toca **som de dano**
  - O herói muda para estado **hurt** por um instante
  - Em seguida ele é **resetado** para o ponto inicial
- Ao chegar na **porta** (tile verde com maçaneta), você **vence** e aparece a **tela de vitória**

---

## 🕹️ Controles

Durante o jogo (STATE_GAME):
- **A / ←**: mover para a esquerda  
- **D / →**: mover para a direita  
- **W / ↑**: mover para cima  
- **S / ↓**: mover para baixo  
- **M**: alterna **música** (Musica ON/OFF)  
- **N**: alterna **efeitos sonoros** (Sons ON/OFF)  
- **ESC**: volta ao **menu** principal  

Tela de vitória (STATE_WIN):
- **ENTER** ou **ESPAÇO**: volta ao **menu**

Menu principal:
- Botões clicáveis: **Iniciar**, **Audio ON/OFF** (liga/desliga música e efeitos juntos), **Sair do jogo**  
- Dentro do jogo há botões pequenos (HUD) para **Musica ON/OFF**, **Sons ON/OFF** e **Voltar ao início**.

---

## 🧩 Requisitos

- **Python 3.10+**
- **PgZero** (testado com `pgzero==1.2.1`)

---

## 📦 Instalação

1. Clone o repositório:
   ```bash
   https://github.com/Carlamagalhaes1/GameTest.git
   cd GameTest
   
   ```


3. Instale as dependências:
   ```bash
   # Windows
   py -m pip install -r requirements.txt

   # macOS/Linux
   python3 -m pip install -r requirements.txt
   ```

---

## ▶️ Como rodar

O arquivo principal do jogo é **`game.py`**.
  rode com:

  ```bash
  pgzrun game.py
  ```

---

## 🗂️ Estrutura do projeto


**Importante (PgZero):**
- **Sprites**: o código usa `screen.blit("nome_da_imagem", ...)` implicitamente via `screen.blit(img, ...)` em `AnimatedSprite.draw()`, onde `img` é algo como `"hero_idle_left_0"`.  
  Por isso, **os nomes dos arquivos** em `images/` **devem** bater com os nomes formados no código:
  ```
  {name}_{state}_{dir}_{frame}.png
  ```
  Exemplos:
  - `hero_idle_left_0.png`, `hero_idle_left_1.png`
  - `hero_walk_right_0.png`, `hero_walk_right_1.png`
  - `slime_idle_left_0.png`, etc.

- **Sons**: o código toca sons com `sounds.step.play()`, `sounds.hit.play()`, `sounds.win.play()`.  
  Logo, em `sounds/` devem existir: `step.wav`, `hit.wav`, `win.wav`.

- **Música**: o código chama `music.play("bgm")`, então em `music/` deve existir **`bgm.mp3`** (ou `bgm.ogg` / `bgm.wav`).

---

## 🛠️ Solução de problemas

- **“No music found like 'bgm'”**  
  Verifique se o arquivo está em `music/` com nome **`bgm.mp3`** (ou `bgm.ogg`/`bgm.wav`) e sem espaços/acentos no nome.

- **Sprites não aparecem (círculo azul no lugar)**  
  Confira se os nomes **batem exatamente** com o padrão `{name}_{state}_{dir}_{frame}.png`  
  e se estão na pasta `images/`.

- **Erro ao rodar `pgzrun`**  
  Garanta que instalou os requisitos (ver seção Instalação) e que está no **diretório do projeto**:
  ```bash
  cd CAMINHO/DA/SUA/PASTA/GameTest
  pgzrun
  ```

- **Pip desatualizado (aviso)**  
  É só um aviso. Se quiser atualizar:
  ```bash
  py -m pip install --upgrade pip
  ```

---


