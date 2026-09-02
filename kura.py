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
# SESSION STATE
# =========================================================

if "katilimci_df" not in st.session_state:
    st.session_state.katilimci_df = pd.DataFrame(
        {"Katılımcı": ["", "", "", "", ""]}
    )

if "kura_sonucu" not in st.session_state:
    st.session_state.kura_sonucu = None


# =========================================================
# TARİH HESAPLAMA
# =========================================================

def altin_gunu_tarihi(yil, ay, gun):
    """
    Kurallar:

    - Seçilen gün ilgili ayda varsa o gün kullanılır.
    - Gün yoksa ayın son günü kullanılır.
    - Hafta sonuna denk gelirse sonraki ilk hafta içi güne geçilir.
    """

    ayin_son_gunu = calendar.monthrange(yil, ay)[1]

    # Örneğin 31 seçildiyse Şubat'ta 28/29 kullanılır
    gercek_gun = min(gun, ayin_son_gunu)

    tarih = date(yil, ay, gercek_gun)

    # Cumartesi = 5
    # Pazar = 6
    while tarih.weekday() >= 5:
        tarih += timedelta(days=1)

    return tarih


# =========================================================
# AYLIK TARİHLER
# =========================================================

def aylari_olustur(baslangic_tarihi, ay_sayisi):

    liste = []

    secilen_gun = baslangic_tarihi.day

    for i in range(ay_sayisi):

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

        liste.append({
            "Sıra": i + 1,
            "Ay": AYLAR[ay],
            "Tarih": tarih.strftime("%d.%m.%Y"),
            "Gün": GUNLER[tarih.weekday()]
        })

    return pd.DataFrame(liste)


# =========================================================
# BAŞLIK
# =========================================================

st.title("💰 Altın Günü Kurası")

st.markdown(
    """
    Altın günü tarihini belirleyin ve kuraya katılacak kişileri
    tabloya girin.
    """
)


# =========================================================
# TARİH
# =========================================================

st.header("📅 Altın Günü Tarihi")

baslangic_tarihi = st.date_input(
    "İlk altın günü tarihi",
    value=date.today(),
    format="DD.MM.YYYY"
)

st.info(
    f"""
    Her ayın **{baslangic_tarihi.day}. günü** esas alınacaktır.

    • Bu gün ilgili ayda yoksa ayın son günü kullanılır.  
    • Tarih hafta sonuna denk gelirse sonraki ilk hafta içi güne taşınır.
    """
)


# =========================================================
# KATILIMCI TABLOSU
# =========================================================

st.header("👥 Kuraya Katılacak Kişiler")

st.write(
    "Aşağıdaki tabloya isimleri girin. "
    "Yeni satır eklemek için tablonun altındaki **+** düğmesini kullanabilirsiniz."
)


duzenlenen_df = st.data_editor(
    st.session_state.katilimci_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Katılımcı": st.column_config.TextColumn(
            "Katılımcı Adı",
            help="Kuraya katılacak kişinin adını yazın.",
            max_chars=100
        )
    },
    key="katilimci_editor"
)

# Güncel tabloyu kaydet
st.session_state.katilimci_df = duzenlenen_df


# =========================================================
# TEMİZ İSİM LİSTESİ
# =========================================================

isimler = []

for isim in duzenlenen_df["Katılımcı"].tolist():

    if pd.notna(isim):

        isim = str(isim).strip()

        if isim:
            isimler.append(isim)


# Tekrarlanan isimleri kontrol et
tekrar_edenler = [
    isim
    for isim in set(isimler)
    if isimler.count(isim) > 1
]


# =========================================================
# KATILIMCI BİLGİSİ
# =========================================================

st.write(
    f"**Kuraya katılan kişi sayısı: {len(isimler)}**"
)

if tekrar_edenler:

    st.error(
        "Aynı isim birden fazla kez girilmiş: "
        + ", ".join(tekrar_edenler)
    )


# =========================================================
# TAKVİM
# =========================================================

if len(isimler) > 0:

    st.header("📆 Altın Günü Takvimi")

    takvim_df = aylari_olustur(
        baslangic_tarihi,
        len(isimler)
    )

    st.dataframe(
        takvim_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# KURA BUTONU
# =========================================================

st.header("🎲 Kura")

if len(isimler) < 2:

    st.warning(
        "Kura için en az 2 katılımcı gereklidir."
    )

elif tekrar_edenler:

    st.warning(
        "Kura çekmeden önce tekrarlanan isimleri düzeltin."
    )

else:

    if st.button(
        "🎲 KURAYI ÇEK",
        type="primary",
        use_container_width=True
    ):

        # Katılımcı listesinin kopyasını oluştur
        kura_listesi = isimler.copy()

        # Rastgele sırala
        random.SystemRandom().shuffle(
            kura_listesi
        )

        # Takvimi oluştur
        sonuc_df = aylari_olustur(
            baslangic_tarihi,
            len(kura_listesi)
        )

        # Rastgele sırayı aylara ata
        sonuc_df["Ev Sahibi"] = kura_listesi

        # Sonucu kaydet
        st.session_state.kura_sonucu = sonuc_df

        st.rerun()


# =========================================================
# KURA SONUCU
# =========================================================

if st.session_state.kura_sonucu is not None:

    st.header("🏆 Kura Sonucu")

    sonuc = st.session_state.kura_sonucu

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
        "🎉 Kura tamamlandı!"
    )


    # =====================================================
    # KURA SIRASI
    # =====================================================

    st.subheader("🎲 Rastgele Kura Sırası")

    for i, kisi in enumerate(
        sonuc["Ev Sahibi"].tolist(),
        start=1
    ):

        if i == 1:
            ikon = "🥇"
        elif i == 2:
            ikon = "🥈"
        elif i == 3:
            ikon = "🥉"
        else:
            ikon = f"{i}."

        st.write(
            f"**{ikon} {kisi}**"
        )


    # =====================================================
    # CSV İNDİRME
    # =====================================================

    csv = sonuc_goster.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Kura Sonucunu İndir",
        data=csv,
        file_name="altin_gunu_kura_sonucu.csv",
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
