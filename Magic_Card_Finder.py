import streamlit as st
import pandas as pd
from enum import Enum

st.title("Magic Karten Finder")

class Language(Enum):
    englisch = 1
    deutsch = 2

currentLanguage = Language.englisch

fehlerCount = 0
fehlerList = []

def add_Fehler(fehlerMeldung):
    global fehlerCount 
    fehlerCount += 1

    message = f"<span style='color:red'>Fehler {fehlerCount}: " + fehlerMeldung + "</span>"
    
    fehlerList.insert(1, message)

    st.markdown(message, unsafe_allow_html=True)

def get_CarNumber(cardNumber):
    if str(cardNumber)[0].isalpha():
        return 0
    if str(cardNumber) == "-":
        return -1
    else:
        return int(cardNumber)

def get_KisteFromPossibleList(df_Expansion,possibleList):
    kisten = df_Expansion["Kiste"]   

    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, kisten[possibleList[i]]) 

    return returnList

def get_SchlittenFromPossibleList(df_Expansion,possibleList):
    schlitten = df_Expansion["Schlitten"]   

    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, schlitten[possibleList[i]]) 

    return returnList

def get_Schlitten(df_Expansion, cardNumber, cardName, cardCondition, possibleList):
    schlitteVon = df_Expansion["Karten Nummer Von"]   
    schlitteBis = df_Expansion["Karten Nummer Bis"]
    schlitten = df_Expansion["Schlitten"]   
    kisten = df_Expansion["Kiste"]   
    condition = df_Expansion["Condition"]
    
    fehler = False

    for i in range(len(possibleList)):
        cardNumberInt = get_CarNumber(cardNumber)
        
        if(cardNumberInt == -1):
            add_Fehler(f"Die Karte <strong>{cardName}</strong> hat keine KartenNummer: <strong>{cardNumber}</strong> mögliche Boxen: <strong>{get_KisteFromPossibleList(df_Expansion,possibleList)}</strong> Schlitten: <strong>{get_SchlittenFromPossibleList(df_Expansion,possibleList)}</strong>")
            fehler = True
            return -1,-1,fehler

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "":
            if (cardNumberInt >= int(schlitteVon[possibleList[i]]) and cardNumberInt <= int(schlitteBis[possibleList[i]])):
                return schlitten[possibleList[i]], kisten[possibleList[i]], fehler
        else:
             if (condition[possibleList[i]] == cardCondition):
                return schlitten[possibleList[i]], kisten[possibleList[i]], fehler
   
    add_Fehler(f"Keine genaue Kiste oder Spalte konnte für die Karte <strong>{cardName}</strong> mit der Nummer: <strong>{cardNumber}</strong> gefunden werden mögliche Boxen: <strong>{get_KisteFromPossibleList(df_Expansion,possibleList)}</strong> Schlitten: <strong>{get_SchlittenFromPossibleList(df_Expansion,possibleList)}</strong>")     
    fehler = True
    return -1,-1, fehler

def get_List(df_Expansion, sellingCardsExpansion, sellingCardsLanguage, sellingCardConditon, cardName):
   
    fehler = False

    condition = df_Expansion["Condition"]
    
    if(currentLanguage ==  Language.englisch):
        expansion = df_Expansion["Expansion"]
        languageDF = df_Expansion["Language"]
    else:
        expansion = df_Expansion["Expansion deutsch"]
        languageDF = df_Expansion["Language deutsch"]

    listOnlyExpansion = [] 
    listWithLanguage = [] 

    returnList = [] 

    for i in range(len(expansion)):
        if(sellingCardConditon == "NM"):
            if (expansion[i] == sellingCardsExpansion):
                listOnlyExpansion.insert(1, i)  
                if (sellingCardsLanguage == languageDF[i]):
                    listWithLanguage.insert(1, i)  
                else:
                    listWithLanguage.insert(1, "")  
        else:
            if (sellingCardConditon == condition[i]):
                returnList.insert(1, i) 
    
    if(len(listOnlyExpansion) > 0 and len(listWithLanguage) == 0 ):
        add_Fehler(f"Karte <strong>{cardName}</strong> in der Sprache <strong>{sellingCardsLanguage}</strong> konnte nicht gefunden werden. In der Expansion <strong>{sellingCardsExpansion}</strong> zu finden")     
        fehler = True
    elif(len(listOnlyExpansion) == 0):
        add_Fehler(f"Keinen Eintrag für die Expansion <strong>{sellingCardsExpansion}</strong> gefunden. Karte <strong>{cardName}</strong> in der Sprache <strong>{sellingCardsLanguage}</strong>")     
        fehler = True
    else:
        for i in range(len(listOnlyExpansion)):
            if (listWithLanguage[i] != ""):
                returnList.insert(1, listOnlyExpansion[i])

    return returnList, fehler

expansion_csv = st.file_uploader("Expansion- und Kistenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")      

    if( "Magic the Gathering Einzelkarten" == df_Cards.columns[0]):
        currentLanguage =  Language.deutsch
    
    df_Cards["Kiste"] = "-"
    df_Cards["Schlitte"] = "-"
    df_Cards["Fehlermeldung"] = "-"

    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsCondtion = df_Cards["Condition"]

    sellingCardsKiste = df_Cards["Kiste"]
    sellingCardsSchlitte = df_Cards["Schlitte"]
    sellingCardsFehlermeldung = df_Cards["Fehlermeldung"]

    sellingCardsName = df_Cards["Localized Article Name"]
    sellingCardsCollectorsNumber = df_Cards["Collector Number"]

    st.title("Fehler:")

    for i in range(len(sellingCardsExpansion)):
       
        possibleExpansionList, fehler = get_List(df_Expansion, sellingCardsExpansion[i], sellingCardsLanguage[i], sellingCardsCondtion[i],sellingCardsName[i])

        if(fehler):
            sellingCardsFehlermeldung[i] = fehlerCount

        if len(possibleExpansionList) > 0:
            schlitte, kiste, fehler =  get_Schlitten(df_Expansion, sellingCardsCollectorsNumber[i], sellingCardsName[i],sellingCardsCondtion[i], possibleExpansionList)
           
            if(fehler):
               sellingCardsFehlermeldung[i] = fehlerCount
           
            if(schlitte != -1 and kiste != -1):
                sellingCardsKiste[i] = kiste
                sellingCardsSchlitte[i] = schlitte
     
    st.title("Resultat:")
    st.write(df_Cards)
    
    resultsCSV = df_Cards.to_csv(index=False)

    st.download_button(
        label="CSV herunterladen",
        data=resultsCSV,
        file_name="Resultat_File.csv",
        mime="text/csv"
    )

#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic