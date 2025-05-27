import streamlit as st
import pandas as pd
from enum import Enum

st.set_page_config(page_title="Magic Karten Finder", layout="wide")

st.markdown(f"<span style='color:red; font-size:30px;'>  Wichtig Spalte zu Fach umbenennen</span>", unsafe_allow_html=True)

st.title("Magic Karten Finder")

class Language(Enum):
    englisch = 1
    deutsch = 2

currentLanguage = Language.englisch

fehlerList = []
hinweisList = []

def get_CurrentLanguageRowText():
    if(currentLanguage == Language.deutsch):
        return "Magic the Gathering Einzelkarten"
    else:
        return "Magic the Gathering Singles"

def add_Fehler(fehlerMeldung, code):
    message = f"<span style='color:red'>{code}, Fehler {len(fehlerList) + 1}: " + fehlerMeldung + "</span>"
    
    fehlerList.append({"code": code, "message": message})

def add_Hinweis(hinweisMeldung, code):

    message = f"<span style='color:orange'> {code}, Hinweis {len(hinweisList) + 1}: " + hinweisMeldung + "</span>"
    
    hinweisList.append({"code": code, "message": message})

def showErrorsAndHints():
    st.title("Fehler:")
    
    for i in range(len(fehlerList)): 
        st.markdown(fehlerList[i]["message"], unsafe_allow_html=True)

    st.title("Hinweise:")
    
    for i in range(len(hinweisList)): 
        st.markdown(hinweisList[i]["message"], unsafe_allow_html=True)

def get_CardNumber(cardNumber):
    if str(cardNumber)[0].isalpha():
        return 0
    if str(cardNumber) == "-":
        return -1
    else:
        return int(cardNumber)

def get_AllCardsFromBestellung(df_Results, bestellung):

    bestellungen = df_Results[get_CurrentLanguageRowText()]

    returnList = []

    for i in range(len(bestellungen)):
        if(bestellung == bestellungen[i]):
            returnList.append(i)

    return returnList

def get_AllCardsInBoxAndSpalten(box, spalte, df_Results):
    spaltenResults = df_Results["Fach"]   
    boxResults = df_Results["Box"]   

    returnList = []

    for i in range(len(boxResults)):
        if boxResults[i] != "" and box != "":
            if(int(boxResults[i])==int(box) and spaltenResults[i] == spalte):
                returnList.append(i)

    return returnList

def get_BoxFromPossibleList(df_Expansion, possibleList):
    box = df_Expansion["Box"]   

    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, box[possibleList[i]]) 

    return returnList

def get_SpaltenFromPossibleList(df_Expansion,possibleList):
    spalten = df_Expansion["Fach"]   

    returnList = []

    for i in range(len(possibleList)):
        returnList.insert(1, spalten[possibleList[i]]) 

    return returnList

def get_Spalten(df_Expansion, cardNumber, cardName, cardCondition, possibleList):
    spalteVon = df_Expansion["Karten Nummer Von"]   
    spalteBis = df_Expansion["Karten Nummer Bis"]
    spalten = df_Expansion["Fach"]   
    box = df_Expansion["Box"]   
    condition = df_Expansion["Condition"]
    
    hinweis = False

    for i in range(len(possibleList)):
        cardNumberInt = get_CardNumber(cardNumber)
        
        if(cardNumberInt == -1):
            add_Hinweis(f"Die Karte <strong>{cardName}</strong> hat keine Kartennummer: <strong>{cardNumber}</strong> mögliche Boxen: <strong>{get_BoxFromPossibleList(df_Expansion,possibleList)}</strong> Fach: <strong>{get_SpaltenFromPossibleList(df_Expansion,possibleList)}</strong>", "H1")
            hinweis = True
            return -1,-1,hinweis

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "":
            if (cardNumberInt >= int(spalteVon[possibleList[i]]) and cardNumberInt <= int(spalteBis[possibleList[i]])):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
        else:
             if (condition[possibleList[i]] == cardCondition):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
   
    add_Hinweis(f"Keine genaue Box oder Fach konnte für die Karte <strong>{cardName}</strong> mit der Nummer: <strong>{cardNumber}</strong> gefunden werden mögliche Boxen: <strong>{get_BoxFromPossibleList(df_Expansion,possibleList)}</strong> Fach: <strong>{get_SpaltenFromPossibleList(df_Expansion,possibleList)}</strong>", "H2")     
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
        for i in range(len(listWithLanguage)):
            returnList.insert(1, listWithLanguage[i])
        for i in range(len(listWithCondtion)):
             returnList.insert(1, listWithCondtion[i])
 
    return returnList, fehler

def get_getColumnsFromDFWithList(list, df):
    temp_df = pd.DataFrame(columns=df.columns) 
 
    for a in list:
        zeile = df.iloc[int(a)]
        temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)

    return temp_df
    
def mainSortFunction(df_Cards, df_Expansion):

    df_Cards["Box"] = ""
    df_Cards["Fach"] = ""
    df_Cards["Fehlermeldung"] = "-"
    df_Cards["Hinweis"] = "-"

    sellingCardsLanguage = df_Cards["Language"]
    sellingCardsExpansion = df_Cards["Expansion"]
    sellingCardsCondtion = df_Cards["Condition"]
    sellingCardsBox = df_Cards["Box"]
    sellingCardsSpalte= df_Cards["Fach"]
    sellingCardsFehlermeldung = df_Cards["Fehlermeldung"]
    sellingCardsHinweis = df_Cards["Hinweis"]
    sellingCardsName = df_Cards["Localized Article Name"]
    sellingCardsCollectorsNumber = df_Cards["Collector Number"]

    for i in range(len(sellingCardsExpansion)):
        possibleExpansionList, fehler = get_List(df_Expansion, sellingCardsExpansion[i], sellingCardsLanguage[i], sellingCardsCondtion[i],sellingCardsName[i])

        if(fehler):
            sellingCardsFehlermeldung[i] = fehlerList[len(fehlerList) - 1]["code"]

        if len(possibleExpansionList) > 0:
            spalte, box, hinweis =  get_Spalten(df_Expansion, sellingCardsCollectorsNumber[i], sellingCardsName[i],sellingCardsCondtion[i], possibleExpansionList)
           
            if(hinweis):
               sellingCardsHinweis[i] = hinweisList[len(hinweisList) - 1]["code"]
           
            if(spalte != -1 and box != -1):
                sellingCardsBox[i] = box
                sellingCardsSpalte[i] = spalte

    return df_Cards

def showResult(df_Cards):
    st.title("Resultat:")
    st.write(df_Cards)

    resultsCSV = df_Cards.to_csv(index=False, sep=";")

    st.download_button(
        label="CSV herunterladen",
        data=resultsCSV,
        file_name="Resultat_File.csv",
        mime="text/csv"
    )

def getCardsSortedToBoxes(df_Cards):
    gefundene_BoxSpalte = df_Cards[["Box", "Fach"]].drop_duplicates()
    gefundene_BoxSpalte = gefundene_BoxSpalte[(gefundene_BoxSpalte["Box"] != "") & (gefundene_BoxSpalte["Fach"] != "")] 
    gefundene_BoxSpalte["Box"] = pd.to_numeric(gefundene_BoxSpalte["Box"], errors="coerce")
    gefundene_BoxSpalte["Fach"] = pd.to_numeric(gefundene_BoxSpalte["Fach"], errors="coerce")
    gefundene_BoxSpalte = gefundene_BoxSpalte.sort_values(by=["Box","Fach"], ascending=True)
   
    boxList = []

    for _, row in gefundene_BoxSpalte.iterrows():
        box = row["Box"]
        spalte = row["Fach"]          
                
        listBoxSpalte = get_AllCardsInBoxAndSpalten(box,spalte,df_Cards)

        temp_df = get_getColumnsFromDFWithList(listBoxSpalte,df_Cards)

        if(len(listBoxSpalte) > 0): 
            temp_df = temp_df.drop(temp_df.columns[6], axis=1)
            temp_df = temp_df.drop(temp_df.columns[3], axis=1)
            temp_df = temp_df.drop("Product ID", axis=1)
            temp_df = temp_df.drop("Comments", axis=1)
            temp_df = temp_df.drop("Order ID", axis=1)
            temp_df = temp_df.drop("Rarity", axis=1)
            temp_df = temp_df.drop("Box", axis=1)
            temp_df = temp_df.drop("Fach", axis=1)
            temp_df = temp_df.drop("Fehlermeldung", axis=1)
            temp_df = temp_df.drop("Hinweis", axis=1)

            spalteTemp = temp_df.pop("Collector Number")
         
            temp_df.insert(1,"Collector Number",spalteTemp)

            spalteTemp = temp_df.pop(temp_df.columns[0])

            temp_df["Bestellung"] = spalteTemp

            spalteTemp = temp_df.pop("Expansion")

            temp_df.insert(0,"Expansion",spalteTemp)

            temp_df = temp_df.rename(columns={"-": "Stückzahl"})
            
            boxList.append({"Box": box ,"Spalte": spalte, "df": temp_df})

    return boxList

def showBoxesResults(boxList):
    for i in range(len(boxList)): 
        st.markdown(f"<span style='font-size:30px;'>Box: {int(boxList[i]['Box'])} - {int(boxList[i]['Spalte'])}</span>", unsafe_allow_html=True)

        st.write(boxList[i]["df"])

def getCardsSortedToBestellungen(df_Cards):
    spaltenname = get_CurrentLanguageRowText()
    
    bestellungen = df_Cards[spaltenname].drop_duplicates()
    bestellungen = bestellungen.sort_values()

    orderID = df_Cards["Order ID"].drop_duplicates()
    orderID = orderID.sort_values()
 
    returnList = []

    for i in range(len(bestellungen)):
        bestellungsID = bestellungen.iloc[i]
      
        order = orderID.iloc[i] 

        bestellungList = get_AllCardsFromBestellung(df_Cards, bestellungsID)
        
        temp_df = get_getColumnsFromDFWithList(bestellungList,df_Cards)
       
        if(len(bestellungList) > 0):
            temp_df = temp_df.drop(temp_df.columns[6], axis=1)
            temp_df = temp_df.drop(temp_df.columns[3], axis=1)
            temp_df = temp_df.drop("Product ID", axis=1)
            temp_df = temp_df.drop("Comments", axis=1)
            temp_df = temp_df.drop("Order ID", axis=1)
            temp_df = temp_df.drop("Rarity", axis=1)
            temp_df = temp_df.drop("Collector Number", axis=1)
            temp_df = temp_df.drop("Box", axis=1)
            temp_df = temp_df.drop("Fach", axis=1)
            temp_df = temp_df.drop("Hinweis", axis=1)
            temp_df = temp_df.drop(temp_df.columns[0], axis=1)

            spalteTemp = temp_df.pop("Expansion")

            temp_df.insert(0,"Expansion",spalteTemp)

            temp_df = temp_df.rename(columns={"-": "Stückzahl"})

            returnList.append({"Bestellung": bestellungsID ,"OrderID": order, "df": temp_df})
    return returnList

def highlight_row(row):
    if row["Fehlermeldung"] != "-":
        return ["color: red; font-weight: bold"] * len(row)
    else:
        return [""] * len(row)
    
def showBestellungenResults(list):
    st.title("Bestellungen:")

    for i in range(len(list)): 
        st.markdown(f"<span style='font-size:35px;'>Bestellung {int(list[i]['Bestellung'])} #{int(list[i]['OrderID']):,}</span>", unsafe_allow_html=True)

        st.dataframe(list[i]["df"].style.apply(highlight_row, axis=1))

expansion_csv = st.file_uploader("Expansion- und Boxenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")


if expansion_csv:
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")
    
    df_Expansion["Condition"] = df_Expansion["Condition"].fillna("NM")

    conditions = df_Expansion["Condition"].drop_duplicates().dropna()

    expansions = df_Expansion["Expansion"].drop_duplicates().dropna()
    
    expansions = expansions.sort_values(key=lambda col: col.str.lower())

    language = df_Expansion["Language"].drop_duplicates().dropna()

    col1, col2, col3 = st.columns(3)

    condition_list = ["-- Alle --"] + conditions.tolist()
    expansion_list = ["-- Alle --"] + expansions.tolist()
    language_list = ["-- Alle --"] + language.tolist()

    with col1:
        auswahl1 = st.selectbox("Condition", condition_list)

    with col2:
        auswahl2 = st.selectbox("Expansion", expansion_list)

    with col3:
        auswahl3 = st.selectbox("Edition", language_list)

    gefiltert = df_Expansion.copy()

    if auswahl1 != "-- Alle --":
       gefiltert = gefiltert[gefiltert["Condition"] == auswahl1]

    if auswahl2 != "-- Alle --":
      gefiltert = gefiltert[gefiltert["Expansion"] == auswahl2]

    if auswahl3 != "-- Alle --":
      gefiltert = gefiltert[gefiltert["Language"] == auswahl3]

    st.write("Gefilterte Ergebnisse:", gefiltert)


if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")

    df_CardsCopy = df_Cards.copy()

    if( "Magic the Gathering Einzelkarten" == df_CardsCopy.columns[0]):
        currentLanguage =  Language.deutsch

    df_CardsCopy = mainSortFunction(df_CardsCopy, df_Expansion)

    showErrorsAndHints()
     
    showResult(df_CardsCopy)
    
    boxList = getCardsSortedToBoxes(df_CardsCopy)

    showBoxesResults(boxList)

    bestellungenList = getCardsSortedToBestellungen(df_CardsCopy)

    showBestellungenResults(bestellungenList)


#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic 
