import streamlit as st
import pandas as pd

st.title("Magic Karten Finder")

def get_CarNumber(cardNumber):
    if str(cardNumber)[0].isalpha():
        return 0
    else:
        return int(cardNumber)

def get_Schlitten(df_Expansion, cardNumber,cardCondition, possibleList):
    schlitteVon = df_Expansion["Karten Nummer Von"]   
    schlitteBis = df_Expansion["Karten Nummer Bis"]
    schlitten = df_Expansion["Schlitten"]   
    kisten = df_Expansion["Kiste"]   
    condition = df_Expansion["Condition"]

    for i in range(len(possibleList)):
        cardNumberInt = get_CarNumber(cardNumber)

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "":
            if (cardNumberInt >= int(schlitteVon[possibleList[i]]) and cardNumberInt <= int(schlitteBis[possibleList[i]])):
                return schlitten[possibleList[i]], kisten[possibleList[i]]
        else:
             if (condition[possibleList[i]] == cardCondition):
                return schlitten[possibleList[i]], kisten[possibleList[i]]
            
    #st.markdown(f"<span style='color:red'>Fehler: Keine Spalte in der Kiste <strong>{possibleList}</strong> für Karten Nummer: <strong>{cardNumber}</strong> gefunden </span>", unsafe_allow_html=True)
    return -1,-1

def get_List(df_Expansion, sellingCardsExpansion, sellingCardsLanguage, sellingCardConditon, language):
   
    condition = df_Expansion["Condition"]

    if(language == "English"):
        expansion = df_Expansion["Expansion"]
        languageDF = df_Expansion["Language"]
    else:
        expansion = df_Expansion["Expansion deutsch"]
        languageDF = df_Expansion["Language deutsch"]

    returnList = []


    for i in range(len(expansion)):
        if(sellingCardConditon == "NM"):
            if (expansion[i] == sellingCardsExpansion and sellingCardsLanguage == languageDF[i]):
               returnList.insert(1, i) 
        else:
            if (sellingCardConditon == condition[i]):
                returnList.insert(1, i) 

    return returnList

expansion_csv = st.file_uploader("Expansion- und Kistenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")      

    language = "english"

    if( "Magic the Gathering Einzelkarten" == df_Cards.columns[0]):
        language = "deutsch"
    
    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsCondtion = df_Cards["Condition"]

    sellingCardsName = df_Cards["Localized Article Name"]
    collectorsNumber = df_Cards["Collector Number"]

    st.title("Resultat:")
  
    for i in range(len(sellingCardsExpansion)):
        possibleExpansionList = get_List(df_Expansion, sellingCardsExpansion[i], sellingCardsLanguage[i],sellingCardsCondtion[i],language)
        
        if len(possibleExpansionList) > 0:
           schlitte, kiste =  get_Schlitten(df_Expansion, collectorsNumber[i],sellingCardsCondtion[i], possibleExpansionList)

           if(schlitte != -1 and kiste != -1):
              st.write("Die Karte ", sellingCardsName[i], " in der Sprache: ",sellingCardsLanguage[i] ," aus der Expansion: ", sellingCardsExpansion[i] ," befindet sich in der Box:", kiste, " in der Kistenspalte: ",schlitte)
              st.checkbox("Karte gefunden",key=f"checkbox_{i}")
        else:
            st.markdown(f"<span style='color:red'>Fehler: Expansion: <strong>{sellingCardsExpansion[i]}</strong> in <strong>{sellingCardsLanguage[i]} nicht gefunden, Karte: <strong>{sellingCardsName[i]}</strong> Nummer: <strong>{collectorsNumber[i]}</strong></span>", unsafe_allow_html=True)



#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic