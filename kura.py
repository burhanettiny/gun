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
# SESSION STATE
# =========================================================

if "katilimci_df" not in st.session_state:
    st.session_state.katilimci_df = pd.DataFrame(
        {"Katılımcı": ["", "", "", "", ""]}
    )

if "kura_sonucu" not in st.session_state:
    st.session_state.kura_sonucu = None

if "kura_yapildi" not in st.session_state:
    st.session_state.kura_yapildi = False


# =========================================================
# TARİH HESAPLAMA
# =========================================================

def altin_gunu_tarihi(yil, ay, gun):
    """
    Altın günü tarihini hesaplar.

    Kurallar:
    1. Kullanıcının belirlediği gün kullanılır.
    2. O ayda bu gün yoksa ayın son günü kullanılır.
    3. Hafta sonuna denk gelirse sonraki ilk hafta içi güne geçilir.
    """

    ayin_son_gunu = calendar.monthrange(yil, ay)[1]

    # Örneğin 31 seçildiyse:
    # Şubat -> 28/29
    # Nisan -> 30
    gercek_gun = min(gun, ayin_son_gunu)

    tarih = date(yil, ay, gercek_gun)

    # Cumartesi veya Pazar ise sonraki ilk hafta içi
    while tarih.weekday() >= 5:
        tarih += timedelta(days=1)

    return tarih


# =========================================================
# AYLIK TAKVİMİ OLUŞTUR
# =========================================================

def aylari_olustur(baslangic_tarihi, ay_sayisi):

    liste = []

    secilen_gun = baslangic_tarihi.day

    for i in range(ay_sayisi):

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
    Altın günü tarihini belirleyin, katılımcıları girin
    ve kura ile her aya bir kişi atayın.
    """
)

st.divider()


# =========================================================
# TARİH SEÇİMİ
# =========================================================

st.subheader("📅 Altın Günü Başlangıç Tarihi")

col1, col2 = st.columns([2, 1])

with col1:
    baslangic_tarihi = st.date_input(
        "İlk Altın Günü tarihi",
        value=date.today(),
        format="DD.MM.YYYY"
    )

with col2:
    st.metric(
        "Seçilen Gün",
        f"{baslangic_tarihi.day}. gün"
    )

st.info(
    f"""
    **Tarih kuralı:** Her ayın {baslangic_tarihi.day}. günü esas alınır.
    
    • İlgili ayda bu gün yoksa ayın son günü kullanılır.  
    • Hafta sonuna denk gelirse sonraki ilk hafta içi güne taşınır.
    """
)

st.divider()


# =========================================================
# SEKME YAPISI
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

    st.header("👥 Kuraya Katılacak Kişiler")

    st.write(
        "İsimleri aşağıdaki tabloya girin. "
        "Tablonun altındaki **+** işareti ile yeni kişi ekleyebilirsiniz."
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

    # Tabloyu session state'e kaydet
    st.session_state.katilimci_df = duzenlenen_df

    # -----------------------------------------------------
    # İSİMLERİ TEMİZLE
    # -----------------------------------------------------

    isimler = []

    for isim in duzenlenen_df["Katılımcı"].tolist():

        if pd.notna(isim):

            isim = str(isim).strip()

            if isim:
                isimler.append(isim)

    # -----------------------------------------------------
    # TEKRAR KONTROLÜ
    # -----------------------------------------------------

    tekrar_edenler = []

    for isim in set(isimler):

        if isimler.count(isim) > 1:
            tekrar_edenler.append(isim)

    # -----------------------------------------------------
    # BİLGİ
    # -----------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Katılımcı Sayısı",
            len(isimler)
        )

    with col2:
        st.metric(
            "Kura Ay Sayısı",
            len(isimler)
        )

    if tekrar_edenler:

        st.error(
            "Aşağıdaki isimler birden fazla girilmiş: "
            + ", ".join(tekrar_edenler)
        )

    elif len(isimler) == 0:

        st.warning(
            "Henüz katılımcı eklenmedi."
        )

    else:

        st.success(
            f"✅ {len(isimler)} katılımcı hazır. "
            f"Kura {len(isimler)} ay üzerinden yapılacak."
        )


# =========================================================
# TAB 2 - TAKVİM
# =========================================================

with tab2:

    st.header("📅 Altın Günü Takvimi")

    if len(isimler) == 0:

        st.warning(
            "Önce 'Katılımcılar' sekmesinden kişi ekleyin."
        )

    else:

        takvim_df = aylari_olustur(
            baslangic_tarihi,
            len(isimler)
        )

        st.write(
            f"Toplam **{len(isimler)} kişi** olduğu için "
            f"**{len(isimler)} aylık** Altın Günü takvimi oluşturuldu."
        )

        st.dataframe(
            takvim_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🎯 Tarih Kurallarının Uygulanması")

        st.write(
            f"Başlangıç günü: **ayın {baslangic_tarihi.day}. günü**"
        )

        st.write(
            "Hafta sonuna denk gelen tarihler otomatik olarak "
            "**sonraki ilk hafta içi güne** taşınır."
        )

        if baslangic_tarihi.day >= 29:

            st.write(
                f"Seçilen gün **{baslangic_tarihi.day}** olduğu için "
                "bazı aylarda ayın son günü kullanılabilir."
            )


# =========================================================
# TAB 3 - KURA SONUCU
# =========================================================

with tab3:

    st.header("🎲 Kura Sonucu")

    if len(isimler) == 0:

        st.warning(
            "Kura çekmek için önce katılımcıları girin."
        )

    elif tekrar_edenler:

        st.error(
            "Kura çekebilmek için tekrarlanan isimleri düzeltin."
        )

    else:

        st.write(
            f"**{len(isimler)} kişi → {len(isimler)} ay**"
        )

        st.info(
            "Kura sonucunda her katılımcı yalnızca "
            "**bir kez** seçilecektir."
        )

        st.divider()

        # -------------------------------------------------
        # KURA BUTONU
        # -------------------------------------------------

        if st.button(
            "🎲 KURAYI ÇEK",
            type="primary",
            use_container_width=True
        ):

            # Listeyi kopyala
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

            # Kura sırasını aylara ata
            sonuc_df["Ev Sahibi"] = kura_listesi

            # Sonucu kaydet
            st.session_state.kura_sonucu = sonuc_df
            st.session_state.kura_yapildi = True

            st.rerun()

        # -------------------------------------------------
        # SONUÇ
        # -------------------------------------------------

        if st.session_state.kura_sonucu is not None:

            sonuc = st.session_state.kura_sonucu

            st.success(
                "🎉 Kura tamamlandı!"
            )

            st.subheader("🏆 Altın Günü Sonuçları")

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

            # -------------------------------------------------
            # KURA SIRASI
            # -------------------------------------------------

            st.subheader("🎲 Rastgele Sıralama")

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
                    f"{ikon} **{kisi}**"
                )

            # -------------------------------------------------
            # CSV İNDİR
            # -------------------------------------------------

            st.divider()

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
