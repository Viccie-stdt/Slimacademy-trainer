"""
SlimAcademy AI Trainer - Streamlit Web Applicatie
Een interactieve studie-trainer die vragen stelt over oorzaak-gevolg relaties.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

# Laad environment variabelen
load_dotenv()

# System Prompt voor de interactieve studietrainer
SYSTEM_PROMPT = """Je bent een interactieve medische studietrainer. Je rol is om studenten te helpen door vragen te stellen over oorzaak-gevolg relaties (→) in de brontekst die ze hebben geplakt.

BELANGRIJKE INSTRUCTIES:

1. STRUCTUUR ANALYSE (CRITIEK BELANGRIJK):
   - Scan de brontekst actief op structuurelementen: hoofdstuktitels, kopjes, paragrafen, secties
   - Identificeer de hiërarchie: Hoofdstuk X → Kopje Y → Paragraaf Z
   - Noteer mentaal waar elke belangrijke informatie staat in de structuur
   - Gebruik deze structuurinformatie ALTIJD bij feedback en vragen

2. INTERNE ANALYSE (niet zichtbaar voor student):
   - Analyseer de brontekst intern op oorzaak-gevolg relaties (→) en correlaties (↔)
   - Identificeer de belangrijkste logische verbanden
   - GEEN samenvatting geven - start direct met vragen stellen
   - De brontekst staat in het eerste bericht van de conversatie - gebruik deze altijd als referentie

3. QUIZ MODUS:
   - Stel telkens ÉÉN duidelijke vraag over een oorzaak-gevolg relatie uit de brontekst
   - Focus op het testen of de student de logische verbanden (pijlen) begrijpt
   - Begin met een basisvraag en ga geleidelijk dieper
   - Je MAG refereren naar de structuur om de student te sturen:
     * Bijvoorbeeld: "Laten we kijken naar de sectie over 'Downregulatie'. Wat is daar het gevolg van...?"
     * Bijvoorbeeld: "In het hoofdstuk over 'Endocrinologie' wordt gesproken over..."

4. FEEDBACK LOOP MET BRONVERMELDING (VERPLICHT):
   - Als antwoord FOUT is:
     * VERMELD ALTIJD de structuurlocatie: "In [Hoofdstuk X] / [Kopje Y] / [sectie Z] staat namelijk..."
     * Citeer het EXACTE stukje uit de brontekst waar het antwoord staat (gebruik aanhalingstekens)
     * Leg de logische stap (→) duidelijk uit
     * Stel een vergelijkbare vraag om te testen of het nu begrepen wordt
     * Voorbeeld: "Niet helemaal. In Hoofdstuk 2, onder het kopje 'Endocrinologie', staat namelijk: '[exact citaat]' → Dit betekent dat..."
   
   - Als antwoord GOED is:
     * Bevestig kort en positief (bijv. "✓ Correct!" of "✓ Goed gedaan!")
     * VERMELD de structuurlocatie waar deze informatie staat: "Dit staat inderdaad in [Hoofdstuk X] / [Kopje Y]..."
     * Stel direct een verdiepende vervolgvraag over een gerelateerd onderwerp
     * Ga dieper in op de logische verbanden
     * Voorbeeld: "✓ Correct! Dit staat in de sectie over 'Downregulatie'. Nu, wat zou er gebeuren als..."

5. GESCHIEDENIS:
   - Houd rekening met eerdere vragen en antwoorden in het gesprek
   - Herhaal geen vragen die al gesteld zijn
   - Bouw voort op wat de student al heeft geleerd
   - Verwijs terug naar de brontekst in het eerste bericht voor exacte citaten

6. COMMUNICATIE STIJL:
   - Bemoedigend maar strikt inhoudelijk - focus op accuraatheid
   - Vriendelijk en ondersteunend, maar houd de student verantwoordelijk voor correcte antwoorden
   - Geef duidelijke, concrete vragen
   - Gebruik de notatie → om oorzaak-gevolg relaties aan te geven
   - ALTIJD structuurlocatie vermelden bij feedback (zowel goed als fout)

FORMAT:
- Stel vragen in een natuurlijke, gespreksmatige stijl
- Gebruik → om oorzaak-gevolg relaties te visualiseren
- Bij foute antwoorden: "❌ In [structuurlocatie] staat: '[exact citaat]' → [uitleg logische stap]"
- Bij goede antwoorden: "✓ Correct! Dit staat in [structuurlocatie]. [verdiepende vraag]"
- Bij vragen: Je mag refereren naar structuur: "Laten we kijken naar [sectie/kopje]..." """


def initialize_session_state():
    """Initialiseer session state variabelen."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "context_set" not in st.session_state:
        st.session_state.context_set = False
    if "source_text" not in st.session_state:
        st.session_state.source_text = ""


def get_openai_client():
    """Haal OpenAI client op of toon error."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY niet gevonden in .env bestand. Voeg deze toe om de applicatie te gebruiken.")
        st.stop()
    return OpenAI(api_key=api_key)


def get_ai_response(client: OpenAI, messages: list) -> str:
    """Haal antwoord op van OpenAI."""
    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Fout bij het ophalen van antwoord: {str(e)}"


def extract_text_from_pdf(pdf_file) -> tuple:
    """
    Extraheer tekst uit een PDF bestand.
    
    Args:
        pdf_file: Het geüploade PDF bestand object
    
    Returns:
        Tuple van (extracted_text, num_pages)
    """
    try:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Extraheer tekst van alle pagina's
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        
        extracted_text = "\n".join(text_parts)
        return extracted_text, num_pages
    except Exception as e:
        st.error(f"❌ Fout bij het lezen van PDF: {str(e)}")
        return "", 0


def start_training(source_text: str, client: OpenAI, num_pages: int = 0):
    """Start de training sessie met de brontekst."""
    if not source_text.strip():
        st.warning("⚠️ Upload eerst een PDF bestand voordat je de training start.")
        return
    
    # Toon success melding als PDF is verwerkt
    if num_pages > 0:
        st.success(f"✅ PDF succesvol verwerkt! ({num_pages} pagina's)")
    
    # Voeg brontekst toe aan geschiedenis
    st.session_state.source_text = source_text
    
    # Bouw initial messages op
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"BRONTEKST:\n{source_text}\n\nStart nu met het stellen van vragen over de oorzaak-gevolg relaties in deze tekst. Geef GEEN samenvatting, stel direct een vraag."
        }
    ]
    
    # Haal eerste vraag op
    with st.spinner("🤔 Trainer bereidt eerste vraag voor..."):
        first_question = get_ai_response(client, messages)
    
    # Voeg eerste vraag toe aan geschiedenis (zonder systeem prompt)
    st.session_state.history.append({"role": "assistant", "content": first_question})
    st.session_state.context_set = True
    
    # Rerun om chat interface te tonen
    st.rerun()


def handle_user_answer(user_answer: str, client: OpenAI):
    """Verwerk het antwoord van de gebruiker en haal feedback op."""
    if not user_answer.strip():
        return
    
    # Voeg antwoord toe aan geschiedenis
    st.session_state.history.append({"role": "user", "content": user_answer})
    
    # Bouw messages op voor OpenAI
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"BRONTEKST:\n{st.session_state.source_text}\n\nStart met het stellen van vragen."
        }
    ]
    
    # Voeg conversatiegeschiedenis toe (zonder systeem prompt)
    for msg in st.session_state.history:
        messages.append(msg)
    
    # Haal feedback op
    with st.spinner("📝 Trainer analyseert je antwoord..."):
        feedback = get_ai_response(client, messages)
    
    # Voeg feedback toe aan geschiedenis
    st.session_state.history.append({"role": "assistant", "content": feedback})


def reset_session():
    """Reset de sessie."""
    st.session_state.history = []
    st.session_state.context_set = False
    st.session_state.source_text = ""
    st.rerun()


def main():
    """Hoofdfunctie voor de Streamlit app."""
    # Pagina configuratie
    st.set_page_config(
        page_title="SlimAcademy AI Trainer",
        page_icon="🎓",
        layout="wide"
    )
    
    # Initialiseer session state
    initialize_session_state()
    
    # Sidebar met reset knop
    with st.sidebar:
        st.title("⚙️ Instellingen")
        if st.button("🔄 Reset", use_container_width=True):
            reset_session()
        st.markdown("---")
        st.markdown("### 📖 Instructies")
        st.markdown("""
        1. Upload je PDF bestand
        2. Klik op "Start Training"
        3. Beantwoord de vragen van de trainer
        4. Krijg direct feedback met bronvermelding
        """)
    
    # Hoofdinterface
    st.title("🎓 SlimAcademy AI Trainer")
    st.markdown("Een interactieve studie-trainer die vragen stelt over oorzaak-gevolg relaties in je studieteksten.")
    st.markdown("---")
    
    # Haal OpenAI client op
    client = get_openai_client()
    
    # Stap 1: Input interface (als context nog niet is ingesteld)
    if not st.session_state.context_set:
        st.subheader("📚 Stap 1: Upload je samenvatting")
        
        uploaded_file = st.file_uploader(
            "Upload je samenvatting (PDF)",
            type="pdf",
            help="Upload een PDF bestand met je studietekst. De trainer zal vragen stellen over de oorzaak-gevolg relaties."
        )
        
        source_text = ""
        num_pages = 0
        
        # Verwerk PDF als bestand is geüpload
        if uploaded_file is not None:
            source_text, num_pages = extract_text_from_pdf(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Training", use_container_width=True, type="primary"):
                start_training(source_text, client, num_pages)
    
    # Stap 2: Chat interface (als context is ingesteld)
    else:
        st.subheader("💬 Training Sessie")
        
        # Toon chat geschiedenis
        for message in st.session_state.history:
            if message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
            elif message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
        
        # Chat input voor nieuwe antwoorden
        if user_answer := st.chat_input("Type je antwoord hier..."):
            handle_user_answer(user_answer, client)
            st.rerun()


if __name__ == "__main__":
    main()
