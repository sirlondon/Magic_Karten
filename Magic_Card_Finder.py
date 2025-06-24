import streamlit as st
import pandas as pd
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from reportlab.pdfgen import canvas # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle # type: ignore
from reportlab.lib import colors # type: ignore # type: ignore
from PyPDF2 import PdfMerger # type: ignore
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
import os

# Nur falls du in Streamlit Cloud bist
os.system("apt-get update")
os.system("apt-get install -y wget unzip xvfb libxi6 libgconf-2-4")
os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
os.system("dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install")

st.set_page_config(page_title="Magic Karten Finder", layout="wide")

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

def get_IndexFromPossibleList(df_Expansion, possibleList, column):
    returnVa = df_Expansion[column]   
    
    returnList = []

    for i in range(len(possibleList)):
        returnList.append(returnVa[possibleList[i]]) 

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
            if(len(possibleList) == 1):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
            else:
                add_Hinweis(f"Die Karte <strong>{cardName}</strong> hat keine Kartennummer: <strong>{cardNumber}</strong> mögliche Boxen: <strong>{', '.join(map(str, get_IndexFromPossibleList(df_Expansion,possibleList, 'Box')))}</strong> Fach: <strong>{', '.join(map(str, ([int(x) for x in get_IndexFromPossibleList(df_Expansion,possibleList, 'Fach')])))}</strong>", "H1")
                hinweis = True
                return -1,-1,hinweis

        if pd.isna(condition.iloc[possibleList[i]]) or condition.iloc[possibleList[i]] == "" or condition.iloc[possibleList[i]] == "NM":
            if (cardNumberInt >= int(spalteVon[possibleList[i]]) and cardNumberInt <= int(spalteBis[possibleList[i]])):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
        else:
             if (condition[possibleList[i]] == cardCondition):
                return spalten[possibleList[i]], box[possibleList[i]], hinweis
   
    add_Hinweis(f"Keine genaue Box oder Fach konnte für die Karte <strong>{cardName}</strong> mit der Nummer: <strong>{cardNumber}</strong> gefunden werden mögliche Boxen: <strong>{', '.join(map(str, get_IndexFromPossibleList(df_Expansion,possibleList, 'Box')))}</strong> Fach: <strong>{', '.join(map(str, ([int(x) for x in get_IndexFromPossibleList(df_Expansion,possibleList, 'Fach')])))}</strong>", "H2")     
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
    
    unique = list(set(returnList))

    return unique, fehler

def get_getColumnsFromDFWithList(list, df):
    temp_df = pd.DataFrame(columns=df.columns) 
 
    for a in list:
        zeile = df.iloc[int(a)]
        temp_df = pd.concat([temp_df, zeile.to_frame().T], ignore_index=True)

    return temp_df


CardsWithHint = []

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
               CardsWithHint.append({"PossibleList": possibleExpansionList ,"ID": i, "Gefunden": False})

            if(spalte != -1 and box != -1):
                sellingCardsBox[i] = int(box)
                sellingCardsSpalte[i] = int(spalte)

    return df_Cards

def showResult(df_Cards):
    st.title("Resultat:")

    df = df_Cards.copy()
    df.index = df.index + 1
    st.dataframe(df.style.apply(highlight_combined, axis=1))
    
    resultsCSV = df_Cards.to_csv(index=False, sep=";")

    st.download_button(
        label="CSV herunterladen",
        data=resultsCSV,
        file_name="Resultat_File.csv",
        mime="text/csv"
    )

def showCardsWithHint(df_Cards, df_Expansion):
    st.title("Hinweis Karten:")

    sellingCardsName = df_Cards["Localized Article Name"]
    spalten = df_Expansion["Fach"]   
    box = df_Expansion["Box"]   

    for i in range(len(CardsWithHint)): 
        st.markdown(f"<span style='font-size:30px;'>{sellingCardsName.loc[CardsWithHint[i]['ID']]}</span>", unsafe_allow_html=True)
        
        CardsWithHint[i]["Gefunden"] = st.checkbox("Gefunden " + sellingCardsName.loc[CardsWithHint[i]['ID']], value=False)
        
        if CardsWithHint[i]["Gefunden"] == False:
            temp_df = df_Cards.iloc[[CardsWithHint[i]['ID']]]

            temp_df = ColumnOutputForBoxes(temp_df)
            
            posList = CardsWithHint[i]['PossibleList']
        
            st.dataframe(temp_df)

            st.markdown("<span style='font-size:25px;'>Mögliche Boxen:</span>", unsafe_allow_html=True)
        
            resultList = []
            for a in range(len(posList)):
                resultList.append({"Box":box[posList[a]], "Spalte": spalten[posList[a]]})
        
            df = pd.DataFrame(resultList)
            df = df.drop_duplicates()
            resultList = df.to_dict(orient="records")

            for a in range(len(resultList)):
                st.markdown(f"<span style='font-size:20px;'>Box:  {str(resultList[a]['Box'])} Spalte: {str(resultList[a]['Spalte'])}</span>",unsafe_allow_html=True) 

def showCardsWithHintFound(df_Cards, df_Expansion):
    st.title("Gefunde Hinweis Karten:")

    sellingCardsName = df_Cards["Localized Article Name"]
    spalten = df_Expansion["Fach"]   
    box = df_Expansion["Box"]   

    for i in range(len(CardsWithHint)): 
        if CardsWithHint[i]["Gefunden"] == True:
            st.markdown(f"<span style='font-size:30px;'>{sellingCardsName.loc[CardsWithHint[i]['ID']]}</span>", unsafe_allow_html=True)
        
            temp_df = df_Cards.iloc[[CardsWithHint[i]['ID']]]

            temp_df = ColumnOutputForBoxes(temp_df)
            
            posList = CardsWithHint[i]['PossibleList']
        
            st.dataframe(temp_df)

            st.markdown("<span style='font-size:25px;'>Mögliche Boxen:</span>", unsafe_allow_html=True)
        
            resultList = []
            for a in range(len(posList)):
                resultList.append({"Box":box[posList[a]], "Spalte": spalten[posList[a]]})
        
            df = pd.DataFrame(resultList)
            df = df.drop_duplicates()
            resultList = df.to_dict(orient="records")

            for a in range(len(resultList)):
                st.markdown(f"<span style='font-size:20px;'>Box:  {str(resultList[a]['Box'])} Spalte: {str(resultList[a]['Spalte'])}</span>",unsafe_allow_html=True) 

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
            temp_df = ColumnOutputForBoxes(temp_df)
            
            boxList.append({"Box": box ,"Spalte": spalte, "df": temp_df,"Gefunden": False})

    return boxList

def ColumnOutputForBoxes(temp_df):
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
            
    return temp_df

def showBoxesResults(boxList):
    st.title("Verkaufte Karten:")

    for i in range(len(boxList)): 
        
        st.markdown(
                f"<span style='font-size:30px;'>Box: {int(boxList[i]['Box'])} - {int(boxList[i]['Spalte'])}</span>",
                unsafe_allow_html=True
            )
        
        boxList[i]["Gefunden"] = st.checkbox(f"Box {int(boxList[i]['Box'])} - {int(boxList[i]['Spalte'])} gefunden", value=False)

        if boxList[i]["Gefunden"] == False:
            df = boxList[i]["df"].copy()
            df.index = df.index + 1
            st.dataframe(df)
        
    return boxList

def showBoxesGefunden(boxList):
    st.title("Gefundene Karten:")

    for i in range(len(boxList)): 
        if boxList[i]["Gefunden"] == True:
            st.markdown(
                f"<span style='font-size:30px;'>Box: {int(boxList[i]['Box'])} - {int(boxList[i]['Spalte'])}</span>",
                unsafe_allow_html=True
            )
        
            df = boxList[i]["df"].copy()
            df.index = df.index + 1
            st.dataframe(df)
                  
    return boxList

def getCardsSortedToBestellungen(df_Cards, cut = True):
    spaltenname = get_CurrentLanguageRowText()
    
    bestellungOrderSpalte = df_Cards[[spaltenname, "Order ID"]].drop_duplicates()
    bestellungOrderSpalte[spaltenname] = pd.to_numeric(bestellungOrderSpalte[spaltenname], errors="coerce")
    bestellungOrderSpalte["Order ID"] = pd.to_numeric(bestellungOrderSpalte["Order ID"], errors="coerce")
    bestellungOrderSpalte = bestellungOrderSpalte.sort_values(by=[spaltenname,"Order ID"], ascending=True)
 
    returnList = []

    for i in range(len(bestellungOrderSpalte[spaltenname])):
        bestellungsID = bestellungOrderSpalte[spaltenname].iloc[i]
      
        order = bestellungOrderSpalte["Order ID"].iloc[i] 

        bestellungList = get_AllCardsFromBestellung(df_Cards, bestellungsID)
        
        temp_df = get_getColumnsFromDFWithList(bestellungList,df_Cards)
       
        if(len(bestellungList) > 0):
            if(cut):
                temp_df = ColumnOutputForBestellungen(temp_df)

            returnList.append({"Bestellung": bestellungsID ,"OrderID": order, "df": temp_df})
    return returnList

def ColumnOutputForBestellungen(temp_df):
    temp_df = temp_df.drop(temp_df.columns[6], axis=1)
    temp_df = temp_df.drop(temp_df.columns[3], axis=1)
    temp_df = temp_df.drop("Product ID", axis=1)
    temp_df = temp_df.drop("Comments", axis=1)
    temp_df = temp_df.drop("Order ID", axis=1)
    temp_df = temp_df.drop("Rarity", axis=1)
    temp_df = temp_df.drop("Collector Number", axis=1)
    temp_df = temp_df.drop("Box", axis=1)
    temp_df = temp_df.drop("Fach", axis=1)
    temp_df = temp_df.drop(temp_df.columns[0], axis=1)

    spalteTemp = temp_df.pop("Expansion")

    temp_df.insert(0,"Expansion",spalteTemp)

    temp_df = temp_df.rename(columns={"-": "Stückzahl"})

    return temp_df

def highlight_combined(row):
    styles = []
    for col in row.index:
        style = ""
        if row["Fehlermeldung"] != "-" and col in row.index:
            style += "color: red; font-weight: bold;"
        if row["Hinweis"] != "-" and col in row.index:
            style += "color: orange; font-weight: bold;"  # Achtung: überschreibt evtl. rot
        styles.append(style)
    return styles

       
def showBestellungenResults(list):
    st.title("Bestellungen:")

    for i in range(len(list)): 
        linkText = "https://www.cardmarket.com/en/Magic/Orders/" + str(list[i]['OrderID'])
      
        st.markdown(f"<span style='font-size:35px;'>Bestellung {int(list[i]['Bestellung'])} [#{int(list[i]['OrderID']):,}]({linkText})</span>", unsafe_allow_html=True)

        df = list[i]["df"].copy()
        df.index = df.index + 1
        st.dataframe(df.style.apply(highlight_combined, axis=1))

def ColumnOutputForPDF(temp_df):
    st.write(temp_df)

    spalteTemp = temp_df.pop(temp_df.columns[2])

    temp_df.insert(0,"Stückzahl",spalteTemp)

    spalteTemp = temp_df.pop(temp_df.columns[6])

    temp_df.insert(15,"Price",spalteTemp)

    temp_df = temp_df.drop("Product ID", axis=1)
    temp_df = temp_df.drop("Order ID", axis=1)
    temp_df = temp_df.drop("Rarity", axis=1)
    temp_df = temp_df.drop("Box", axis=1)
    temp_df = temp_df.drop("Fach", axis=1)
    temp_df = temp_df.drop("Expansion", axis=1)
    temp_df = temp_df.drop(get_CurrentLanguageRowText(), axis=1)
    temp_df = temp_df.drop("Fehlermeldung", axis=1)
    temp_df = temp_df.drop("Hinweis", axis=1)
    temp_df = temp_df.drop("isFoil", axis=1)
    temp_df = temp_df.drop("isSigned", axis=1)
    temp_df = temp_df.drop("isAltered", axis=1)
    temp_df = temp_df.drop(temp_df.columns[1], axis = 1)

    spalteTemp = temp_df.pop("Collector Number")

    temp_df.insert(2,"Collector Number",spalteTemp)

    spalteTemp = temp_df.pop("Language")

    temp_df.insert(3,"Language",spalteTemp)

    spalteTemp = temp_df.pop("Comments")

    temp_df.insert(5,"Comments",spalteTemp)

    st.write(temp_df)

    return temp_df
def getAllLinks(list):
    order_urls = []

    for i in range(len(list)): 
        linkText =  "https://www.cardmarket.com/en/Magic/Orders/" + str(list[i]['OrderID'])
        order_urls.append(linkText)
    
    return order_urls

def getShipping(url, driver):
    driver.get(url)
    time.sleep(0.5)
    
    try:
        div = driver.find_element(By.CSS_SELECTOR, "div.text-danger")
        full_text = div.text

        first_part = full_text.split("|")[1].strip()
        
        dd = driver.find_element(By.CSS_SELECTOR, "dd.col-12.col-md-8.col-lg-9")

        spans = dd.find_elements(By.TAG_NAME, "span")

        brief_text = spans[1].text     

        return {
            "Method": brief_text,
            "Trust": first_part,
        }
    except:
        return {"Fehler": "❌ Adresse nicht gefunden"}

def getPayment(url, driver):
    driver.get(url)
    time.sleep(0.5)
    
    try:
        summary = driver.find_element(By.CSS_SELECTOR, ".summary")
    
        article_count = summary.get_attribute("data-article-count")
        item_value = summary.get_attribute("data-item-value")
        shipping_price = summary.get_attribute("data-shipping-price")
        total_price = summary.get_attribute("data-total-price")

        return {
            "Contents": article_count,
            "Article Value": item_value,
            "Shipping": shipping_price,
            "Total": total_price,
        }
    except:
        return {"Fehler": "❌ Adresse nicht gefunden"}

def getAddress(url, driver):
    driver.get(url)
    time.sleep(7) 

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, "#labelShippingAddress button")
        toggle_button.click()
        time.sleep(1)
    except:
        print()

    try:
        name = driver.find_element(By.CSS_SELECTOR, "#ShippingAddress .Name").text
        street = driver.find_element(By.CSS_SELECTOR, "#ShippingAddress .Street").text
        city = driver.find_element(By.CSS_SELECTOR, "#ShippingAddress .City").text
        country = driver.find_element(By.CSS_SELECTOR, "#ShippingAddress .Country").text
        user_link_element = driver.find_element(By.CSS_SELECTOR, 'a[href*="/en/Magic/Users/"]')

        return {
            "User": user_link_element.text,
            "Empfänger": name,
            "Straße": street,
            "Stadt": city,
            "Land": country
        }
    except:
        return {"Fehler": "❌ Adresse nicht gefunden"}

def getData(list, i):
    order_urls = getAllLinks(list)
 
    # Selenium setup
    options = Options()
    options.headless = False  # or True if no GUI available
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = order_urls[i]

    resultAddress = getAddress(url, driver)
    resultPayment = getPayment(url, driver)
    resultShipping = getShipping(url, driver)

    driver.quit()

    return resultAddress, resultPayment, resultShipping

def draw_table(c, data, x_start=45, y_start=500, row_height=14):
    for row_num, row in enumerate(data):
        if(row_num != 0):  
            start = x_start
            for col_num, cell in enumerate(row):
                addval = 0
                if(col_num == 0):
                   addval = 0
                if(col_num == 1):
                    addval = 15 
                if(col_num == 2):
                    addval = 225
                if(col_num == 3):
                    addval = 25
                if(col_num == 4):
                    addval = 50
                if(col_num == 5):
                    addval = 25
                if(col_num == 6):
                    addval = 150

                start += addval
                c.drawString(start, y_start - row_num * row_height, str(cell)) 

    

def createPDFs(list):
    if(st.button("Load Data")):
        pdfs = []
        for i in range(len(list)): 
            temp = ("Sale #" + str(list[i]['OrderID']))
            pdfs.append(temp)
            c = canvas.Canvas(pdfs[i])
            c.setFont("Helvetica", 15)
            c.drawString(45, 790, str(temp))

            address, payment, shipping = getData(list, i)
            
            c.setFont("Helvetica", 10)

            message = "Buyer - " + str(address["User"])
            c.drawString(305, 734, message)

            c.setFont("Helvetica", 10)
            a = 0

            for key, value in address.items():
                if (key != "User"):
                    c.drawString(305, 720 - (14 * a), str(value))
                    a += 1
            
            c.drawString(45, 734, "Seller - mimtelf")
            c.drawString(45, 720, "Mario Milanollo")
            c.drawString(45, 706, "Neuhausgasse 1")
            c.drawString(45, 692, "7202 Bad Sauerbrunn")
            c.drawString(45, 678, "Austria")

            c.drawString(45, 660, "Contents")
            c.drawString(45, 646, "Article Value")
            c.drawString(45, 632, "Shipping")
            c.drawString(45, 618, "Total")

            c.drawString(130, 660, str(payment["Contents"]) + " articles")
            c.drawString(130, 646, str(payment["Article Value"]) + " EUR")
            c.drawString(130, 632, str(payment["Shipping"]) + " EUR")
            c.drawString(130, 618, str(payment["Total"]) + " EUR")

            c.drawString(130, 632, str(payment["Shipping"]) + " EUR")
            c.drawString(130, 618, str(payment["Total"]) + " EUR")

            c.drawString(45, 590, "Shipping Method " + str(shipping["Method"]))
            c.drawString(45, 576, str(shipping["Trust"]))

            df = list[i]["df"].copy()
            df.index += 1
            df = ColumnOutputForPDF(df)
            data = [df.columns.tolist()] + df.values.tolist()

            draw_table(c, data, x_start=45, y_start=500)
            c.save()
        
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        output_path = "merged_output.pdf"
        merger.write(output_path)
        merger.close()

        # Load final PDF into memory
        with open(output_path, "rb") as f:
            pdf_data = f.read()

        # Provide download button
        st.download_button("Download PDF", data=pdf_data, file_name="merged_output.pdf", mime="application/pdf")

expansion_csv = st.file_uploader("Expansion- und Boxenliste hochladen", type="csv")
sellingCards_csv = st.file_uploader("Gesuchte Karten hochladen", type="csv")


if expansion_csv:
    df_Expansion = pd.read_csv(expansion_csv, sep=";", encoding="utf-8")
    
    df_Expansion["Condition"] = df_Expansion["Condition"].fillna("NM")

    conditions = df_Expansion["Condition"].drop_duplicates().dropna()

    expansionsDeutsch = df_Expansion["Expansion deutsch"].drop_duplicates().dropna()
    expansionsEnglisch = df_Expansion["Expansion"].drop_duplicates().dropna()

    expansionsEnglisch = expansionsEnglisch.sort_values(key=lambda col: col.str.lower())
    expansionsDeutsch = expansionsDeutsch.sort_values(key=lambda col: col.str.lower())

    language = df_Expansion["Language"].drop_duplicates().dropna()

    col1, col2, col3, col4 = st.columns(4)

    condition_list = ["-- Alle --"] + conditions.tolist()
    language_list = ["-- Alle --"] + language.tolist()
    
    englisch = True
    
    with col1:
        auswahl1 = st.selectbox("Condition", condition_list)

    with col3:
        englisch = st.checkbox("Englisch", englisch)    
 
    with col2:
        if(englisch):
            expansion_list = ["-- Alle --"] + expansionsEnglisch.tolist()
            auswahl2 = st.selectbox("Expansion", expansion_list)
        else:
            expansion_list = ["-- Alle --"] + expansionsDeutsch.tolist()
            auswahl2 = st.selectbox("Expansion deutsch", expansion_list)
    with col4:
        auswahl3 = st.selectbox("Sprache", language_list)

    gefiltert = df_Expansion.copy()

    if auswahl1 != "-- Alle --":
       gefiltert = gefiltert[gefiltert["Condition"] == auswahl1]

    if auswahl2 != "-- Alle --":
        if(englisch):
            gefiltert = gefiltert[gefiltert["Expansion"] == auswahl2]
        else:
            gefiltert = gefiltert[gefiltert["Expansion deutsch"] == auswahl2]

    if auswahl3 != "-- Alle --":
      gefiltert = gefiltert[gefiltert["Language"] == auswahl3]

    st.write("Gefilterte Ergebnisse:", gefiltert)


if sellingCards_csv and expansion_csv:
    df_Cards = pd.read_csv(sellingCards_csv, sep=";", encoding="utf-8")

    df_Cards = df_Cards.sort_values(by=[get_CurrentLanguageRowText(),"Order ID"])

    df_Cards = df_Cards.reset_index(drop=True)

    df_CardsCopy = df_Cards.copy()

    if( "Magic the Gathering Einzelkarten" == df_CardsCopy.columns[0]):
        currentLanguage =  Language.deutsch

    df_CardsCopy = mainSortFunction(df_CardsCopy, df_Expansion)

    showErrorsAndHints()
     
    showResult(df_CardsCopy)
    
    boxList = getCardsSortedToBoxes(df_CardsCopy)

    boxList = showBoxesResults(boxList)
    
    showCardsWithHint(df_CardsCopy,df_Expansion)

    bestellungenList = getCardsSortedToBestellungen(df_CardsCopy)

    showBestellungenResults(bestellungenList)
    
    bestellungenList = getCardsSortedToBestellungen(df_CardsCopy, False)

    createPDFs(bestellungenList)

    boxList = showBoxesGefunden(boxList)
    showCardsWithHintFound(df_CardsCopy,df_Expansion)
#streamlit run Magic_Card_Finder.py
#cd C:\Users\ismae\Desktop\Magic 
#   