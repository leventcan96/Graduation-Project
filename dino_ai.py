import pygame
import random
import nnet
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np

EKR_YUK = 250#skor yüksekliği
EKR_GEN = 800#skor genişliği
YERCEKIMI = 6#yer çekimi
YERC_ARTIS = 0.1#yerçekimi artışı
OYUN_HIZI = 6#oyun hızı
OHIZ_ARTIS = 0.1#hız artışı
YER_YUK = 200#yeryüzü yüksekliği
DINO_POZ = 30#dinazor pozisyonu
DINO_YUK = YER_YUK -35#dinazor yüksekliği
ENG_ARALIK = 300#engeller arası mesafe
FPS = 600#frame per second
DINO_SAYISI = 100#dinazor sayısı
AI = True#yapay zeka


class Dino_model:
    def __init__(self):
        self.dino = pygame.Rect(DINO_POZ, YER_YUK, 30, 42)
        self.dinoY = YER_YUK
        self.perf_skoru = 0
        self.dead = False
        self.sekil = 0
        self.ziplamaZamani = 0
        self.ziplamaHizi = 0
        self.yercekimi = YERCEKIMI
        self.egik = 0
        self.ekran = pygame.display.set_mode((EKR_GEN, EKR_YUK))


        self.hiz = OYUN_HIZI


        self.nn = nnet.neural_net(n_giris=6, nrons=20, n_cikis=2)


    def ciz(self):
            pygame.draw.rect(self.ekran, (41, 128, 185),
                         pygame.Rect(30, self.dinoY, 45, 35),1)  ##################################################


    def zipla(self):
        if self.dinoY >= DINO_YUK:
            self.ziplamaZamani = 29
            self.yercekimi = YERCEKIMI
            self.ziplamaHizi = 16

    def egil(self):
        if self.dinoY == DINO_YUK:
            self.egik = 1
            self.dino[3] = 30#dinonun yuksekliğini düşür(eğilme)
            self.dino[2] = 42#dinoyu genişlet
    def beyin(self):
        out = self.nn.beyin([self.ilk_engel_uzaklık,#uzaklık
                             self.engel_alt_konum ,
                             self.ikinci_engel_uzaklık,
                             self.engel_gen,#engelin genişliüi
                             self.engel_yuk,#engelin yüksekliği
                             self.hiz])#hız
        if out[0] > 0.5:
            self.zipla()
            self.ciz()
        elif out[1] > 0.5:
            self.egil()
            pygame.draw.rect(self.ekran, (41, 128, 185),
                         pygame.Rect(30, self.dinoY, 60, 30), 1)
        else:
            self.ciz()


class engel(object):
    def __init__(self, eng_list):
        self.engelYuk = DINO_YUK
        self.en_img2 = None
        ind = random.choice(range(len(eng_list) - 1))#random engel resmi seçme
        if ind == 6:#kus
            self.engelYuk -= random.choice([-15, 45, 90,
                                       90]) #iki kere doksan daha çok yüksekten gelsin
            self.en_img2 = eng_list[ind + 1]#ikinci resim (kanadı eğik kus
        elif ind > 3:
            self.engelYuk += 10#engelin  konumu
        self.en_img = eng_list[ind]#engelin resmi
        self.enx = random.randint(EKR_GEN+50, EKR_GEN+100)#ekranın dışından şeklin oluşması
        self.Rect = pygame.Rect(self.enx,
                                self.engelYuk,
                                self.en_img.get_width() - 10,
                                self.en_img.get_height())#Rect (xkonum, ykonum, genişlik, yükseklik)


class bulut(object):
    def __init__(self, bulut_img):
        self.bulut_img = bulut_img
        self.bulutY = random.randint(15, 140)#random bulut yükseklikleri
        self.bulutX = EKR_GEN
        self.hiz = random.uniform(1, 3)#random olarak buut hızları


class DinoGame:
    def __init__(self):

        self.dinolar = [Dino_model() for i in range(DINO_SAYISI)]#dino oluştur
        self.ekran = pygame.display.set_mode((EKR_GEN, EKR_YUK))#ekranı başlat
        self.yer = pygame.image.load("assets/land.png").convert_alpha()#resimlerin yükleneceği yer
        self.dinoHareket = [pygame.image.load("assets/step1.png").convert_alpha(),#Dino resimleri
                        pygame.image.load("assets/step2.png").convert_alpha(),
                        pygame.image.load("assets/air.png").convert_alpha(),
                        pygame.image.load("assets/dead.png").convert_alpha(),
                        pygame.image.load("assets/down1.png").convert_alpha(),
                        pygame.image.load("assets/down2.png").convert_alpha()]
        self.eng_list = [pygame.image.load("assets/cac_l2.png").convert_alpha(),#engeller
                         pygame.image.load("assets/cac_l3.png").convert_alpha(),
                         pygame.image.load("assets/cac_l4.png").convert_alpha(),
                         pygame.image.load("assets/cac_l.png").convert_alpha(),
                         pygame.image.load("assets/cac_s2.png").convert_alpha(),
                         pygame.image.load("assets/cac_s.png").convert_alpha(),
                         pygame.image.load("assets/bird1.png").convert_alpha(),
                         pygame.image.load("assets/bird2.png").convert_alpha()]
        self.bulut_img = pygame.image.load("assets/cloud.png").convert_alpha()#bulut
        self.jenerasyon = 1
        self.onceki_jen_skor = 0

        self.yuksek_skor = 0
        self.yasayan_sayisi = DINO_SAYISI
        self.oyun_hiz = OYUN_HIZI

        self.aralik = ENG_ARALIK
        self.eng = [engel(self.eng_list) for i in range(2)]#ekrana aynı anda 2 engel gelmesi
        self.eng[1].enx += self.aralik#
        self.bulutlar = [bulut(self.bulut_img) for i in range(4)]#ekrana aynı anda 4 bulut gelmesi
        self.yerx = 0
        self.yer_genislik = self.yer.get_width()
        self.yer2x = self.yer_genislik


    def yerGuncelle(self):
        self.yerx -= self.oyun_hiz#yerin hızı oyun hızına göre artsın
        self.yer2x -= self.oyun_hiz#iki tane yer var biri bitince diğeri başlıyor
        for oo in self.eng:
            oo.enx -= self.oyun_hiz#engellerin hızı oyun hızına göre artsın
        for dno in self.dinolar:
            if not dno.dead:
                dno.perf_skoru += self.oyun_hiz / (OYUN_HIZI * 5)  #oyun hızı arrtıgı için skorda ona göre artar
        if self.yerx < -self.yer_genislik:
            self.yerx = self.yer2x + self.yer_genislik#ikinci yerin gelmesi
            if self.oyun_hiz < 13:
                self.oyun_hiz += OHIZ_ARTIS#oyun hızı belli bir yere kadar artsın
        elif self.yer2x < -self.yer_genislik:
            self.yer2x = self.yerx + self.yer_genislik#tekrardan birinci yerin gelmesi
            if self.oyun_hiz < 13:#sınır
                self.oyun_hiz += OHIZ_ARTIS

    def bulutOlustur(self):
        for i in range(4):
            if self.bulutlar[i].bulutX < -40:#bulutlar ekrandan cıktığında
                self.bulutlar[i] = bulut(self.bulut_img)#yeni bulut oluştur
            self.bulutlar[i].bulutX -= self.bulutlar[i].hiz#ilerlemesi

    def engelOlustur(self):
        for i in range(2):
            if self.eng[i].enx < -60:#engel ekrandan cıktıgında
                self.eng[i] = engel(self.eng_list)#engel olustur
        fark = abs(self.eng[0].enx - self.eng[1].enx)#farkın mutlak degeri
        while fark < self.aralik:
            if self.eng[0].enx > EKR_GEN:#engel daha ekrana girmemisse
                self.eng[0].enx += self.aralik / 2
            else:
                self.eng[1].enx += self.aralik / 2
            fark = abs(self.eng[0].enx - self.eng[1].enx)
        self.aralik += OHIZ_ARTIS /5

    def dinoGuncelle(self):
        for dno in self.dinolar:
            if dno.egik > 0:#eğildiyse
                dno.egik -= 1#eğik durumu degistirme
                dno.dino[3] = 42#genişliğini düzeltme
            if dno.ziplamaZamani:#zıpladıysa
                dno.ziplamaHizi -= 1#zıplama surumunu değistirme
                dno.dinoY -= dno.ziplamaHizi#eski konumuna getirme
                dno.ziplamaZamani -= 1
                # print("y ve yuk", self.dinolar[0].dinoY)
            elif dno.dinoY < DINO_YUK:#havadaysa
                dno.dinoY += dno.yercekimi#yerçekimini ekleme
                dno.yercekimi += YERC_ARTIS #yer cekimi artıs
            else:
                dno.dinoY = DINO_YUK
            dno.dino[1] = dno.dinoY

        for dno in self.dinolar:
            if not dno.dead:#dino ölmediyse
                for oo in self.eng:
                    if oo.enx < 100:
                        oo.Rect[0] = oo.enx + 2
                        if oo.Rect.colliderect(dno.dino):#iki dikdörtgeninin üst üste gelip gelmediği(dino engel)
                            dno.dead = True
                            self.yasayan_sayisi -= 1#yasayan sayısı azalt

#############################################################################################################################
        self.dinolar.sort(key=lambda x: x.perf_skoru, reverse=True)

        if self.dinolar[0].perf_skoru > self.yuksek_skor:
            self.onceki_eniyi = deepcopy(self.dinolar[0])
            self.yuksek_skor = self.dinolar[0].perf_skoru

        if not self.yasayan_sayisi:
            print("Jenerasyon", self.jenerasyon, ":", self.dinolar[0].perf_skoru)
            self.onceki_jen_skor = self.dinolar[0].perf_skoru
            self.cizim()
            if AI:
                self.eniyi_klon()
                self.caprazlama()
                self.b_Mutasyon()
                self.w_Mutasyon()
                self.rast_jen()
            for dno in self.dinolar:
                dno.dino[1] = 50
                dno.dinoY = YER_YUK - 100
                dno.perf_skoru = 0
                dno.dead = False
                dno.yercekimi = YERCEKIMI
            self.yerx = 0
            self.yer2x = self.yer_genislik
            self.aralik = ENG_ARALIK
            self.yasayan_sayisi = DINO_SAYISI
            self.jenerasyon += 1
            self.oyun_hiz = OYUN_HIZI
            self.eng = [engel(self.eng_list) for i in range(2)]
            self.eng[1].enx += self.aralik

    def eniyi_klon(self):
        self.dinolar.pop()  # 0 to 3
        self.dinolar.insert(0, Dino_model())
        self.dinolar[0] = deepcopy(self.onceki_eniyi)

    def caprazlama(self):
        x = 3 * int(DINO_SAYISI / 10)
        y = 4 * int(DINO_SAYISI / 10)
        z = 5 * int(DINO_SAYISI / 10)
        for i in range(x, y):  # 3 to 4
            self.dinolar[i].nn.w1[:] = self.dinolar[i - x].nn.w1[:]
            self.dinolar[i].nn.w2[:] = self.dinolar[i - x].nn.w2[:]
        for i in range(y, z):  # 4 to 5
            self.dinolar[i].nn.w1[:] = self.dinolar[i - y].nn.w1[:]
            self.dinolar[i].nn.w2[:] = self.dinolar[i + 1 - y].nn.w2[:]
        for i in range(z, 6 * int(DINO_SAYISI / 10)):  # 5 to 6
            self.dinolar[i].nn.w1[:] = self.dinolar[i - z].nn.w1[:]

    def b_Mutasyon(self):
        x = 6 * int(DINO_SAYISI / 10)
        for i in range(x, 8 * int(DINO_SAYISI / 10)):  # 6 to 8
            self.dinolar[i].nn.w1[:] = self.dinolar[i - x].nn.w1[:]
            self.dinolar[i].nn.w2[:] = self.dinolar[i - x].nn.w2[:]
            self.dinolar[i].nn.gen_bias()

    def w_Mutasyon(self):
        x = 8 * int(DINO_SAYISI / 10)
        for i in range(x, 9 * int(DINO_SAYISI / 10)):  # 8 to 9
            self.dinolar[i].nn.b1[:] = self.dinolar[i - x].nn.b1[:]
            self.dinolar[i].nn.b2 = 0
            self.dinolar[i].nn.b2 += self.dinolar[i - x].nn.b2
            self.dinolar[i].nn.gen_weights()

    def rast_jen(self):
        for i in range(9 * int(DINO_SAYISI / 10), int(DINO_SAYISI)):  # 9 to 10
            self.dinolar[i].nn.gen_bias()
            self.dinolar[i].nn.gen_weights()
    def run(self):
        saat = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 16)
        adim = 0
        kanat = 0
        n_exit_game = True
        while n_exit_game:
            saat.tick(FPS)
            #tus = pygame.key.get_pressed()
            # for dno in self.dinolar:
            #     if not dno.dead:
            #         if tus[K_DOWN]:
            #             dno.egil()
            #         elif tus[K_UP]:
            #             dno.zipla()
            for event in pygame.event.get():#kuyruktan olayları al
                if event.type == pygame.QUIT:#oyunu kapama
                    n_exit_game = False

            self.ekran.fill((255, 255, 255))#renk
            self.ekran.blit(self.yer, (self.yerx, YER_YUK))#yercizdir
            self.ekran.blit(self.yer, (self.yer2x, YER_YUK))

            for oo in self.eng:
                if oo.en_img2:
                    if kanat < 13:#kanat hareketleri
                        self.ekran.blit(oo.en_img, (oo.enx, oo.engelYuk))
                    elif kanat < 26:
                        self.ekran.blit(oo.en_img2, (oo.enx, oo.engelYuk - 6))
                    else:
                        kanat = 0
                else:
                    self.ekran.blit(oo.en_img, (oo.enx, oo.engelYuk))
            kanat += 1
            for blt in self.bulutlar:
                self.ekran.blit(blt.bulut_img, (blt.bulutX, blt.bulutY))
            self.bulutOlustur()
            self.ekran.blit(font.render("Skor: " + str(self.dinolar[0].perf_skoru)[:5],
                                         -1,
                                         (110, 110, 110)),#renk
                             (EKR_GEN / 1.6, 10))#konum
            self.ekran.blit(font.render("Önceki Skor: " + str(self.onceki_jen_skor)[:5],
                                         -1,
                                         (110, 110, 110)),#renk
                             (EKR_GEN / 1.6, 40))#konum
            self.ekran.blit(font.render("Yüksek Skor: " + str(self.yuksek_skor)[:5],
                                         -1,
                                         (110, 110, 110)),#renk
                             (EKR_GEN / 1.6, 70))#konum
            self.ekran.blit(font.render("Jenerasyon: " + str(self.jenerasyon),
                                         -1,
                                         (110, 110, 110)),
                             (EKR_GEN / 1.2, 10))
            self.ekran.blit(font.render("Yaşayan sayısı: " + str(self.yasayan_sayisi),
                                         -1,
                                         (110, 110, 110)),#renk
                             (EKR_GEN / 1.2, 40))#konum
            if self.eng[0].enx > 20:
                dx0 = (self.eng[0].enx - 40 - DINO_POZ)#ilk engel mesafe
            else:
                dx0 = EKR_GEN
            if self.eng[1].enx > 20:
                dx1 = (self.eng[1].enx - 40 - DINO_POZ)#ikinci engel mesafe
            else:
                dx1 = EKR_GEN
            if dx0 < dx1:
                ilk_engel_uzaklık = dx0
                ikinci_engel_uzaklık = dx1
                engel_gen = self.eng[0].en_img.get_width()
                engel_yuk = DINO_YUK + 47 - self.eng[0].engelYuk
                engel_alt_konum = engel_yuk - self.eng[0].en_img.get_height()
            else:
                ilk_engel_uzaklık = dx1
                ikinci_engel_uzaklık = dx0
                engel_gen = self.eng[1].en_img.get_width()
                engel_yuk = DINO_YUK + 47 - self.eng[1].engelYuk#dinoya göre yukseklik
                engel_alt_konum = engel_yuk - self.eng[1].en_img.get_height()
            for dno in self.dinolar:
                if not dno.dead:
                    dno.ilk_engel_uzaklık = ilk_engel_uzaklık
                    dno.engel_alt_konum = engel_alt_konum
                    dno.ikinci_engel_uzaklık = ikinci_engel_uzaklık
                    dno.engel_gen = engel_gen
                    dno.engel_yuk = engel_yuk
                    dno.hiz = self.oyun_hiz
                    foto_no = 0
                    egik_poz = 0
                    if AI:
                        dno.beyin()
                    if dno.egik:
                        foto_no = 4
                        egik_poz = 15
                    else:
                        foto_no = 0
                    if dno.ziplamaZamani:
                        dno.sekil = 2
                    elif adim > 5:
                        dno.sekil = foto_no
                        if adim > 10:
                            adim = 0
                    else:
                        dno.sekil = 1 + foto_no
                    self.ekran.blit(self.dinoHareket[dno.sekil], (DINO_POZ, dno.dinoY + egik_poz))  # DINO_POZ, YER_YUK, 30, 42
            adim += 1

            self.yerGuncelle()
            self.dinoGuncelle()
            self.engelOlustur()

            pygame.display.update()
    def cizim(self):

        liste=list()

        x=self.jenerasyon
        y = self.onceki_jen_skor
        liste.append(y)

        plt.scatter(x,liste)
        if x==10:
             plt.show()

        # plt.figure(figsize=(int(800/100), 5))


if __name__ == "__main__":
    DinoGame().run()