import streamlit as st
import pandas as pd
from enum import Enum

st.set_page_config(page_title="Magic Karten Finder", layout="wide")

st.title("Magic Karten Finder")

class Language(Enum):
    englisch = 1
    deutsch = 2

currentLanguage = Language.englisch

def get_AllCardsFromBestellung(df_Results, bestellung):

    if(currentLanguage == Language.deutsch):
        bestellungen = df_Results["Magic the Gathering Einzelkarten"]
    else:
        bestellungen = df_Results["Magic the Gathering Singles"]

    returnList = []

    for i in range(len(bestellungen)):
        if(bestellung == bestellungen[i]):
            returnList.insert(1, i)

    return returnList

def get_AllCardsInKisteAndSchlitten(kiste, schlitte, df_Results):
    schlittenResults = df_Results["Schlitten"]   
    kistenResults = df_Results["Kiste"]   

    returnList = []

    for i in range(len(kistenResults)):
        if(kistenResults[i] ==kiste and schlittenResults[i] == schlitte):
            returnList.insert(1, i)

    return returnList

fehlerCount = 0
fehlerList = []

def add_Fehler(fehlerMeldung, code):
    global fehlerCount 
    fehlerCount += 1

    message = f"<span style='color:red'>{code}, Fehler {fehlerCount}: " + fehlerMeldung + "</span>"
    
    fehlerList.insert(1, message)

    st.markdown(message, unsafe_allow_html=True)

hinweisCount = 0
hinweisList = []

def add_Hinweis(hinweisMeldung,code):
    global hinweisCount 
    hinweisCount += 1

    message = f"<span style='color:orange'> {code}, Hinweis {hinweisCount}: " + hinweisMeldung + "</span>"
    
    hinweisList.insert(1, message)

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

    st.write(possibleList)
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
    
    hinweis = False

    for i in range(len(possibleList)):
        cardNumberInt = get_CarNumber(cardNumber)
        
        if(cardNumberInt == -1):
            add_Hinweis(f"Die Karte <strong>{cardName}</strong> hat keine Kartennummer: <strong>{cardNumber}</strong> mögliche Boxen: <strong>{get_KisteFromPossibleList(df_Expansion,possibleList)}</strong> Schlitten: <strong>{get_SchlittenFromPossibleList(df_Expansion,possibleList)}</strong>", "H1")
            hinweis = True
            return -1,-1,hinweis

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "":
            if (cardNumberInt >= int(schlitteVon[possibleList[i]]) and cardNumberInt <= int(schlitteBis[possibleList[i]])):
                return schlitten[possibleList[i]], kisten[possibleList[i]], hinweis
        else:
             if (condition[possibleList[i]] == cardCondition):
                return schlitten[possibleList[i]], kisten[possibleList[i]], hinweis
   
    add_Hinweis(f"Keine genaue Kiste oder Schlitten konnte für die Karte <strong>{cardName}</strong> mit der Nummer: <strong>{cardNumber}</strong> gefunden werden mögliche Boxen: <strong>{get_KisteFromPossibleList(df_Expansion,possibleList)}</strong> Schlitten: <strong>{get_SchlittenFromPossibleList(df_Expansion,possibleList)}</strong>", "H2")     
    hinweis = True
    return -1,-1, hinweis

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
    listWithCondtion = [] 

    returnList = [] 

    for i in range(len(expansion)):
        if(sellingCardConditon == "NM"):
            if (expansion[i] == sellingCardsExpansion):
                listOnlyExpansion.insert(1, i)  
                if (sellingCardsLanguage == languageDF[i]):
                    listWithLanguage.insert(1, i)  
        else:
            if (sellingCardConditon == condition[i]):
                listWithCondtion.insert(1, i) 
    
    if(len(listOnlyExpansion) > 0 and len(listWithLanguage) == 0 and len(listWithCondtion) == 0):
        add_Fehler(f"Karte <strong>{cardName}</strong> in der Sprache <strong>{sellingCardsLanguage}</strong> konnte nicht gefunden werden. In der Expansion <strong>{sellingCardsExpansion}</strong> zu finden", "F1")     
        fehler = True
    elif(len(listOnlyExpansion) == 0 and len(listWithCondtion) == 0):
        add_Fehler(f"Keinen Eintrag für die Expansion <strong>{sellingCardsExpansion}</strong> gefunden. Karte <strong>{cardName}</strong> in der Sprache <strong>{sellingCardsLanguage}</strong>", "F2")     
        fehler = True
    else:
        for i in range(len(listOnlyExpansion)):
            returnList.insert(1, listOnlyExpansion[i])
        for i in range(len(listWithCondtion)):
             returnList.insert(1, listWithCondtion[i])
 
    return returnList, fehler

expansion_csv = st.file_uploader("Expansion- und Kistenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")      

    if( "Magic the Gathering Einzelkarten" == df_Cards.columns[0]):
        currentLanguage =  Language.deutsch
    
    df_Cards["Kiste"] = ""
    df_Cards["Schlitten"] = ""
    df_Cards["Fehlermeldung"] = "-"
    df_Cards["Hinweis"] = "-"

    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsCondtion = df_Cards["Condition"]

    sellingCardsKiste = df_Cards["Kiste"]
    sellingCardsSchlitte = df_Cards["Schlitten"]
    sellingCardsFehlermeldung = df_Cards["Fehlermeldung"]
    sellingCardsHinweis = df_Cards["Hinweis"]

    sellingCardsName = df_Cards["Localized Article Name"]
    sellingCardsCollectorsNumber = df_Cards["Collector Number"]

    st.title("Fehler:")

    for i in range(len(sellingCardsExpansion)):
       
        possibleExpansionList, fehler = get_List(df_Expansion, sellingCardsExpansion[i], sellingCardsLanguage[i], sellingCardsCondtion[i],sellingCardsName[i])

        if(fehler):
            sellingCardsFehlermeldung[i] = fehlerCount

        if len(possibleExpansionList) > 0:
            schlitte, kiste, hinweis =  get_Schlitten(df_Expansion, sellingCardsCollectorsNumber[i], sellingCardsName[i],sellingCardsCondtion[i], possibleExpansionList)
           
            if(hinweis):
               sellingCardsHinweis[i] = hinweisCount
           
            if(schlitte != -1 and kiste != -1):
                sellingCardsKiste[i] = kiste
                sellingCardsSchlitte[i] = schlitte
     
    st.title("Resultat:")
    st.write(df_Cards)

    resultsCSV = df_Cards.to_csv(index=False, sep=";")

    st.download_button(
        label="CSV herunterladen",
        data=resultsCSV,
        file_name="Resultat_File.csv",
        mime="text/csv"
    )
    
    if(currentLanguage == Language.deutsch):
        bestellungen = df_Cards[["Magic the Gathering Einzelkarten"]].drop_duplicates()
        spaltenname = "Magic the Gathering Einzelkarten"
    else:
        bestellungen = df_Cards[["Magic the Gathering Singles"]].drop_duplicates()
        spaltenname = "Magic the Gathering Singles"

    bestellungen = bestellungen.sort_values(by=spaltenname)

    gefundene_KistenSchlitten = df_Cards[["Kiste", "Schlitten"]].drop_duplicates()
    gefundene_KistenSchlitten = gefundene_KistenSchlitten[(gefundene_KistenSchlitten["Kiste"] != "") & (gefundene_KistenSchlitten["Schlitten"] != "")] 
    gefundene_KistenSchlitten = gefundene_KistenSchlitten.sort_values(by=["Kiste", "Schlitten"])

    for _, row in gefundene_KistenSchlitten.iterrows():
        kiste = row["Kiste"]
        schlitte = row["Schlitten"]          

        temp_df = pd.DataFrame(columns=df_Cards.columns) 

        listKistenSchlitten = get_AllCardsInKisteAndSchlitten(kiste,schlitte,df_Cards)

        for a in listKistenSchlitten:
            zeile = df_Cards.iloc[int(a)]
            temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)
            
        if(len(listKistenSchlitten) > 0):
            st.write(f"Kiste: {kiste}  Schlitten: {schlitte}")
            st.write(temp_df)
 
    
    for i in bestellungen[spaltenname]:
        st.title(f"Bestellung {i}")
        for _, row in gefundene_KistenSchlitten.iterrows():
            temp_df = pd.DataFrame(columns=df_Cards.columns) 
            bestellungList = get_AllCardsFromBestellung(df_Cards, i)
            
            for a in bestellungList:
                zeile = df_Cards.iloc[int(a)]
                temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)
            
        if(len(bestellungList) > 0):
           st.write(temp_df)


#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic 
