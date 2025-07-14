import re
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Paso 1: Autenticación
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("./src/nifty-might-269005-cd303aaaa33f.json", scope)
client = gspread.authorize(creds)


# Paso 4: Abrir el Sheet por ID
spreadsheet = client.open_by_key("1PWz0McxGvGGD5LzVFXsJTaNIAEYjfWohqtimNVCvTGQ")
sheet = spreadsheet.worksheet("KF")
data = sheet.get_all_values()
df = pd.DataFrame(data)
df.columns = df.iloc[0]   # pone la primera fila como nombres de columna
df = df.drop(index=0).reset_index(drop=True) 
print(df)




