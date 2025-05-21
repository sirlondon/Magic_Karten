import streamlit as st
import pandas as pd

st.title("Magic Karten Finder")

expansion_csv = st.file_uploader("Expansion- und Kistenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv)
    df_Expansion = pd.read_csv(expansion_csv)    
    
    expansion_to_kiste = pd.Series(df_Expansion.Kiste.values, index=df_Expansion.Expansion).to_dict()
    
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsName = df_Cards["Localized Article Name"]

    st.title("Resultat:")

    for i in range(len(sellingCardsExpansion)):
        if sellingCardsExpansion[i] in expansion_to_kiste:
           st.write("Die Karte ", sellingCardsName[i], " aus der Expansion: ", sellingCardsExpansion[i] ," befindet sich in der Box:", expansion_to_kiste.get(sellingCardsExpansion[i]))
           st.checkbox("Karte gefunden",key=f"checkbox_{i}")
        else:
            st.markdown(f"<span style='color:red'>Fehler: Expansion: <strong>{sellingCardsExpansion[i]}</strong> nicht gefunden, Karte: <strong>{sellingCardsName[i]}</strong></span>", unsafe_allow_html=True)



#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic