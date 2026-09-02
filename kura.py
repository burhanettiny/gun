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
    page_icon="💰",
    layout="centered"
)


# =========================================================
# TÜRKÇE TARİH BİLGİLERİ
# =========================================================

TURKISH_DAYS = {
    0: "Pazartesi",
    1: "Salı",
    2: "Çarşamba",
    3: "Perşembe",
    4: "Cuma",
    5: "Cumartesi",
    6: "Pazar"
}

TURKISH_MONTHS = {
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
# ALTIN GÜNÜ TARİHİNİ HESAPLA
# =========================================================

def altin_gunu_tarihi(yil, ay, gun):
    """
    Kurallar:

    1. Kullanıcının seçtiği gün esas alınır.
    2. O ayda bu gün yoksa ayın son günü kullanılır.
    3. Tarih Cumartesi/Pazar ise sonraki ilk hafta içi güne geçilir.
    """

    # İlgili ayın son günü
    ayin_son_gunu = calendar.monthrange(yil, ay)[1]

    # Örneğin 31 seçilmişse ve ay 30 gün çekiyorsa 30 kullanılır
    gercek_gun = min(gun, ayin_son_gunu)

    tarih = date(yil, ay, gercek_gun)

    # Cumartesi veya Pazar ise sonraki ilk iş günü
    while tarih.weekday() >= 5:
        tarih += timedelta(days=1)

    return tarih


# =========================================================
# AYLIK TARİHLERİ OLUŞTUR
# =========================================================

def aylari_olustur(baslangic_tarihi, katilimci_sayisi):

    tarihler = []

    secilen_gun = baslangic_tarihi.day

    for i in range(katilimci_sayisi):

        # Başlangıç ayından itibaren ilerle
        toplam_ay = (
            baslangic_tarihi.month - 1 + i
        )

        yil = (
            baslangic_tarihi.year
            + toplam_ay // 12
        )

        ay = (
            toplam_ay % 12
        ) + 1

        tarih = altin_gunu_tarihi(
            yil,
            ay,
            secilen_gun
        )

        tarihler.append({
            "Sıra": i + 1,
            "Ay": TURKISH_MONTHS[ay],
            "Tarih": tarih.strftime("%d.%m.%Y"),
            "Gün": TURKISH_DAYS[tarih.weekday()]
        })

    return pd.DataFrame(tarihler)


# =========================================================
# BAŞLIK
# =========================================================

st.title("💰 Altın Günü Kurası")

st.write(
    "Katılımcıları ekleyin, başlangıç tarihini belirleyin "
    "ve her katılımcıya bir Altın Günü çekiliş ile atansın."
)


# =========================================================
# TARİH SEÇİMİ
# =========================================================

st.header("📅 1. Altın Günü Tarihi")

baslangic_tarihi = st.date_input(
    "İlk Altın Günü tarihi",
    value=date.today(),
    format="DD.MM.YYYY"
)

st.info(
    f"Her ayın **{baslangic_tarihi.day}. günü** esas alınacaktır. "
    "Eğer ilgili ayda bu gün yoksa ayın son günü kullanılacaktır. "
    "Hafta sonuna denk gelirse sonraki ilk hafta içi gününe geçilecektir."
)


# =========================================================
# KATILIMCI EKLEME
# =========================================================

st.header("👥 2. Katılımcılar")

isim = st.text_input(
    "Katılımcı adı",
    placeholder="Örneğin: Ayşe Yılmaz"
)

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "➕ Katılımcı Ekle",
        use_container_width=True
    ):

        isim = isim.strip()

        if not isim:
            st.warning("Lütfen bir isim girin.")

        elif isim in st.session_state.katilimcilar:
            st.warning("Bu kişi zaten listede.")

        else:
            st.session_state.katilimcilar.append(isim)

            # Katılımcı değiştiğinde eski kura geçersiz
            st.session_state.kura_sonucu = None
            st.session_state.kura_yapildi = False

            st.rerun()


with col2:

    if st.button(
        "🗑️ Listeyi Temizle",
        use_container_width=True
    ):

        st.session_state.katilimcilar = []
        st.session_state.kura_sonucu = None
        st.session_state.kura_yapildi = False

        st.rerun()


# =========================================================
# KATILIMCI LİSTESİ
# =========================================================

if st.session_state.katilimcilar:

    st.subheader(
        f"Katılımcılar ({len(st.session_state.katilimcilar)} kişi)"
    )

    for i, kisi in enumerate(
        st.session_state.katilimcilar
    ):

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(
                f"**{i + 1}.** {kisi}"
            )

        with col2:

            if st.button(
                "❌",
                key=f"sil_{i}"
            ):

                st.session_state.katilimcilar.pop(i)

                st.session_state.kura_sonucu = None
                st.session_state.kura_yapildi = False

                st.rerun()

else:

    st.warning(
        "Henüz katılımcı eklenmedi."
    )


# =========================================================
# AY SAYISI
# =========================================================

katilimci_sayisi = len(
    st.session_state.katilimcilar
)

if katilimci_sayisi > 0:

    st.success(
        f"👥 {katilimci_sayisi} katılımcı → "
        f"{katilimci_sayisi} aylık Altın Günü"
    )


# =========================================================
# TAKVİMİ OLUŞTUR
# =========================================================

if katilimci_sayisi > 0:

    st.header("📆 3. Altın Günü Takvimi")

    tarih_df = aylari_olustur(
        baslangic_tarihi,
        katilimci_sayisi
    )

    st.dataframe(
        tarih_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# KURA
# =========================================================

if katilimci_sayisi > 0:

    st.header("🎲 4. Kura")

    st.write(
        "Her katılımcı yalnızca **bir kez** seçilecektir."
    )

    if st.button(
        "🎲 KURAYI ÇEK",
        type="primary",
        use_container_width=True
    ):

        # Katılımcı listesinin kopyası
        kisiler = (
            st.session_state.katilimcilar.copy()
        )

        # Güvenli rastgele karıştırma
        random.SystemRandom().shuffle(kisiler)

        # Takvime kişileri sırayla ata
        sonuc_df = tarih_df.copy()

        sonuc_df["Ev Sahibi"] = kisiler

        # Sonucu kaydet
        st.session_state.kura_sonucu = sonuc_df

        st.session_state.kura_yapildi = True

        st.rerun()


# =========================================================
# KURA SONUCU
# =========================================================

if st.session_state.kura_yapildi:

    st.header("🏆 Kura Sonucu")

    sonuc = st.session_state.kura_sonucu

    # Sadece sonuç tablosu
    sonuc_goster = sonuc[
        [
            "Sıra",
            "Ay",
            "Tarih",
            "Gün",
            "Ev Sahibi"
        ]
    ]

    st.dataframe(
        sonuc_goster,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "🎉 Kura tamamlandı! "
        "Her katılımcı bir kez seçildi."
    )


    # =====================================================
    # KİŞİ BAZLI SONUÇLAR
    # =====================================================

    st.subheader("👤 Katılımcıların Altın Günleri")

    for _, satir in sonuc.iterrows():

        st.write(
            f"**{satir['Ev Sahibi']}** → "
            f"{satir['Tarih']} "
            f"({satir['Gün']})"
        )


    # =====================================================
    # CSV
    # =====================================================

    csv = sonuc_goster.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Sonucu Excel/CSV için indir",
        data=csv,
        file_name="altin_gunu_kurasi.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# ALT BİLGİ
# =========================================================

st.divider()

st.caption(
    "💰 Altın Günü Kura Uygulaması"
)
