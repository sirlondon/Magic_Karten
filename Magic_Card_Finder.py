import streamlit as st
import pandas as pd

st.title("Magic Karten Finder")

def get_CarNumber(cardNumber):
    if str(cardNumber)[0].isalpha():
        return 0
    else:
        return int(cardNumber)

def get_Schlitten(df_Expansion, kiste, cardNumber):
    schlitteVon = df_Expansion["Karten Nummer Von"]   
    schlitteBis = df_Expansion["Karten Nummer Bis"]
    schlitten = df_Expansion["Schlitten"]   
    kisten = df_Expansion["Kiste"]   
  
    for i in range(len(kisten)):
        if kiste == kisten[i]:
            cardNumberInt = get_CarNumber(cardNumber)

            if cardNumberInt >= int(schlitteVon[i]) and cardNumberInt <= int(schlitteBis[i]):
               return schlitten[i] 
            
    st.markdown(f"<span style='color:red'>Fehler: Keine Spalte in der Kiste <strong>{kiste}</strong> für Karten Nummer: <strong>{cardNumber}</strong> gefunden </span>", unsafe_allow_html=True)


expansion_csv = st.file_uploader("Expansion- und Kistenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")    
    
    df_Expansion["Key"] = df_Expansion["Expansion"] + "|" + df_Expansion["Language"]
    expansion_to_kiste = dict(zip(df_Expansion["Key"], df_Expansion["Kiste"]))   

    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsName = df_Cards["Localized Article Name"]
    collectorsNumber = df_Cards["Collector Number"]

    st.title("Resultat:")

    for i in range(len(sellingCardsExpansion)):
        key = f"{sellingCardsExpansion[i]}|{sellingCardsLanguage[i]}"
        if key in expansion_to_kiste:
           st.write("Die Karte ", sellingCardsName[i], " in der Sprache: ",sellingCardsLanguage[i] ," aus der Expansion: ", sellingCardsExpansion[i] ," befindet sich in der Box:", expansion_to_kiste.get(key), " in der Kistenspalte: ", get_Schlitten(df_Expansion,expansion_to_kiste.get(key),collectorsNumber[i]))
           st.checkbox("Karte gefunden",key=f"checkbox_{i}")
        else:
            st.markdown(f"<span style='color:red'>Fehler: Expansion: <strong>{sellingCardsExpansion[i]}</strong> in <strong>{sellingCardsLanguage[i]} nicht gefunden, Karte: <strong>{sellingCardsName[i]}</strong></span>", unsafe_allow_html=True)



#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic