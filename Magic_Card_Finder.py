import streamlit as st
import pandas as pd
from enum import Enum

st.set_page_config(page_title="Magic Karten Finder", layout="wide")

st.markdown(f"<span style='color:red; font-size:30px;'>  Wichtig in Expansion Excel Kiste zu Box und Schlitten zu Spalte umbenennen</span>", unsafe_allow_html=True)

st.title("Magic Karten Finder")

class Language(Enum):
    englisch = 1
    deutsch = 2

currentLanguage = Language.englisch

def get_CardForOrderWithErrorMessage(df_Results, bestellung):

    if(currentLanguage == Language.deutsch):
        bestellungen = df_Results["Magic the Gathering Einzelkarten"]
    else:
        bestellungen = df_Results["Magic the Gathering Singles"]

    fehler = df_Results["Fehlermeldung"]

    returnList = []

    for i in range(len(bestellungen)):
        if(bestellung == bestellungen[i] and fehler[i] != "-"):
            returnList.insert(1, i)

    return returnList

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

def get_AllCardsInBoxAndSpalten(box, spalte, df_Results):
    spaltenResults = df_Results["Spalte"]   
    boxResults = df_Results["Box"]   

    returnList = []

    for i in range(len(boxResults)):
        if boxResults[i] != "" and box != "":
            if(int(boxResults[i])==int(box) and spaltenResults[i] == spalte):
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

def get_BoxFromPossibleList(df_Expansion,possibleList):
    box = df_Expansion["Box"]   

    st.write(possibleList)
    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, box[possibleList[i]]) 

    return returnList

def get_SpaltenFromPossibleList(df_Expansion,possibleList):
    spalten = df_Expansion["Spalte"]   

    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, spalten[possibleList[i]]) 

    return returnList

def get_Spalten(df_Expansion, cardNumber, cardName, cardCondition, possibleList):
    spalteVon = df_Expansion["Karten Nummer Von"]   
    spalteBis = df_Expansion["Karten Nummer Bis"]
    spalten = df_Expansion["Spalte"]   
    box = df_Expansion["Box"]   
    condition = df_Expansion["Condition"]
    
    hinweis = False

    for i in range(len(possibleList)):
        cardNumberInt = get_CarNumber(cardNumber)
        
        if(cardNumberInt == -1):
            add_Hinweis(f"Die Karte <strong>{cardName}</strong> hat keine Kartennummer: <strong>{cardNumber}</strong> mögliche Boxen: <strong>{get_BoxFromPossibleList(df_Expansion,possibleList)}</strong> Spalte: <strong>{get_SpaltenFromPossibleList(df_Expansion,possibleList)}</strong>", "H1")
            hinweis = True
            return -1,-1,hinweis

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "":
            if (cardNumberInt >= int(spalteVon[possibleList[i]]) and cardNumberInt <= int(spalteBis[possibleList[i]])):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
        else:
             if (condition[possibleList[i]] == cardCondition):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
   
    add_Hinweis(f"Keine genaue Box oder Spalte konnte für die Karte <strong>{cardName}</strong> mit der Nummer: <strong>{cardNumber}</strong> gefunden werden mögliche Boxen: <strong>{get_BoxFromPossibleList(df_Expansion,possibleList)}</strong> Spalte: <strong>{get_SpaltenFromPossibleList(df_Expansion,possibleList)}</strong>", "H2")     
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

expansion_csv = st.file_uploader("Expansion- und Boxenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")

if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")      

    if( "Magic the Gathering Einzelkarten" == df_Cards.columns[0]):
        currentLanguage =  Language.deutsch
    
    df_Cards["Box"] = ""
    df_Cards["Spalte"] = ""
    df_Cards["Fehlermeldung"] = "-"
    df_Cards["Hinweis"] = "-"

    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsCondtion = df_Cards["Condition"]

    sellingCardsBox = df_Cards["Box"]
    sellingCardsSpalte= df_Cards["Spalte"]
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
            spalte, box, hinweis =  get_Spalten(df_Expansion, sellingCardsCollectorsNumber[i], sellingCardsName[i],sellingCardsCondtion[i], possibleExpansionList)
           
            if(hinweis):
               sellingCardsHinweis[i] = hinweisCount
           
            if(spalte != -1 and box != -1):
                sellingCardsBox[i] = box
                sellingCardsSpalte[i] = spalte
     
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
        bestellungen = df_Cards["Magic the Gathering Einzelkarten"].drop_duplicates()
        spaltenname = "Magic the Gathering Einzelkarten"
    else:
        bestellungen = df_Cards["Magic the Gathering Singles"].drop_duplicates()
        spaltenname = "Magic the Gathering Singles"
    
    bestellungen = bestellungen.sort_values()

    orderID = df_Cards["Order ID"].drop_duplicates()
    orderID = orderID.sort_values()

    gefundene_BoxSpalte = df_Cards[["Box", "Spalte"]].drop_duplicates()
    gefundene_BoxSpalte = gefundene_BoxSpalte[(gefundene_BoxSpalte["Box"] != "") & (gefundene_BoxSpalte["Spalte"] != "")] 

    gefundene_BoxSpalte["Box"] = pd.to_numeric(gefundene_BoxSpalte["Box"], errors="coerce")
    gefundene_BoxSpalte["Spalte"] = pd.to_numeric(gefundene_BoxSpalte["Spalte"], errors="coerce")
    gefundene_BoxSpalte = gefundene_BoxSpalte.sort_values(by=["Box"], ascending=True)

    for _, row in gefundene_BoxSpalte.iterrows():
        box = row["Box"]
        spalte = row["Spalte"]          

        temp_df = pd.DataFrame(columns=df_Cards.columns) 
        
        listBoxSpalte = get_AllCardsInBoxAndSpalten(box,spalte,df_Cards)

        for a in listBoxSpalte:
            zeile = df_Cards.iloc[int(a)]
            temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)
            
        if(len(listBoxSpalte) > 0):
          
            st.markdown(f"<span style='font-size:30px;'>Box: {int(box)} - {int(spalte)}</span>", unsafe_allow_html=True)

            temp_df = temp_df.drop(temp_df.columns[6], axis=1)
            temp_df = temp_df.drop(temp_df.columns[3], axis=1)
            temp_df = temp_df.drop("Product ID", axis=1)
            temp_df = temp_df.drop("Comments", axis=1)
            temp_df = temp_df.drop("Order ID", axis=1)
            temp_df = temp_df.drop("Rarity", axis=1)
            temp_df = temp_df.drop("Box", axis=1)
            temp_df = temp_df.drop("Spalte", axis=1)
            temp_df = temp_df.drop("Fehlermeldung", axis=1)
            temp_df = temp_df.drop("Hinweis", axis=1)

            spalte = temp_df.pop("Collector Number")
         
            temp_df.insert(1,"Collector Number",spalte)

            spalte = temp_df.pop(temp_df.columns[0])

            temp_df["Bestellung"] = spalte

            spalte = temp_df.pop("Expansion")

            temp_df.insert(0,"Expansion",spalte)

            temp_df = temp_df.rename(columns={"-": "Stückzahl"})

            st.write(temp_df)
    
    st.title("Bestellungen:")

    for i in range(len(bestellungen)):
     
        bestellungsID = bestellungen.iloc[i]
      
        order = orderID.iloc[i] 

        st.markdown(f"<span style='font-size:35px;'>Bestellung {bestellungsID} #{int(order):,}</span>", unsafe_allow_html=True)

        for _, row in gefundene_BoxSpalte.iterrows():
            temp_df = pd.DataFrame(columns=df_Cards.columns) 
            bestellungList = get_AllCardsFromBestellung(df_Cards, bestellungsID)
            
            for a in bestellungList:
                zeile = df_Cards.iloc[int(a)]
                temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)
       
        if(len(bestellungList) > 0):
            temp_df = temp_df.drop(temp_df.columns[6], axis=1)
            temp_df = temp_df.drop(temp_df.columns[3], axis=1)
            temp_df = temp_df.drop("Product ID", axis=1)
            temp_df = temp_df.drop("Comments", axis=1)
            temp_df = temp_df.drop("Order ID", axis=1)
            temp_df = temp_df.drop("Rarity", axis=1)
            temp_df = temp_df.drop("Collector Number", axis=1)
            temp_df = temp_df.drop("Box", axis=1)
            temp_df = temp_df.drop("Spalte", axis=1)
            temp_df = temp_df.drop("Hinweis", axis=1)
            temp_df = temp_df.drop(temp_df.columns[0], axis=1)

            spalte = temp_df.pop("Expansion")

            temp_df.insert(0,"Expansion",spalte)

            temp_df = temp_df.rename(columns={"-": "Stückzahl"})

            st.write(temp_df)


#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic 
