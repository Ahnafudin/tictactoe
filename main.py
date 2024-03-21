import copy
import sys
import pygame
import random
import numpy as np
import pygame.mixer
from config import *


# Persiapan Pygame
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill(WARNA_BG)

# Load sound effects
move_sound = pygame.mixer.Sound("sounds/move.mp3")
win_sound = pygame.mixer.Sound("sounds/win.mp3")
tie_sound = pygame.mixer.Sound("sounds/tie.mp3")

# Kelas-kelas
class Papan:
    def __init__(self):
        self.kotak = np.zeros((BARIS, KOLOM))
        self.kotak_terisi = 0

    def status_akhir(self, tampilkan=False):
        for kolom in range(KOLOM):
            if self.kotak[0][kolom] == self.kotak[1][kolom] == self.kotak[2][kolom] != 0:
                if tampilkan:
                    warna = WARNA_LINGKARAN if self.kotak[0][kolom] == 2 else WARNA_SILANG
                    pygame.draw.line(screen, warna, (kolom * UKURAN_KOTAK + UKURAN_KOTAK // 2, 20), (kolom * UKURAN_KOTAK + UKURAN_KOTAK // 2, TINGGI - 20), LEBAR_GARIS)
                return self.kotak[0][kolom]

        for baris in range(BARIS):
            if self.kotak[baris][0] == self.kotak[baris][1] == self.kotak[baris][2] != 0:
                if tampilkan:
                    warna = WARNA_LINGKARAN if self.kotak[baris][0] == 2 else WARNA_SILANG
                    pygame.draw.line(screen, warna, (20, baris * UKURAN_KOTAK + UKURAN_KOTAK // 2), (LEBAR - 20, baris * UKURAN_KOTAK + UKURAN_KOTAK // 2), LEBAR_GARIS)
                return self.kotak[baris][0]

        if self.kotak[0][0] == self.kotak[1][1] == self.kotak[2][2] != 0:
            if tampilkan:
                warna = WARNA_LINGKARAN if self.kotak[1][1] == 2 else WARNA_SILANG
                pygame.draw.line(screen, warna, (20, 20), (LEBAR - 20, TINGGI - 20), LEBAR_SILANG)
            return self.kotak[1][1]

        if self.kotak[2][0] == self.kotak[1][1] == self.kotak[0][2] != 0:
            if tampilkan:
                warna = WARNA_LINGKARAN if self.kotak[1][1] == 2 else WARNA_SILANG
                pygame.draw.line(screen, warna, (20, TINGGI - 20), (LEBAR - 20, 20), LEBAR_SILANG)
            return self.kotak[1][1]

        return 0

    def tandai_kotak(self, baris, kolom, pemain):
        self.kotak[baris][kolom] = pemain
        self.kotak_terisi += 1

    def kotak_kosong(self, baris, kolom):
        return self.kotak[baris][kolom] == 0

    def dapatkan_kotak_kosong(self):
        return [(baris, kolom) for baris in range(BARIS) for kolom in range(KOLOM) if self.kotak_kosong(baris, kolom)]

    def penuh(self):
        return self.kotak_terisi == 9

class KecerdasanBuatan:
    def __init__(self, level=1, pemain=2):
        self.level = level
        self.pemain = pemain

    def acak(self, papan):
        kotak_kosong = papan.dapatkan_kotak_kosong()
        return random.choice(kotak_kosong) if kotak_kosong else None

    def minimax(self, papan, memaksimalkan):
        kasus = papan.status_akhir()

        if kasus == 1:
            return 1, None
        if kasus == 2:
            return -1, None
        if papan.penuh():
            return 0, None

        fungsi_eval = max if memaksimalkan else min
        nilai_eval_terbaik = -100 if memaksimalkan else 100
        langkah_terbaik = None

        for baris, kolom in papan.dapatkan_kotak_kosong():
            papan_temp = copy.deepcopy(papan)
            papan_temp.tandai_kotak(baris, kolom, 1 if memaksimalkan else self.pemain)
            nilai_evaluasi, _ = self.minimax(papan_temp, not memaksimalkan)
            nilai_eval_terbaik, langkah_terbaik = fungsi_eval(nilai_eval_terbaik, nilai_evaluasi), (baris, kolom) if fungsi_eval(nilai_eval_terbaik, nilai_evaluasi) == nilai_evaluasi else langkah_terbaik

        return nilai_eval_terbaik, langkah_terbaik

    def evaluasi(self, papan_utama):
        if self.level == 0:
            nilai_evaluasi, langkah = 'acak', self.acak(papan_utama)
        else:
            nilai_evaluasi, langkah = self.minimax(papan_utama, False)
        print(f'AI memilih untuk menandai kotak di posisi {langkah} dengan evaluasi: {nilai_evaluasi}')
        return langkah

class Permainan:
    def __init__(self):
        self.papan = Papan()
        self.kecerdasan_buatan = KecerdasanBuatan()
        self.pemain = 1
        self.mode_permainan = 'pvp'
        self.berjalan = True
        self.tampilkan_garis()
        self.abu_abu_overlay = pygame.Surface((LEBAR, TINGGI))  # Buat permukaan untuk mengaburkan layar
        self.abu_abu_overlay.set_alpha(200)

    def tampilkan_garis(self):
        screen.fill(WARNA_BG)
        pygame.draw.line(screen, WARNA_GARIS, (UKURAN_KOTAK, 0), (UKURAN_KOTAK, TINGGI), LEBAR_GARIS)
        pygame.draw.line(screen, WARNA_GARIS, (LEBAR - UKURAN_KOTAK, 0), (LEBAR - UKURAN_KOTAK, TINGGI), LEBAR_GARIS)
        pygame.draw.line(screen, WARNA_GARIS, (0, UKURAN_KOTAK), (LEBAR, UKURAN_KOTAK), LEBAR_GARIS)
        pygame.draw.line(screen, WARNA_GARIS, (0, TINGGI - UKURAN_KOTAK), (LEBAR, TINGGI - UKURAN_KOTAK), LEBAR_GARIS)
    
    def tampilkan_notifikasi(self, pesan):
        font = pygame.font.SysFont(None, 50)
        teks = font.render(pesan, True, (255, 255, 255))
        teks_rect = teks.get_rect(center=(LEBAR // 2, TINGGI // 2))  # Mendapatkan area teks dan mengatur posisi rata tengah
        screen.blit(teks, teks_rect)

    def tampilkan_hasil(self):
        screen.blit(self.abu_abu_overlay, (0, 0))

        hasil = self.papan.status_akhir()
        if hasil == 1:
            win_sound.play()
            self.tampilkan_notifikasi('X Menang!')
        elif hasil == 2:
            win_sound.play()
            self.tampilkan_notifikasi('O Menang!')
        else:
            tie_sound.play()
            self.tampilkan_notifikasi('Permainan Seri!')


    def gambar_figure(self, baris, kolom):
        if self.pemain == 1:
            start_desc = (kolom * UKURAN_KOTAK + PERGESERAN, baris * UKURAN_KOTAK + PERGESERAN)
            end_desc = (kolom * UKURAN_KOTAK + UKURAN_KOTAK - PERGESERAN, baris * UKURAN_KOTAK + UKURAN_KOTAK - PERGESERAN)
            pygame.draw.line(screen, WARNA_SILANG, start_desc, end_desc, LEBAR_SILANG)
            start_asc = (kolom * UKURAN_KOTAK + PERGESERAN, baris * UKURAN_KOTAK + UKURAN_KOTAK - PERGESERAN)
            end_asc = (kolom * UKURAN_KOTAK + UKURAN_KOTAK - PERGESERAN, baris * UKURAN_KOTAK + PERGESERAN)
            pygame.draw.line(screen, WARNA_SILANG, start_asc, end_asc, LEBAR_SILANG)
        elif self.pemain == 2:
            center = (kolom * UKURAN_KOTAK + UKURAN_KOTAK // 2, baris * UKURAN_KOTAK + UKURAN_KOTAK // 2)
            pygame.draw.circle(screen, WARNA_LINGKARAN, center, JARI_JARI, LEBAR_LINGKARAN)

    def lakukan_langkah(self, baris, kolom):
        self.papan.tandai_kotak(baris, kolom, self.pemain)
        self.gambar_figure(baris, kolom)
        move_sound.play()  # Play move sound effect
        self.ganti_giliran()

    def ganti_giliran(self):
        self.pemain = self.pemain % 2 + 1

    def ubah_mode_permainan(self):
        self.mode_permainan = 'ai' if self.mode_permainan == 'pvp' else 'pvp'

    def selesai(self):
        return self.papan.status_akhir(tampilkan=True) != 0 or self.papan.penuh()

    def reset(self):
        self.__init__()

def main():
    permainan = Permainan()
    papan = permainan.papan
    kecerdasan_buatan = permainan.kecerdasan_buatan

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    permainan.ubah_mode_permainan()
                if event.key == pygame.K_r:
                    permainan.reset()
                    papan = permainan.papan
                    kecerdasan_buatan = permainan.kecerdasan_buatan
                if event.key == pygame.K_0:
                    kecerdasan_buatan.level = 0
                if event.key == pygame.K_1:
                    kecerdasan_buatan.level = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                posisi = event.pos
                baris = posisi[1] // UKURAN_KOTAK
                kolom = posisi[0] // UKURAN_KOTAK
                if papan.kotak_kosong(baris, kolom) and permainan.berjalan:
                    permainan.lakukan_langkah(baris, kolom)
                    if permainan.selesai():
                        permainan.berjalan = False
                        permainan.tampilkan_hasil()

        if permainan.mode_permainan == 'ai' and permainan.pemain == kecerdasan_buatan.pemain and permainan.berjalan:
            pygame.display.update()
            baris, kolom = kecerdasan_buatan.evaluasi(papan)
            permainan.lakukan_langkah(baris, kolom)
            if permainan.selesai():
                permainan.berjalan = False
                permainan.tampilkan_hasil()
            
        pygame.display.update()

main()
