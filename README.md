<h1 align="center" style="font-size: 40px"> WLM - Diamonds!</h1>

<p align="center">
    <img src="WLM.png" align="center">
</p>

## Project Overview

Project ini ditujukan sebagai pemenuhan Tugas Besar 1 IF2211 Strategi Algoritma Semester II tahun 2023/2024. Project ini merupakan implementasi algoritma greedy pada sebuah game engine bernama diamonds diaman kami membuat sebuah logic untuk bot dalam mendapat point terbesar selama waktu yang ditentukan.

## Algorithm Overview

### Algorithm Greedy Implementation

Penggunaan algoritma greedy pada tugas ini berupa pencarian diamond oleh bot secara efektif dan pengkondisian bot sehingga dapat beradaptasi dengan objek-objek disekitarnya. Selain itu, bot juga harus memperhatikan beberapa aspek seperti diamond inventory dan waktu

### How the algorithm works

1. Algorithm akan melakukan kalkulasi untuk tiap objek pada board
2. Objek dengan point terbesar akan dijadikan target oleh bot
3. Terdapat beberapa handle yang dilakukan, diantaranya jika inventory bot sudah penuh dan waktu sudah hampir habis, maka target bot akan berubah menjadi base

## SETUP AND RUNNING BOT

### Setup Game Engine

1. Install node js
   https://nodejs.org/en
2. Install docker desktop
   https://www.docker.com/products/docker-desktop/
3. Install Yarn

```
npm install --global yarn
```

4. Download game Engine code from
   https://github.com/haziqam/tubes1-IF2211-game-engine/releases/tag/v1.1.0
5. Goes to root directory by

```
cd tubes1-IF2110-game-engine-1.1.1.0
```

6. Install dependencies

```
yarn
```

7. Setup default environtment variable by

- For Windows
  ```
  ./scripts/copy-env.bat
  ```
- For Linux
  ```
  chmod +x ./scripts/copy-env.sh
  ./scripts/copy-env.sh
  ```

8. Setup local database <br><b>⚠️ make sure to open the docker desktop first ⚠️</b>

```
docker compose up -d database
```

- For windows
  ```
  ./scripts/setup-db-prisma.bat
  ```
- For Linux or mc os
  ```
  chmod +x ./scripts/setup-db-prisma.sh
  ./scripts/setup-db-prisma.sh
  ```

9. Build or Run <br><b>⚠️ make sure to open the docker desktop first ⚠️</b>

- Build
  ```
  npm run build
  ```
- Run
  ```
  npm run start
  ```

<b>full instructions can be followed from this link below:
https://docs.google.com/document/d/1L92Axb89yIkom0b24D350Z1QAr8rujvHof7-kXRAp7c/edit</b>

### Setup Bot

1. Download the bot script in this repository
2. Make sure to run the Game Engine
3. Open Terminal at the repository
4. Run the bot by:

```
./greedy1.bat
```

## Author :

Special thanks to our contributors :

1. Justin Aditya Putra Prabakti 13522130
2. Muhammad Davis Adhipramana 13522157
3. Muhammad Rasheed Qais Tandjung 13522158</b>
