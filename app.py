import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# --- KONFIGURACJA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    api_key = "AIzaSyBET8qlamTQ1H2OZ6wijb9_8VaFzKbzONE"

genai.configure(api_key=api_key)

def classify_item(input_data):
    """
    Funkcja teraz jest uniwersalna:
    input_data może być TEKSTEM (string) lub OBRAZEM (PIL.Image)
    """
    
    # Bazowa instrukcja dla modelu (system prompt)
    base_prompt = """
    Jesteś ekspertem projektu @sladwodny.

    KONKRETNIE na bazie wzoru Water Footprint Network (W Ftotal), wylicz jaki jest stopień racjonalności śladu wodnego dla danego przedmiotu,
    następnie w oparciu o dane poniżej, określ racjonalność tego zużycia w skali 1-4, biorąc pod uwagę że będzie użytkowany przez kilka lat.
    Smartfon: 2 - całkiem racjonalny bo używany przez 3/4 lata
    1kg wołowiny: 4 - nie racjonalny, można zjeść w kilka dni
    Patelnia żeliwna: 1 - bardzo racjonalny, przedmiot na lata a zużywa mało wody
    Choinka żywa: 3 - średnio racjonalny, ale nie szkodzi bardzo

    ZADANIE:
    1. Zidentyfikuj przedmiot (z tekstu lub ze zdjęcia).
    2. Oceń go według skali.
    
    Odpowiedz TYLKO w formacie podanym poniej, KATEGORYCZNIE nie podawaj jako odpowiedzi CZEGOKOLWIEK INNEGO::
    NUMER_OCENY|KOLOR|NAZWA PRZEDMIOTU: KRÓTKIE UZASADNIENIE
    Np:
    4|Pomarańczowy|Plastikowa butelka: To produkt jednorazowy o dużym śladzie wodnym.
    """
    
    model = genai.GenerativeModel('gemini-flash-latest')
    
    try:
        # Tworzymy listę treści do wysłania (Gemini przyjmuje listę [prompt, obraz])
        content = [base_prompt]
        
        if isinstance(input_data, str):
            # Jeśli użytkownik wpisał tekst
            content.append(f"Przedmiot do oceny: {input_data}")
        else:
            # Jeśli użytkownik wysłał zdjęcie (obiekt PIL Image)
            content.append("Oceń przedmiot widoczny na tym zdjęciu.")
            content.append(input_data) 

        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        return f"Błąd|Błąd|Wystąpił błąd połączenia: {e}"

# --- INTERFEJS STRONY ---

st.set_page_config(page_title="@sladwodny", page_icon="🤓")

st.title("💧 Kalkulator Śladu Wodnego")
st.markdown("Sprawdź racjonalność śladu wodnego wpisując nazwę lub **robiąc zdjęcie**!")
st.markdown("---")

# Zakładki: Wybór między tekstem a aparatem
tab1, tab2 = st.tabs(["📝 Wpisz nazwę", "📸 Zrób/Wgraj zdjęcie"])

user_input = None
process_request = False

# --- ZAKŁADKA 1: TEKST ---
with tab1:
    text_input = st.text_input("Co chcesz sprawdzić?", placeholder="np. jeansy")
    if st.button("Sprawdź tekst"):
        user_input = text_input
        process_request = True

# --- ZAKŁADKA 2: ZDJĘCIE ---
with tab2:
    # Opcja zrobienia zdjęcia kamerką
    camera_photo = st.camera_input("Zrób zdjęcie")
    # Opcja wgrania pliku z dysku (np. z galerii w telefonie)
    uploaded_file = st.file_uploader("Lub wybierz z galerii", type=["jpg", "png", "jpeg"])
    
    if camera_photo:
        user_input = Image.open(camera_photo)
        process_request = True
    elif uploaded_file:
        user_input = Image.open(uploaded_file)
        process_request = True

# --- PRZETWARZANIE ---
if process_request and user_input:
    with st.spinner('Analizuje przedmiot...'):
        result = classify_item(user_input)
        
        try:
            # Rozdzielamy odpowiedź
            parts = result.split('|')
            if len(parts) >= 3:
                score_num = parts[0].strip()
                color_name = parts[1].strip()
                reason = parts[2].strip()
                
                image_map = {
                    "1": "bardzodobrze.png",
                    "2": "dobrze.png",
                    "3": "sredno.png",
                    "4": "zle.png"
                }
                
                image_file = image_map.get(score_num)

                st.markdown("---")
                # Wyświetlamy grafikę wyniku
                col_res1, col_res2, col_res3 = st.columns([1, 2, 1])
                with col_res2:
                    if image_file and os.path.exists(image_file):
                        st.image(image_file, width=300)
                    else:
                        st.error(f"Ocena: {score_num}/4 (ERR067 - no file)")

                st.info(f"**Wynik:** {reason}")
            else:
                st.error("Przepraszam, nie rozpoznałem zdjęcia lub tekstu. Spróbuj wykonać je ponownie.")
                
        except Exception as e:
            st.error(f"Błąd przetwarzania: {e}")

st.markdown("---")
st.caption("Projekt studencki @sladwodny")