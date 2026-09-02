import streamlit as st
import pandas as pd
import calendar
import random
from datetime import date, timedelta

# =========================================================
# SAYFA AYARLARI
# =========================================================

st.set_page_config(
    page_title="Altın Günü Kurası",
    page_icon="🪙",
    layout="wide"
)

# =========================================================
# TÜRKÇE TARİH BİLGİLERİ
# =========================================================

AYLAR = {
    1: "Ocak",
    2: "Şubat",
    3: "Mart",
    4: "Nisan",
    5: "Mayıs",
    6: "Haziran",
    7: "Temmuz",
    8: "Ağustos",
    9: "Eylül",
    10: "Ekim",
    11: "Kasım",
    12: "Aralık"
}

GUNLER = {
    0: "Pazartesi",
    1: "Salı",
    2: "Çarşamba",
    3: "Perşembe",
    4: "Cuma",
    5: "Cumartesi",
    6: "Pazar"
}

# =========================================================
# ALTIN GÜNÜ TARİHİ HESAPLAMA
# =========================================================

def altin_gunu_tarihi(yil, ay, gun):
    """
    Seçilen gün o ayda yoksa ayın son günü kullanılır.
    Tarih hafta sonuna denk gelirse sonraki ilk iş gününe taşınır.
    """

    son_gun = calendar.monthrange(yil, ay)[1]

    # Örneğin 31 seçilmişse Şubat için 28/29 kullan
    kullanilacak_gun = min(gun, son_gun)

    tarih = date(yil, ay, kullanilacak_gun)

    # Cumartesi / Pazar ise sonraki Pazartesi
    while tarih.weekday() >= 5:
        tarih += timedelta(days=1)

    return tarih


# =========================================================
# AY LİSTESİ OLUŞTURMA
# =========================================================

def aylari_olustur(baslangic_tarihi, ay_sayisi):
    """
    Başlangıç tarihindeki gün numarasını koruyarak
    ardışık ayları oluşturur.
    """

    sonuc = []

    baslangic_yil = baslangic_tarihi.year
    baslangic_ay = baslangic_tarihi.month
    gun = baslangic_tarihi.day

    for i in range(ay_sayisi):

        toplam_ay = baslangic_ay - 1 + i

        yil = baslangic_yil + toplam_ay // 12
        ay = toplam_ay % 12 + 1

        tarih = altin_gunu_tarihi(
            yil,
            ay,
            gun
        )

        sonuc.append({
            "Sıra": i + 1,
            "Yıl": yil,
            "Ay": AYLAR[ay],
            "Tarih": tarih,
            "Gün": GUNLER[tarih.weekday()]
        })

    return sonuc


# =========================================================
# SESSION STATE
# =========================================================

if "katilimcilar" not in st.session_state:
    st.session_state.katilimcilar = []

if "kura_sonucu" not in st.session_state:
    st.session_state.kura_sonucu = None

if "kura_yapildi" not in st.session_state:
    st.session_state.kura_yapildi = False


# =========================================================
# BAŞLIK
# =========================================================

st.title("🪙 Altın Günü Kurası")

st.markdown(
    """
    Aylık Altın Günü organizasyonunuz için katılımcıları rastgele
    aylara dağıtın.
    
    **Kurallar:**
    - Her katılımcı yalnızca bir ay alır.
    - Ay sayısı otomatik olarak katılımcı sayısına eşittir.
    - Başlangıç tarihindeki gün numarası korunur.
    - İlgili ayda o gün yoksa ayın son günü kullanılır.
    - Tarih hafta sonuna denk gelirse sonraki ilk iş gününe taşınır.
    """
)

st.divider()


# =========================================================
# TABLAR
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "👥 Katılımcılar",
    "📅 Takvim",
    "🎲 Kura Sonucu"
])


# =========================================================
# TAB 1 - KATILIMCILAR
# =========================================================

with tab1:

    st.header("👥 Katılımcılar")

    st.write(
        "Önce Altın Günü'ne katılacak kişi sayısını belirleyin."
    )

    kisi_sayisi = st.number_input(
        "Kaç kişi katılacak?",
        min_value=2,
        max_value=100,
        value=8,
        step=1
    )

    st.divider()

    giris_yontemi = st.radio(
        "Katılımcıları nasıl girmek istersiniz?",
        [
            "📝 Tek tek isim gir",
            "📋 Toplu olarak yapıştır"
        ],
        horizontal=True
    )

    # -----------------------------------------------------
    # TEK TEK İSİM GİRİŞİ
    # -----------------------------------------------------

    if giris_yontemi == "📝 Tek tek isim gir":

        st.subheader("Katılımcı isimleri")

        isimler = []

        # İki sütun halinde göster
        sol, sag = st.columns(2)

        for i in range(kisi_sayisi):

            if i % 2 == 0:
                with sol:
                    isim = st.text_input(
                        f"{i + 1}. Katılımcı",
                        key=f"katilimci_{i}",
                        placeholder="Ad Soyad"
                    )
            else:
                with sag:
                    isim = st.text_input(
                        f"{i + 1}. Katılımcı",
                        key=f"katilimci_{i}",
                        placeholder="Ad Soyad"
                    )

            isimler.append(isim.strip())

        st.divider()

        if st.button(
            "💾 Katılımcıları Kaydet",
            type="primary",
            use_container_width=True
        ):

            # Boş isimleri kontrol et
            boslar = [
                i + 1
                for i, isim in enumerate(isimler)
                if not isim
            ]

            # Aynı isimleri kontrol et
            temiz_isimler = [
                isim.lower()
                for isim in isimler
                if isim
            ]

            tekrar_var = len(temiz_isimler) != len(set(temiz_isimler))

            if boslar:
                st.error(
                    f"Lütfen {', '.join(map(str, boslar))}. "
                    "katılımcıların isimlerini girin."
                )

            elif tekrar_var:
                st.error(
                    "Aynı isim birden fazla kez girilmiş. "
                    "Lütfen isimleri kontrol edin."
                )

            else:
                st.session_state.katilimcilar = isimler
                st.session_state.kura_sonucu = None
                st.session_state.kura_yapildi = False

                st.success(
                    f"✅ {len(isimler)} katılımcı kaydedildi."
                )

    # -----------------------------------------------------
    # TOPLU GİRİŞ
    # -----------------------------------------------------

    else:

        st.subheader("📋 Katılımcıları toplu girin")

        st.info(
            "Her satıra bir katılımcı gelecek şekilde isimleri yapıştırın."
        )

        toplu_giris = st.text_area(
            "Katılımcı listesi",
            height=250,
            placeholder=(
                "Ahmet Yılmaz\n"
                "Ayşe Demir\n"
                "Mehmet Kaya\n"
                "Fatma Çelik\n"
                "..."
            )
        )

        st.caption(
            f"Beklenen katılımcı sayısı: **{kisi_sayisi}**"
        )

        if st.button(
            "💾 Listeyi Kaydet",
            type="primary",
            use_container_width=True
        ):

            isimler = [
                x.strip()
                for x in toplu_giris.splitlines()
                if x.strip()
            ]

            if len(isimler) != kisi_sayisi:

                st.error(
                    f"{kisi_sayisi} kişi seçtiniz ancak "
                    f"{len(isimler)} isim girdiniz."
                )

            else:

                temiz_isimler = [
                    isim.lower()
                    for isim in isimler
                ]

                if len(temiz_isimler) != len(set(temiz_isimler)):

                    st.error(
                        "Aynı isim birden fazla kez girilmiş. "
                        "Lütfen listeyi kontrol edin."
                    )

                else:

                    st.session_state.katilimcilar = isimler
                    st.session_state.kura_sonucu = None
                    st.session_state.kura_yapildi = False

                    st.success(
                        f"✅ {len(isimler)} katılımcı kaydedildi."
                    )

    # -----------------------------------------------------
    # KAYITLI KATILIMCILAR
    # -----------------------------------------------------

    if st.session_state.katilimcilar:

        st.divider()

        st.subheader("✅ Kayıtlı Katılımcılar")

        for i, isim in enumerate(
            st.session_state.katilimcilar,
            start=1
        ):
            st.write(f"**{i}.** {isim}")


# =========================================================
# TAB 2 - TAKVİM
# =========================================================

with tab2:

    st.header("📅 Altın Günü Takvimi")

    if not st.session_state.katilimcilar:

        st.warning(
            "Önce 'Katılımcılar' sekmesinden katılımcıları girin."
        )

    else:

        st.subheader("Başlangıç tarihi")

        baslangic_tarihi = st.date_input(
            "İlk Altın Günü tarihi",
            value=date.today(),
            format="DD/MM/YYYY"
        )

        st.info(
            f"Seçilen gün: **{baslangic_tarihi.day}**. "
            "Bu gün tüm aylarda mümkün olduğunca korunacaktır."
        )

        ay_sayisi = len(
            st.session_state.katilimcilar
        )

        takvim = aylari_olustur(
            baslangic_tarihi,
            ay_sayisi
        )

        takvim_df = pd.DataFrame(takvim)

        # Tarihi Türkçe görüntüle
        takvim_df["Tarih"] = takvim_df["Tarih"].apply(
            lambda x: x.strftime("%d/%m/%Y")
        )

        st.dataframe(
            takvim_df[
                [
                    "Sıra",
                    "Yıl",
                    "Ay",
                    "Tarih",
                    "Gün"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# TAB 3 - KURA SONUCU
# =========================================================

with tab3:

    st.header("🎲 Kura Sonucu")

    if not st.session_state.katilimcilar:

        st.warning(
            "Önce katılımcıları girmeniz gerekiyor."
        )

    else:

        st.write(
            f"Toplam **{len(st.session_state.katilimcilar)}** "
            "katılımcı bulunmaktadır."
        )

        st.divider()

        baslangic_tarihi = st.date_input(
            "Kura başlangıç tarihi",
            value=date.today(),
            format="DD/MM/YYYY",
            key="kura_baslangic"
        )

        if st.button(
            "🎲 KURAYI ÇEK",
            type="primary",
            use_container_width=True
        ):

            # Katılımcıları kopyala
            kura_katilimcilari = (
                st.session_state.katilimcilar.copy()
            )

            # Güvenli rastgele karıştırma
            random.SystemRandom().shuffle(
                kura_katilimcilari
            )

            # Ayları oluştur
            takvim = aylari_olustur(
                baslangic_tarihi,
                len(kura_katilimcilari)
            )

            sonuc = []

            for i, kisi in enumerate(
                kura_katilimcilari
            ):

                sonuc.append({
                    "Sıra": takvim[i]["Sıra"],
                    "Ay": takvim[i]["Ay"],
                    "Tarih": takvim[i]["Tarih"],
                    "Gün": takvim[i]["Gün"],
                    "Katılımcı": kisi
                })

            sonuc_df = pd.DataFrame(sonuc)

            st.session_state.kura_sonucu = sonuc_df
            st.session_state.kura_yapildi = True

        # -------------------------------------------------
        # KURA SONUCU
        # -------------------------------------------------

        if st.session_state.kura_yapildi:

            st.success("🎉 Kura tamamlandı!")

            sonuc_df = st.session_state.kura_sonucu.copy()

            gorunum_df = sonuc_df.copy()

            gorunum_df["Tarih"] = gorunum_df["Tarih"].apply(
                lambda x: x.strftime("%d/%m/%Y")
            )

            gorunum_df = gorunum_df[
                [
                    "Sıra",
                    "Ay",
                    "Tarih",
                    "Gün",
                    "Katılımcı"
                ]
            ]

            st.dataframe(
                gorunum_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ---------------------------------------------
            # CSV İNDİRME
            # ---------------------------------------------

            csv_data = gorunum_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="📥 Sonucu CSV olarak indir",
                data=csv_data,
                file_name="altin_gunu_kura_sonucu.csv",
                mime="text/csv",
                use_container_width=True
            )

            # ---------------------------------------------
            # KISA ÖZET
            # ---------------------------------------------

            st.divider()

            st.subheader("📌 Özet")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Katılımcı",
                    len(st.session_state.katilimcilar)
                )

            with col2:
                st.metric(
                    "Altın Günü",
                    len(st.session_state.kura_sonucu)
                )

            with col3:
                st.metric(
                    "Her kişi",
                    "1 ay"
                )
