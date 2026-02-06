"""
White Label Studie-Applicatie
Een intelligente AI-trainer voor 6 verschillende studierichtingen met 3 studiemodi.
Volledig in het Nederlands met boek-integratie en flexibele generatie (met of zonder upload).

VERSIE 3.0 - BACHELOR SUITE (Jaar 1, 2 & 3) + Alle Bug Fixes
"""

import streamlit as st
import os
import base64
import json
import re
import random
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

# Laad environment variabelen
load_dotenv()


# ============================================================================
# 📚 STUDY FIELDS CONFIGURATIE - BACHELOR SUITE (3 JAREN)
# ============================================================================

STUDY_FIELDS = {
    "Geneeskunde 🩺": {
        "color": "#800020",
        "role_instruction": """Je bent een medische studietrainer. Je helpt studenten door vragen te stellen over oorzaak-gevolg relaties (→) in medische teksten en afbeeldingen.

FOCUS:
- Identificeer oorzaak-gevolg ketens (A → B → C)
- Test begrip van diagnoses en pathofysiologie
- Gebruik medische terminologie correct
- Vraag naar mechanismen, niet alleen feiten

STIJL:
- Bemoedigend maar strikt inhoudelijk
- Gebruik de notatie → voor oorzaak-gevolg
- Begin feedback met ✅ (correct) of ❌ (fout)""",
        "tech_instruction": "Gebruik duidelijke medische terminologie en de → notatie voor oorzaak-gevolg relaties.",
        "years": {
            "Jaar 1: De Basis": {
                "sub_subjects": ["Anatomie", "Fysiologie", "Pathologie", "Farmacologie"],
                "books": {
                    "Anatomie": [
                        "Sobotta Atlas",
                        "Gray's Anatomy",
                        "Prometheus Anatomie Atlas",
                        "Netter's Atlas of Human Anatomy",
                        "Moore's Clinically Oriented Anatomy"
                    ],
                    "Fysiologie": [
                        "Guyton & Hall Textbook of Medical Physiology",
                        "Boron & Boulpaep Medical Physiology",
                        "Vander's Human Physiology",
                        "Silverthorn Human Physiology"
                    ],
                    "Pathologie": [
                        "Robbins Basic Pathology",
                        "Kumar & Clark's Clinical Medicine",
                        "Pathologic Basis of Disease"
                    ],
                    "Farmacologie": [
                        "Goodman & Gilman's Pharmacology",
                        "Katzung Basic & Clinical Pharmacology",
                        "Rang & Dale's Pharmacology"
                    ]
                }
            },
            "Jaar 2: Verdieping & Ziektebeelden": {
                "sub_subjects": ["Neurologie", "Immunologie", "Epidemiologie", "Psychiatrie"],
                "books": {
                    "Neurologie": [
                        "Bear - Neuroscience: Exploring the Brain",
                        "Blumenfeld - Neuroanatomy through Clinical Cases",
                        "Fitzgerald - Clinical Neuroanatomy",
                        "Kandel - Principles of Neural Science"
                    ],
                    "Immunologie": [
                        "Abbas - Cellular and Molecular Immunology",
                        "Murphy - Janeway's Immunobiology",
                        "Parham - The Immune System"
                    ],
                    "Epidemiologie": [
                        "Rothman - Modern Epidemiology",
                        "Gordis - Epidemiology",
                        "Szklo - Epidemiology: Beyond the Basics"
                    ],
                    "Psychiatrie": [
                        "Kaplan & Sadock's Synopsis of Psychiatry",
                        "DSM-5 Handbook of Differential Diagnosis",
                        "Stahl's Essential Psychopharmacology"
                    ]
                }
            },
            "Jaar 3: Klinische Praktijk": {
                "sub_subjects": ["Interne Geneeskunde", "Chirurgie", "Kindergeneeskunde", "Gynaecologie"],
                "books": {
                    "Interne Geneeskunde": [
                        "Kumar & Clark's Clinical Medicine",
                        "Harrison's Principles of Internal Medicine",
                        "Oxford Handbook of Clinical Medicine",
                        "Cecil Textbook of Medicine"
                    ],
                    "Chirurgie": [
                        "Cameron - Current Surgical Therapy",
                        "Sabiston Textbook of Surgery",
                        "Schwartz's Principles of Surgery",
                        "Oxford Handbook of Clinical Surgery"
                    ],
                    "Kindergeneeskunde": [
                        "Nelson Textbook of Pediatrics",
                        "Rudolph's Pediatrics",
                        "Oxford Handbook of Paediatrics"
                    ],
                    "Gynaecologie": [
                        "Williams Obstetrics",
                        "Berek & Novak's Gynecology",
                        "Oxford Handbook of Obstetrics and Gynaecology"
                    ]
                }
            }
        }
    },
    
    "Rechten ⚖️": {
        "color": "#1B365D",
        "role_instruction": """Je bent een juridische studietrainer gespecialiseerd in Nederlands recht. Je helpt studenten door vragen te stellen over wetsartikelen, jurisprudentie en juridische argumentatie.

FOCUS:
- Citeer EXACTE wetsartikelen met nummers (bijv. art. 6:217 BW)
- Test juridische redeneringen en argumentaties
- Vraag naar voorwaarden, uitzonderingen en rechtsgevolgen
- Gebruik praktijkcasussen

STIJL:
- Formeel en precies
- Professioneel juridisch taalgebruik
- Begin feedback met ✅ (correct) of ❌ (fout)
- Verwijs altijd naar specifieke wetsartikelen""",
        "tech_instruction": "Citeer wetsartikelen EXACT met artikelnummers (bijv. art. 6:74 BW). Gebruik formeel juridisch taalgebruik.",
        "years": {
            "Jaar 1: Grondslagen": {
                "sub_subjects": ["Burgerlijk Recht", "Strafrecht", "Bestuursrecht"],
                "books": {
                    "Burgerlijk Recht": [
                        "Asser Serie - Verbintenissenrecht",
                        "Pitlo - Het Nederlands Burgerlijk Recht",
                        "Studieboek Burgerlijk Recht (Kluwer)",
                        "Burgerlijk Wetboek (Tekst & Commentaar)"
                    ],
                    "Strafrecht": [
                        "Kelk - Studieboek Materieel Strafrecht",
                        "Corstens - Het Nederlands Strafprocesrecht",
                        "Wetboek van Strafrecht (Tekst & Commentaar)",
                        "Strafrecht (Wolters Kluwer)"
                    ],
                    "Bestuursrecht": [
                        "Damen - Bestuursrecht (Boom)",
                        "Algemene Wet Bestuursrecht (Tekst & Commentaar)",
                        "Nicolaï - Beginselen van het Bestuursrecht",
                        "Bestuursrecht in de Sociale Rechtsstaat"
                    ]
                }
            },
            "Jaar 2: Specialisaties": {
                "sub_subjects": ["Goederenrecht", "Belastingrecht", "Europees Recht"],
                "books": {
                    "Goederenrecht": [
                        "Asser - Goederenrecht",
                        "Pitlo - Goederenrecht",
                        "Studieboek Goederenrecht"
                    ],
                    "Belastingrecht": [
                        "Cursus Belastingrecht (Kluwer)",
                        "Inleiding tot het Nederlandse Belastingrecht",
                        "Vakstudie Belastingrecht"
                    ],
                    "Europees Recht": [
                        "Craig & De Búrca - EU Law",
                        "Kapteyn & VerLoren van Themaat",
                        "Steiner & Woods - EU Law"
                    ]
                }
            },
            "Jaar 3: Praktijk & Ethiek": {
                "sub_subjects": ["Arbeidsrecht", "Rechtsfilosofie", "Internationaal Publiekrecht"],
                "books": {
                    "Arbeidsrecht": [
                        "Loonstra & Zondag - Arbeidsrechtelijke Themata",
                        "Jacobs - Het Burgerlijk Wetboek voor de Praktijk",
                        "Fase - Sociaal Recht"
                    ],
                    "Rechtsfilosofie": [
                        "Dworkin - Law's Empire",
                        "Hart - The Concept of Law",
                        "Cliteur - Inleiding in het Recht"
                    ],
                    "Internationaal Publiekrecht": [
                        "Shaw - International Law",
                        "Brownlie's Principles of Public International Law",
                        "Cassese - International Law"
                    ]
                }
            }
        }
    },
    
    "Computer Science 💻": {
        "color": "#2F4F4F",
        "role_instruction": """Je bent een programmeer-coach. Je helpt studenten door vragen te stellen over code, algoritmes en software development concepten.

FOCUS:
- Test begrip van algoritmes en datastructuren
- Vraag naar time/space complexity
- Test debugging vaardigheden
- Vraag naar best practices en design patterns

STIJL:
- Praktisch en hands-on
- Gebruik concrete voorbeelden
- Begin feedback met ✅ (correct) of ❌ (fout)
- Moedig experimenteren aan""",
        "tech_instruction": """CRUCIAAL: Alle code MOET in Markdown Code Blocks staan voor correcte syntax highlighting.

Format: ```python
# code hier
```

Gebruik ALTIJD deze syntax voor code snippets.""",
        "years": {
            "Jaar 1: Fundamentals": {
                "sub_subjects": ["Python", "Algorithms", "Web Development", "Security"],
                "books": {
                    "Python": [
                        "Python Crash Course (Eric Matthes)",
                        "Fluent Python (Luciano Ramalho)",
                        "Effective Python (Brett Slatkin)",
                        "Python for Data Analysis (Wes McKinney)",
                        "Automate the Boring Stuff with Python"
                    ],
                    "Algorithms": [
                        "Introduction to Algorithms (CLRS)",
                        "Algorithm Design (Kleinberg & Tardos)",
                        "The Algorithm Design Manual (Skiena)",
                        "Grokking Algorithms (Aditya Bhargava)"
                    ],
                    "Web Development": [
                        "Eloquent JavaScript (Marijn Haverbeke)",
                        "You Don't Know JS (Kyle Simpson)",
                        "Full Stack Development with React & Node.js",
                        "Web Development with Django"
                    ],
                    "Security": [
                        "The Web Application Hacker's Handbook",
                        "Hacking: The Art of Exploitation",
                        "Cryptography Engineering",
                        "Network Security Essentials (Stallings)"
                    ]
                }
            },
            "Jaar 2: Systems & Architecture": {
                "sub_subjects": ["Operating Systems", "Computer Networks", "Software Engineering"],
                "books": {
                    "Operating Systems": [
                        "Tanenbaum - Modern Operating Systems",
                        "Silberschatz - Operating System Concepts",
                        "Arpaci-Dusseau - Operating Systems: Three Easy Pieces"
                    ],
                    "Computer Networks": [
                        "Kurose & Ross - Computer Networking",
                        "Tanenbaum - Computer Networks",
                        "Peterson & Davie - Computer Networks: A Systems Approach"
                    ],
                    "Software Engineering": [
                        "Sommerville - Software Engineering",
                        "Pressman - Software Engineering: A Practitioner's Approach",
                        "Clean Code (Robert C. Martin)",
                        "Design Patterns (Gang of Four)"
                    ]
                }
            },
            "Jaar 3: Advanced Topics": {
                "sub_subjects": ["Artificial Intelligence", "Distributed Systems", "Compilers"],
                "books": {
                    "Artificial Intelligence": [
                        "Russell & Norvig - Artificial Intelligence: A Modern Approach",
                        "Bishop - Pattern Recognition and Machine Learning",
                        "Goodfellow - Deep Learning"
                    ],
                    "Distributed Systems": [
                        "Tanenbaum & Van Steen - Distributed Systems",
                        "Coulouris - Distributed Systems: Concepts and Design",
                        "Kleppmann - Designing Data-Intensive Applications"
                    ],
                    "Compilers": [
                        "Aho - Compilers: Principles, Techniques, and Tools (Dragon Book)",
                        "Cooper & Torczon - Engineering a Compiler",
                        "Appel - Modern Compiler Implementation"
                    ]
                }
            }
        }
    },
    
    "Engineering & Wiskunde ⚙️": {
        "color": "#A0522D",
        "role_instruction": """Je bent een wiskunde en engineering coach. Je helpt studenten door vragen te stellen over wiskundige concepten, formules en technische berekeningen.

FOCUS:
- Test begrip van wiskundige concepten
- Vraag naar afleidingen en bewijzen
- Test probleemoplossend vermogen
- Vraag naar praktische toepassingen

STIJL:
- Logisch en stapsgewijs
- Gebruik concrete voorbeelden
- Begin feedback met ✅ (correct) of ❌ (fout)
- Moedig wiskundig redeneren aan""",
        "tech_instruction": """CRUCIAAL: Alle formules MOETEN in LaTeX formaat staan voor correcte rendering in Streamlit.

Inline formules: $f(x) = x^2$
Display formules: $$\\int_{0}^{\\infty} e^{-x} dx = 1$$

Gebruik ALTIJD LaTeX voor wiskundige notatie.""",
        "years": {
            "Jaar 1: Basis Wiskunde": {
                "sub_subjects": ["Calculus", "Statica", "Dynamica", "Lineaire Algebra"],
                "books": {
                    "Calculus": [
                        "Stewart Calculus",
                        "Thomas' Calculus",
                        "Calculus (Spivak)",
                        "Calculus: Early Transcendentals"
                    ],
                    "Statica": [
                        "Engineering Mechanics: Statics (Hibbeler)",
                        "Vector Mechanics for Engineers: Statics",
                        "Statics and Mechanics of Materials"
                    ],
                    "Dynamica": [
                        "Engineering Mechanics: Dynamics (Hibbeler)",
                        "Vector Mechanics for Engineers: Dynamics",
                        "Classical Dynamics (Thornton & Marion)"
                    ],
                    "Lineaire Algebra": [
                        "Linear Algebra and Its Applications (Lay)",
                        "Introduction to Linear Algebra (Strang)",
                        "Linear Algebra Done Right (Axler)",
                        "Schaum's Outline of Linear Algebra"
                    ]
                }
            },
            "Jaar 2: Toegepaste Engineering": {
                "sub_subjects": ["Fluid Mechanics", "Materials Science", "Control Systems"],
                "books": {
                    "Fluid Mechanics": [
                        "Munson - Fundamentals of Fluid Mechanics",
                        "White - Fluid Mechanics",
                        "Fox - Introduction to Fluid Mechanics"
                    ],
                    "Materials Science": [
                        "Callister - Materials Science and Engineering",
                        "Ashby - Materials Selection in Mechanical Design",
                        "Shackelford - Introduction to Materials Science"
                    ],
                    "Control Systems": [
                        "Ogata - Modern Control Engineering",
                        "Nise - Control Systems Engineering",
                        "Franklin - Feedback Control of Dynamic Systems"
                    ]
                }
            },
            "Jaar 3: Advanced Engineering": {
                "sub_subjects": ["Finite Element Method", "Heat Transfer", "Mechatronics"],
                "books": {
                    "Finite Element Method": [
                        "Logan - A First Course in the Finite Element Method",
                        "Zienkiewicz - The Finite Element Method",
                        "Reddy - An Introduction to the Finite Element Method"
                    ],
                    "Heat Transfer": [
                        "Incropera - Fundamentals of Heat and Mass Transfer",
                        "Cengel - Heat and Mass Transfer",
                        "Bergman - Introduction to Heat Transfer"
                    ],
                    "Mechatronics": [
                        "Bolton - Mechatronics",
                        "Alciatore - Introduction to Mechatronics",
                        "De Silva - Mechatronics: An Integrated Approach"
                    ]
                }
            }
        }
    },
    
    "Psychologie 🧠": {
        "color": "#4B0082",
        "role_instruction": """Je bent een psychologie studiecoach. Je helpt studenten door vragen te stellen over psychologische theorieën, experimenten en concepten.

FOCUS:
- Test begrip van psychologische theorieën
- Vraag naar klassieke experimenten en hun bevindingen
- Test toepassing van theorieën op praktijksituaties
- Vraag naar verbanden tussen verschillende concepten

STIJL:
- Empathisch maar wetenschappelijk
- Gebruik concrete voorbeelden
- Begin feedback met ✅ (correct) of ❌ (fout)
- Moedig kritisch denken aan""",
        "tech_instruction": "Verwijs naar specifieke psychologen, theorieën en experimenten. Gebruik wetenschappelijke terminologie.",
        "years": {
            "Jaar 1: Grondslagen": {
                "sub_subjects": ["Cognitieve Psychologie", "Klinische Psychologie", "Ontwikkelingspsychologie", "Sociale Psychologie"],
                "books": {
                    "Cognitieve Psychologie": [
                        "Cognitive Psychology (Goldstein)",
                        "Cognition (Ashcraft & Radvansky)",
                        "Thinking, Fast and Slow (Kahneman)",
                        "The Mind's Machine (Watson & Breedlove)"
                    ],
                    "Klinische Psychologie": [
                        "Abnormal Psychology (Kring et al.)",
                        "Clinical Psychology (Trull & Prinstein)",
                        "DSM-5 Handbook",
                        "Psychopathology (Oltmanns & Emery)"
                    ],
                    "Ontwikkelingspsychologie": [
                        "Developmental Psychology (Santrock)",
                        "Child Development (Berk)",
                        "Lifespan Development (Boyd & Bee)",
                        "The Developing Person Through the Life Span"
                    ],
                    "Sociale Psychologie": [
                        "Social Psychology (Myers & Twenge)",
                        "Social Psychology (Aronson et al.)",
                        "Influence: The Psychology of Persuasion",
                        "The Social Animal (Aronson)"
                    ]
                }
            },
            "Jaar 2: Methodologie & Diagnostiek": {
                "sub_subjects": ["Psychometrie", "Persoonlijkheidsleer", "Neuropsychologie"],
                "books": {
                    "Psychometrie": [
                        "Psychological Testing and Assessment (Cohen)",
                        "Psychometric Theory (Nunnally & Bernstein)",
                        "Measurement and Assessment in Education"
                    ],
                    "Persoonlijkheidsleer": [
                        "Personality Psychology (Larsen & Buss)",
                        "Theories of Personality (Schultz & Schultz)",
                        "The Big Five Personality Traits"
                    ],
                    "Neuropsychologie": [
                        "Kolb - Fundamentals of Human Neuropsychology",
                        "Lezak - Neuropsychological Assessment",
                        "Banich - Cognitive Neuroscience"
                    ]
                }
            },
            "Jaar 3: Praktijk & Interventie": {
                "sub_subjects": ["Klinische Gespreksvoering", "Psychotherapie", "Ethiek & Beroepspraktijk"],
                "books": {
                    "Klinische Gespreksvoering": [
                        "Ivey - Intentional Interviewing and Counseling",
                        "Hill - Helping Skills: Facilitating Exploration",
                        "Sommers-Flanagan - Clinical Interviewing"
                    ],
                    "Psychotherapie": [
                        "Beck - Cognitive Behavior Therapy",
                        "Yalom - The Theory and Practice of Group Psychotherapy",
                        "Linehan - Cognitive-Behavioral Treatment of BPD"
                    ],
                    "Ethiek & Beroepspraktijk": [
                        "APA Ethics Code Commentary",
                        "Pope - Ethics in Psychotherapy and Counseling",
                        "Koocher - Ethics in Psychology"
                    ]
                }
            }
        }
    },
    
    "Economie 📈": {
        "color": "#004B49",
        "role_instruction": """Je bent een economie studiecoach. Je helpt studenten door vragen te stellen over economische modellen, theorieën en marktmechanismen.

FOCUS:
- Test begrip van economische modellen
- Vraag naar vraag/aanbod mechanismen
- Test begrip van macro-economische indicatoren
- Vraag naar praktische toepassingen

STIJL:
- Analytisch en data-gedreven
- Gebruik concrete voorbeelden
- Begin feedback met ✅ (correct) of ❌ (fout)
- Moedig economisch redeneren aan""",
        "tech_instruction": "Gebruik LaTeX voor economische formules (bijv. $$MR = MC$$). Verwijs naar economische modellen en theorieën.",
        "years": {
            "Jaar 1: Fundamenten": {
                "sub_subjects": ["Macro-economie", "Micro-economie", "Finance", "Econometrie"],
                "books": {
                    "Macro-economie": [
                        "Macroeconomics (Mankiw)",
                        "Macroeconomics (Blanchard)",
                        "Modern Principles of Economics",
                        "International Economics (Krugman)"
                    ],
                    "Micro-economie": [
                        "Microeconomics (Pindyck & Rubinfeld)",
                        "Intermediate Microeconomics (Varian)",
                        "Microeconomic Theory (Mas-Colell)",
                        "Principles of Microeconomics (Mankiw)"
                    ],
                    "Finance": [
                        "Corporate Finance (Ross, Westerfield, Jaffe)",
                        "Investments (Bodie, Kane, Marcus)",
                        "Principles of Corporate Finance (Brealey)",
                        "Options, Futures, and Other Derivatives (Hull)"
                    ],
                    "Econometrie": [
                        "Introductory Econometrics (Wooldridge)",
                        "Econometric Analysis (Greene)",
                        "Mostly Harmless Econometrics",
                        "Basic Econometrics (Gujarati)"
                    ]
                }
            },
            "Jaar 2: Verdieping": {
                "sub_subjects": ["Advanced Econometrics", "Speltheorie", "International Trade"],
                "books": {
                    "Advanced Econometrics": [
                        "Stock & Watson - Introduction to Econometrics",
                        "Cameron & Trivedi - Microeconometrics",
                        "Hayashi - Econometrics"
                    ],
                    "Speltheorie": [
                        "Osborne - An Introduction to Game Theory",
                        "Gibbons - Game Theory for Applied Economists",
                        "Dixit & Nalebuff - The Art of Strategy"
                    ],
                    "International Trade": [
                        "Krugman - International Economics",
                        "Feenstra - Advanced International Trade",
                        "Helpman - Understanding Global Trade"
                    ]
                }
            },
            "Jaar 3: Beleid & Praktijk": {
                "sub_subjects": ["Public Finance", "Monetary Policy", "Development Economics"],
                "books": {
                    "Public Finance": [
                        "Rosen - Public Finance",
                        "Gruber - Public Finance and Public Policy",
                        "Stiglitz - Economics of the Public Sector"
                    ],
                    "Monetary Policy": [
                        "Mishkin - The Economics of Money, Banking, and Financial Markets",
                        "Walsh - Monetary Theory and Policy",
                        "Woodford - Interest and Prices"
                    ],
                    "Development Economics": [
                        "Ray - Development Economics",
                        "Todaro & Smith - Economic Development",
                        "Banerjee & Duflo - Poor Economics"
                    ]
                }
            }
        }
    }
}


# ============================================================================
# 🎨 STYLING FUNCTIE
# ============================================================================

def apply_custom_styling(primary_color: str):
    """
    Pas dynamische 'Light Academia' styling toe.
    Thema: Antiek Perkament & Donker Leder.
    """
    custom_css = f"""
    <style>
        /* --- 1. HOOFDSCHERM (Oud Papier) --- */
        .stApp {{
            background-color: #E3D4BC; 
            color: #2A2420;
        }}
        
        /* --- 2. SIDEBAR --- */
        section[data-testid="stSidebar"] {{
            background-color: #D4C5AD !important;
            border-right: 1px solid #8B5A2B;
        }}
        
        section[data-testid="stSidebar"] * {{
            color: #2A2420 !important;
        }}
        
        /* --- 3. CHAT MESSAGES (BLEND IN) --- */
        .stChatMessage {{
            background-color: transparent !important;
            border: 1px solid rgba(139, 90, 43, 0.2); /* Subtiel leder randje */
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        .stChatMessage p, .stChatMessage div {{
            color: #2A2420 !important;
        }}
        
        /* --- 4. DE CHAT INPUT BALK (FIX VOOR ZWART BLOK) --- */
        /* De container van de input */
        .stChatInput {{
            background-color: transparent !important;
        }}
        
        /* Het invulveld zelf */
        .stChatInput textarea {{
            background-color: #FFF8F0 !important; /* Licht papier */
            color: #2A2420 !important; /* Donkere tekst */
            border: 2px solid {primary_color} !important; /* Rand in studiekleur */
            border-radius: 12px;
        }}
        
        /* De verstuur knop (Pijltje) */
        [data-testid="stChatInputSubmitButton"] {{
            color: {primary_color} !important;
            background-color: transparent !important;
        }}
        
        [data-testid="stChatInputSubmitButton"]:hover {{
            color: #2A2420 !important;
        }}
        
        /* --- 5. OVERIGE INPUTS --- */
        .stSelectbox > div > div, 
        .stTextInput > div > div, 
        .stSlider > div > div {{
            background-color: #FFF8F0 !important;
            color: #2A2420 !important;
            border: 1px solid #8B5A2B;
            border-radius: 6px;
        }}
        
        /* Selectbox Focus Border - DYNAMIC COLOR */
        .stSelectbox > div > div:focus-within {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 0 2px {primary_color}40 !important;
        }}
        
        /* Selectbox Hover */
        .stSelectbox > div > div:hover {{
            border-color: {primary_color}80 !important;
        }}
        
        /* Dropdown Text Readability */
        .stSelectbox [data-baseweb="select"] {{
            color: #2A2420 !important;
            font-weight: 500;
        }}
        
        /* Dropdowns */
        [role="listbox"] {{
            background-color: #FFF8F0 !important;
            border: 1px solid {primary_color} !important;
        }}
        
        [role="option"] {{
            background-color: #FFF8F0 !important;
            color: #2A2420 !important;
            padding: 0.75rem !important;
        }}
        
        [role="option"]:hover {{
            background-color: {primary_color}20 !important;
        }}
        
        /* Radio Buttons */
        .stRadio > div {{
            background-color: #FFF8F0;
            border-radius: 8px;
            padding: 0.5rem;
            border: 1px solid #8B5A2B;
        }}
        
        /* Radio Button Labels */
        .stRadio label {{
            color: #2A2420 !important;
        }}
        
        /* Slider */
        .stSlider > div > div > div > div {{
            background-color: {primary_color} !important;
        }}
        
        .stSlider [role="slider"] {{
            background-color: {primary_color} !important;
        }}
        
        /* --- FILE UPLOADER FIX (HET ZWARTE BLOK WEG) --- */
        /* Het drop-zone gebied */
        [data-testid="stFileUploader"] section {{
            background-color: #FFF8F0 !important; /* Licht papier */
            border: 2px dashed {primary_color} !important; /* Gekleurde stippellijn */
            border-radius: 12px;
            box-shadow: none;
            padding: 2rem;
        }}
        
        /* De tekst "Drag and drop..." en "Limit 200MB..." */
        [data-testid="stFileUploader"] section > div,
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section small {{
            color: #2A2420 !important; /* Donkere tekst */
        }}
        
        /* Het Icoontje (Wolkje) */
        [data-testid="stFileUploader"] svg {{
            fill: {primary_color} !important;
            stroke: {primary_color} !important;
        }}
        
        /* De "Browse files" knop */
        [data-testid="stFileUploader"] button {{
            background-color: transparent !important;
            color: {primary_color} !important;
            border: 1px solid {primary_color} !important;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stFileUploader"] button:hover {{
            background-color: {primary_color}20 !important;
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background-color: {primary_color} !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {primary_color} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }}
        
        /* --- 6. KNOPPEN & HEADERS --- */
        div.stButton > button {{
            background-color: {primary_color} !important;
            color: #FFF !important;
            border: none;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        div.stButton > button:hover {{
            background-color: {primary_color} !important;
            opacity: 0.85;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        button[kind="primary"] {{
            background-color: {primary_color} !important;
            color: #FFF !important;
        }}
        
        h1, h2, h3 {{
            color: {primary_color} !important;
            font-family: 'Georgia', serif !important;
        }}
        
        h1 {{
            font-weight: 800 !important;
        }}
        
        h2 {{
            font-weight: 700 !important;
        }}
        
        h3 {{
            font-weight: 600 !important;
        }}
        
        /* Flashcards */
        .flashcard {{
            background: #FFF8F0;
            border: 2px solid {primary_color};
            color: #2A2420;
            border-radius: 12px;
            padding: 3rem;
            margin: 1.5rem 0;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            cursor: pointer;
            transition: all 0.4s ease;
            font-family: 'Georgia', serif;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        
        .flashcard:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 24px rgba(0,0,0,0.2);
            border-color: {primary_color};
        }}
        
        /* Verberg branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================================
# 🔧 CALLBACK FUNCTIES
# ============================================================================

def reset_study_state():
    """Callback functie die wordt aangeroepen wanneer de Hoofdstudie verandert."""
    new_study = st.session_state.major_selector
    
    # Reset naar eerste jaar en eerste vak
    first_year = list(STUDY_FIELDS[new_study]["years"].keys())[0]
    st.session_state.selected_year = first_year
    st.session_state.selected_subject = STUDY_FIELDS[new_study]["years"][first_year]["sub_subjects"][0]
    st.session_state.selected_book = "Geen specifiek boek / Algemeen"
    
    # Reset alle session data
    st.session_state.history = []
    st.session_state.context_set = False
    st.session_state.source_text = ""
    st.session_state.image_base64 = None
    st.session_state.file_type = None
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.exam_questions = []
    st.session_state.exam_answers = {}
    st.session_state.exam_completed = False
    st.session_state.flashcards = []
    st.session_state.current_flashcard_index = 0
    st.session_state.show_flashcard_answer = False


def reset_year_state():
    """Callback functie die wordt aangeroepen wanneer het Jaar verandert."""
    new_year = st.session_state.year_selector
    current_study = st.session_state.selected_major
    
    # Reset naar eerste vak van het nieuwe jaar
    st.session_state.selected_subject = STUDY_FIELDS[current_study]["years"][new_year]["sub_subjects"][0]
    st.session_state.selected_book = "Geen specifiek boek / Algemeen"
    
    # Reset sessie data
    st.session_state.history = []
    st.session_state.context_set = False
    st.session_state.source_text = ""
    st.session_state.image_base64 = None
    st.session_state.file_type = None
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.exam_questions = []
    st.session_state.exam_answers = {}
    st.session_state.exam_completed = False
    st.session_state.flashcards = []
    st.session_state.current_flashcard_index = 0
    st.session_state.show_flashcard_answer = False


def reset_mode_state():
    """
    🔒 FIX 2: NAVIGATIE LOCK
    Callback functie die wordt aangeroepen wanneer de Studiemodus verandert.
    Wist alle modus-specifieke data zodat de gebruiker niet vast komt te zitten.
    
    BELANGRIJK: Als we programmatisch switchen (via knop), skip dan de reset.
    """
    # Check of we programmatisch switchen (via de "Oefenen met dit onderwerp" knop)
    if "skip_mode_reset" in st.session_state and st.session_state.skip_mode_reset:
        st.session_state.skip_mode_reset = False
        return
    
    # Normale reset bij handmatige modus-wissel
    st.session_state.context_set = False
    st.session_state.history = []
    st.session_state.exam_questions = []
    st.session_state.exam_answers = {}
    st.session_state.exam_completed = False
    st.session_state.flashcards = []
    st.session_state.current_flashcard_index = 0
    st.session_state.show_flashcard_answer = False
    st.session_state.score = 0
    st.session_state.total_questions = 0


def switch_to_practice_mode(vraag: str, user_answer: str, correct_answer: str, uitleg: str):
    """
    🔧 BUG FIX 1: CALLBACK FUNCTIE VOOR MODUS WISSEL
    Deze callback wordt aangeroepen VOOR de widget re-run, waardoor we veilig
    de mode_selector kunnen wijzigen zonder StreamlitAPIException.
    """
    # STAP 0: Zet flag om callback te skippen
    st.session_state.skip_mode_reset = True
    
    # STAP 1: Forceer de Sidebar Widget
    st.session_state["mode_selector"] = "🟢 Oefenen"
    st.session_state.study_mode = "🟢 Oefenen"
    
    # STAP 2: Sluit het Tentamen VOLLEDIG
    st.session_state.exam_completed = False
    st.session_state.exam_questions = []
    st.session_state.exam_answers = {}
    
    # STAP 3: Activeer de Chat
    st.session_state.context_set = True
    
    # STAP 4: Injecteer de Context
    st.session_state.history = []
    
    # Maak een user message met de fout beantwoorde vraag
    user_context_message = f"""Ik had de volgende tentamenvraag fout:

**Vraag:** {vraag}

**Mijn antwoord:** {user_answer}

**Correct antwoord:** {correct_answer}

**Uitleg:** {uitleg}

Kun je me dit onderwerp beter uitleggen en me hierover overhoren? Begin met een uitgebreide uitleg van het concept, en stel daarna een gerichte vraag om mijn begrip te testen."""
    
    st.session_state.history.append({
        "role": "user",
        "content": user_context_message
    })
    
    # Zet flag dat we AI moeten triggeren
    st.session_state.trigger_ai_response = True


# ============================================================================
# 🔧 HELPER FUNCTIES
# ============================================================================

def initialize_session_state():
    """Initialiseer alle session state variabelen."""
    if "selected_major" not in st.session_state:
        st.session_state.selected_major = "Geneeskunde 🩺"
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "Jaar 1: De Basis"
    if "selected_subject" not in st.session_state:
        first_year = list(STUDY_FIELDS["Geneeskunde 🩺"]["years"].keys())[0]
        st.session_state.selected_subject = STUDY_FIELDS["Geneeskunde 🩺"]["years"][first_year]["sub_subjects"][0]
    if "selected_book" not in st.session_state:
        st.session_state.selected_book = "Geen specifiek boek / Algemeen"
    if "study_mode" not in st.session_state:
        st.session_state.study_mode = "🟢 Oefenen"
    if "exam_num_questions" not in st.session_state:
        st.session_state.exam_num_questions = 5
    if "exam_question_type" not in st.session_state:
        st.session_state.exam_question_type = "Mix"
    if "skip_mode_reset" not in st.session_state:
        st.session_state.skip_mode_reset = False
    if "trigger_ai_response" not in st.session_state:
        st.session_state.trigger_ai_response = False
    if "history" not in st.session_state:
        st.session_state.history = []
    if "context_set" not in st.session_state:
        st.session_state.context_set = False
    if "source_text" not in st.session_state:
        st.session_state.source_text = ""
    if "image_base64" not in st.session_state:
        st.session_state.image_base64 = None
    if "file_type" not in st.session_state:
        st.session_state.file_type = None
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "exam_questions" not in st.session_state:
        st.session_state.exam_questions = []
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}
    if "exam_completed" not in st.session_state:
        st.session_state.exam_completed = False
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_flashcard_index" not in st.session_state:
        st.session_state.current_flashcard_index = 0
    if "show_flashcard_answer" not in st.session_state:
        st.session_state.show_flashcard_answer = False


def get_openai_client():
    """Haal OpenAI client op of toon error."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    
    if not api_key:
        st.error("❌ OPENAI_API_KEY niet gevonden. Voeg deze toe aan .env bestand of Streamlit secrets.")
        st.stop()
    
    return OpenAI(api_key=api_key)


def extract_text_from_pdf(pdf_file) -> tuple:
    """Extraheer tekst uit een PDF bestand."""
    try:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        
        extracted_text = "\n".join(text_parts)
        return extracted_text, num_pages
    except Exception as e:
        st.error(f"❌ Fout bij het lezen van PDF: {str(e)}")
        return "", 0


def encode_image(image_file) -> str:
    """Encode een afbeelding naar base64 string."""
    return base64.b64encode(image_file.read()).decode('utf-8')


def clean_and_parse_json(response_text: str):
    """Parse JSON response van AI."""
    try:
        text = response_text.strip()
        if "```" in text:
            text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
            text = text.strip()
        
        parsed = json.loads(text, strict=False)
        
        if isinstance(parsed, dict):
            for key in ["questions", "vragen", "items", "flashcards", "begrippen"]:
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]
        
        if isinstance(parsed, list):
            return parsed
        
        return [parsed]
    
    except Exception as e:
        st.error(f"❌ Fout bij JSON parsing: {str(e)}")
        return None


def construct_system_prompt(study: str, subject: str, book: str = None, mode: str = "practice", num_questions: int = 5, question_type: str = "Mix") -> str:
    """🧠 SLIMME System Prompt Generator met BOEK-INTEGRATIE en GENEESKUNDE SPECIALISATIE."""
    field_config = STUDY_FIELDS[study]
    
    base_instruction = f"""Je bent een gespecialiseerde AI-trainer voor {study}, maar je bent SPECIFIEK GESPECIALISEERD in {subject}.

🎯 CRUCIALE INSTRUCTIE:
Je bent niet alleen expert in {study}, je bent GESPECIALISEERD in {subject}. 
Al je vragen en voorbeelden MOETEN specifiek over {subject} gaan. 
Wijk hier NIET vanaf. Blijf binnen de grenzen van {subject}."""
    
    book_instruction = ""
    if book and book != "Geen specifiek boek / Algemeen":
        book_instruction = f"""

📚 BOEK-SPECIFIEKE INSTRUCTIE (ZEER BELANGRIJK):
Baseer je uitleg, structuur en terminologie SPECIFIEK op het boek: '{book}'.
- Gebruik de definities zoals '{book}' ze hanteert
- Volg de structuur en opbouw van '{book}'
- Verwijs naar concepten zoals ze in '{book}' worden uitgelegd
- Gebruik de terminologie en notatie van '{book}'
Dit boek is de LEIDENDE bron voor je uitleg en vragen."""
    
    if mode == "practice":
        system_prompt = f"""{base_instruction}{book_instruction}

{field_config['role_instruction']}

TECHNISCHE INSTRUCTIES:
{field_config['tech_instruction']}

WORKFLOW:
1. Analyseer de brontekst/afbeelding grondig (of gebruik je kennis van {subject} als er geen bron is)
2. Stel ÉÉN gerichte vraag SPECIFIEK over {subject}
3. Wacht op het antwoord van de student
4. Geef feedback:
   - Begin met ✅ (correct) of ❌ (fout)
   - Leg uit waarom het antwoord juist/onjuist is
   - Geef aanvullende context BINNEN {subject}
5. Stel een nieuwe, verdiepende vraag over {subject}

BELANGRIJK:
- Stel telkens maar ÉÉN vraag
- Houd de vragen STRIKT gericht op {subject}
- Bouw voort op eerdere antwoorden
- Pas je niveau aan op basis van de antwoorden
- Begin ALTIJD feedback met ✅ of ❌ voor score tracking
"""
    
    elif mode == "exam":
        # 🏥 FIX 3: GENEESKUNDE SPECIFIEK - Vraagtype instructie
        question_type_instruction = ""
        if study == "Geneeskunde 🩺":
            if question_type == "Klinisch (Casussen)":
                question_type_instruction = """

🏥 VRAAGTYPE: KLINISCH (CASUSSEN)
FOCUS op klinische casuïstiek:
- Presenteer patiëntcasussen met symptomen
- Vraag naar diagnoses, differentiaaldiagnoses
- Test klinisch redeneren en besluitvorming
- Gebruik realistische patiëntscenario's
- Vraag naar behandelingsopties en prognose

Voorbeeld structuur:
"Een 45-jarige man presenteert zich met [symptomen]. Wat is de meest waarschijnlijke diagnose?"
"""
            elif question_type == "Theoretisch (Feiten)":
                question_type_instruction = """

📚 VRAAGTYPE: THEORETISCH (FEITEN)
FOCUS op feitelijke kennis:
- Vraag naar definities en mechanismen
- Test kennis van anatomie, fysiologie, pathofysiologie
- Vraag naar oorzaak-gevolg relaties
- Test kennis van medicijnen en hun werkingsmechanismen
- Geen casussen, alleen directe kennisvragen

Voorbeeld structuur:
"Wat is het werkingsmechanisme van [medicijn]?"
"Welke structuur is verantwoordelijk voor [functie]?"
"""
            else:  # Mix
                question_type_instruction = """

🔀 VRAAGTYPE: MIX
Combineer klinische casussen met theoretische vragen.
- Ongeveer 50% casussen, 50% feitenvragen
- Varieer de vraagstelling voor een compleet beeld
"""
        
        # 🔧 BUG FIX 2: LaTeX escaping instructie voor JSON
        latex_escape_instruction = ""
        if study in ["Engineering & Wiskunde ⚙️", "Economie 📈"] or "Calculus" in subject or "Algebra" in subject:
            latex_escape_instruction = """

⚠️ CRUCIAAL VOOR JSON MET LaTeX:
Wanneer je LaTeX formules gebruikt in je vragen of uitleg, moet je ELKE backslash DUBBEL escapen voor correcte JSON parsing.

FOUT: "De afgeleide van $\\int x dx$ is..."
GOED: "De afgeleide van $\\\\int x dx$ is..."

FOUT: "Gebruik de formule $\\frac{a}{b}$"
GOED: "Gebruik de formule $\\\\frac{a}{b}$"

Voorbeelden van correcte escaping:
- \\int wordt \\\\int
- \\frac wordt \\\\frac
- \\sqrt wordt \\\\sqrt
- \\sum wordt \\\\sum
- \\lim wordt \\\\lim
- \\partial wordt \\\\partial

Als je dit niet doet, crasht de JSON parsing en zien studenten rode vakjes of \\x0 karakters!
"""
        
        system_prompt = f"""{base_instruction}{book_instruction}{question_type_instruction}{latex_escape_instruction}

{field_config['role_instruction']}

TECHNISCHE INSTRUCTIES:
{field_config['tech_instruction']}

OPDRACHT:
Genereer EXACT {num_questions} multiple choice vragen SPECIFIEK over {subject}.

OUTPUT FORMAT (STRICT JSON):
{{
  "questions": [
    {{
      "vraag": "De vraag hier (SPECIFIEK over {subject})...",
      "opties": ["A) Optie 1", "B) Optie 2", "C) Optie 3", "D) Optie 4"],
      "correct_antwoord": "B) Optie 2",
      "uitleg": "Uitleg waarom dit correct is..."
    }}
  ]
}}

EISEN:
- EXACT {num_questions} vragen
- ALLE vragen over {subject}
- Elke vraag heeft 4 opties (A, B, C, D)
- Geef het volledige correcte antwoord (inclusief letter)
- Geef een duidelijke uitleg
- Vragen moeten uitdagend maar eerlijk zijn
- Focus op begrip van {subject}, niet op triviale feiten
"""
    
    elif mode == "flashcards":
        system_prompt = f"""{base_instruction}{book_instruction}

{field_config['role_instruction']}

TECHNISCHE INSTRUCTIES:
{field_config['tech_instruction']}

OPDRACHT:
Genereer 10 flashcards met belangrijke begrippen/concepten SPECIFIEK uit {subject}.

OUTPUT FORMAT (STRICT JSON):
{{
  "flashcards": [
    {{
      "term": "Het begrip/concept (uit {subject})",
      "definitie": "De uitleg/definitie"
    }}
  ]
}}

EISEN:
- Selecteer de 10 belangrijkste begrippen uit {subject}
- Houd definities beknopt maar compleet (max 2-3 zinnen)
- Focus op kernconcepten van {subject} die studenten MOETEN kennen
- Gebruik duidelijke, toegankelijke taal
"""
    
    return system_prompt


def get_ai_response(client: OpenAI, messages: list, has_image: bool = False, json_mode: bool = False) -> str:
    """Haal AI response op van OpenAI."""
    try:
        model = "gpt-4o" if has_image else "gpt-4o"
        
        params = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ Fout bij AI aanroep: {str(e)}"


def reset_session():
    """Reset de sessie."""
    st.session_state.history = []
    st.session_state.context_set = False
    st.session_state.source_text = ""
    st.session_state.image_base64 = None
    st.session_state.file_type = None
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.exam_questions = []
    st.session_state.exam_answers = {}
    st.session_state.exam_completed = False
    st.session_state.flashcards = []
    st.session_state.current_flashcard_index = 0
    st.session_state.show_flashcard_answer = False


# ============================================================================
# 🟢 OEFENMODUS FUNCTIES
# ============================================================================

def start_practice_mode(client: OpenAI, study: str, subject: str, book: str, with_file: bool = True):
    """Start oefenmodus."""
    if with_file:
        if not st.session_state.source_text and not st.session_state.image_base64:
            st.warning("⚠️ Upload eerst een bestand voordat je de training start.")
            return
    
    system_prompt = construct_system_prompt(study, subject, book, "practice")
    messages = [{"role": "system", "content": system_prompt}]
    
    if with_file:
        if st.session_state.file_type == "image" and st.session_state.image_base64:
            image_url = f"data:image/jpeg;base64,{st.session_state.image_base64}"
            user_content = [
                {"type": "text", "text": f"Analyseer deze afbeelding voor {subject} en stel je eerste vraag."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
            messages.append({"role": "user", "content": user_content})
            has_image = True
        else:
            user_content = f"""STUDIEMATERIAAL voor {subject}:

{st.session_state.source_text}

Analyseer dit materiaal en stel je eerste vraag SPECIFIEK over {subject}."""
            messages.append({"role": "user", "content": user_content})
            has_image = False
    else:
        random_seed = random.randint(1000, 9999)
        
        if book and book != "Geen specifiek boek / Algemeen":
            user_content = f"""Je bent een expert in {subject} en specialist in het boek '{book}'.

OPDRACHT:
1. Kies een belangrijk kernconcept uit hoofdstuk 1 of 2 van '{book}'
2. Stel direct je eerste vraag over dit kernconcept
3. Geef GEEN introductie, start DIRECT met de vraag
4. Gebruik de terminologie en stijl van '{book}'

Random seed voor variatie: {random_seed}

Begin nu met je eerste vraag over {subject} (gebaseerd op '{book}')."""
        else:
            user_content = f"""Je bent een expert in {subject}.

OPDRACHT:
1. Kies een interessant onderwerp BINNEN {subject} (gebruik random seed: {random_seed})
2. Stel direct je eerste vraag over dit onderwerp
3. Geef GEEN introductie, start DIRECT met de vraag

Begin nu met je eerste vraag over {subject}."""
        
        messages.append({"role": "user", "content": user_content})
        has_image = False
        st.session_state.file_type = "no_file"
    
    with st.spinner("🤖 AI bereidt de eerste vraag voor..."):
        first_question = get_ai_response(client, messages, has_image)
    
    if first_question.startswith("❌"):
        st.error(first_question)
        return
    
    st.session_state.history.append({
        "role": "assistant",
        "content": first_question
    })
    st.session_state.context_set = True
    st.rerun()


def handle_practice_answer(client: OpenAI, user_answer: str, study: str, subject: str, book: str):
    """Verwerk antwoord in oefenmodus."""
    if not user_answer.strip():
        return
    
    st.session_state.history.append({
        "role": "user",
        "content": user_answer
    })
    
    system_prompt = construct_system_prompt(study, subject, book, "practice")
    messages = [{"role": "system", "content": system_prompt}]
    
    if st.session_state.file_type == "image" and st.session_state.image_base64:
        image_url = f"data:image/jpeg;base64,{st.session_state.image_base64}"
        initial_content = [
            {"type": "text", "text": f"Studiemateriaal voor {subject} (zie afbeelding)."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        messages.append({"role": "user", "content": initial_content})
        has_image = True
    elif st.session_state.file_type == "pdf" and st.session_state.source_text:
        initial_content = f"STUDIEMATERIAAL voor {subject}:\n\n{st.session_state.source_text}"
        messages.append({"role": "user", "content": initial_content})
        has_image = False
    elif st.session_state.file_type == "no_file":
        initial_content = f"Je bent expert in {subject}. Gebruik je kennis om vragen te stellen en feedback te geven."
        messages.append({"role": "user", "content": initial_content})
        has_image = False
    else:
        has_image = False
    
    for msg in st.session_state.history:
        messages.append(msg)
    
    with st.spinner("🤔 AI analyseert je antwoord..."):
        feedback = get_ai_response(client, messages, has_image)
    
    if feedback.strip().startswith("✅"):
        st.session_state.score += 1
        st.session_state.total_questions += 1
    elif feedback.strip().startswith("❌"):
        st.session_state.total_questions += 1
    
    st.session_state.history.append({
        "role": "assistant",
        "content": feedback
    })


# ============================================================================
# 📝 TENTAMENMODUS FUNCTIES - MET BATCHING LOGICA
# ============================================================================

def generate_exam_batch(client: OpenAI, study: str, subject: str, book: str, num_questions: int, source_text: str = None, question_type: str = "Mix"):
    """
    🔧 FIX 1: BATCHING LOGICA
    Genereer een ENKELE batch van max 5 vragen.
    Deze functie wordt meerdere keren aangeroepen door generate_exam_questions.
    """
    system_prompt = construct_system_prompt(study, subject, book, "exam", num_questions, question_type)
    messages = [{"role": "system", "content": system_prompt}]
    
    if source_text and source_text.strip():
        # MET BRONTEKST
        user_content = f"""STUDIEMATERIAAL voor {subject}:

{source_text}

INSTRUCTIE: Gebruik ENKEL de brontekst voor de vragen.
Genereer nu EXACT {num_questions} multiple choice vragen SPECIFIEK over {subject} in JSON format."""
    else:
        # ZONDER BRONTEKST
        book_context = f" en de stijl van '{book}'" if book and book != "Geen specifiek boek / Algemeen" else ""
        user_content = f"""GEEN BRONTEKST BESCHIKBAAR.

INSTRUCTIE: Gebruik je parate kennis over {subject}{book_context}.
Genereer representatieve, uitdagende vragen die een student van {subject} zou moeten kunnen beantwoorden.

Genereer nu EXACT {num_questions} multiple choice vragen SPECIFIEK over {subject} in JSON format."""
    
    messages.append({"role": "user", "content": user_content})
    
    response = get_ai_response(client, messages, has_image=False, json_mode=True)
    return clean_and_parse_json(response)


def generate_exam_questions(client: OpenAI, study: str, subject: str, book: str, total_questions: int, source_text: str = None, question_type: str = "Mix"):
    """
    🔧 FIX 1: BATCHING LOGICA (HOOFDFUNCTIE)
    Genereer tentamenvragen in batches van max 5 vragen.
    Voorkomt dat de AI te veel vragen tegelijk genereert en crasht.
    """
    BATCH_SIZE = 5
    num_batches = (total_questions + BATCH_SIZE - 1) // BATCH_SIZE  # Ceil division
    
    all_questions = []
    
    # Progress container
    progress_container = st.empty()
    progress_bar = st.progress(0)
    
    for batch_num in range(num_batches):
        # Bereken hoeveel vragen in deze batch
        remaining = total_questions - len(all_questions)
        questions_in_batch = min(BATCH_SIZE, remaining)
        
        # Update progress
        progress_container.info(f"📝 Batch {batch_num + 1}/{num_batches} wordt gegenereerd ({questions_in_batch} vragen)...")
        
        # Genereer batch
        batch_questions = generate_exam_batch(
            client,
            study,
            subject,
            book,
            questions_in_batch,
            source_text,
            question_type
        )
        
        if batch_questions:
            all_questions.extend(batch_questions)
        
        # Update progress bar
        progress_bar.progress((batch_num + 1) / num_batches)
    
    # Clear progress indicators
    progress_container.empty()
    progress_bar.empty()
    
    # Zorg dat we EXACT het juiste aantal vragen hebben
    if len(all_questions) > total_questions:
        all_questions = all_questions[:total_questions]
    
    return all_questions


def start_exam_mode(client: OpenAI, study: str, subject: str, book: str, num_questions: int, question_type: str = "Mix"):
    """Start tentamenmodus - WERKT MET OF ZONDER BESTAND."""
    
    # Check alleen of het een afbeelding is
    if st.session_state.file_type == "image":
        st.warning("⚠️ Tentamenmodus werkt niet met afbeeldingen. Upload een PDF of genereer zonder bestand.")
        return
    
    # Informatieve tekst
    if not st.session_state.source_text or not st.session_state.source_text.strip():
        book_info = f" op basis van '{book}'" if book and book != "Geen specifiek boek / Algemeen" else ""
        st.info(f"💡 Geen bestand geüpload? Geen probleem. De AI genereert vragen{book_info} uit parate kennis over {subject}.")
    
    # 🔧 FIX 1: Gebruik de nieuwe batching functie
    questions = generate_exam_questions(
        client, 
        study, 
        subject, 
        book, 
        num_questions, 
        st.session_state.source_text if st.session_state.source_text else None,
        question_type
    )
    
    if not questions or len(questions) == 0:
        st.error("❌ Kon geen vragen genereren. Probeer opnieuw.")
        return
    
    st.session_state.exam_questions = questions
    st.session_state.exam_answers = {}
    st.session_state.exam_completed = False
    st.session_state.context_set = True
    st.success(f"✅ Tentamen gegenereerd met {len(questions)} vragen over {subject}!")
    st.rerun()


def evaluate_exam():
    """Evalueer tentamen antwoorden."""
    results = []
    
    for i, question in enumerate(st.session_state.exam_questions):
        user_answer = st.session_state.exam_answers.get(i, "")
        correct_answer = question.get("correct_antwoord", "")
        
        is_correct = user_answer == correct_answer
        
        results.append({
            "vraag": question.get("vraag", ""),
            "opties": question.get("opties", []),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "uitleg": question.get("uitleg", ""),
            "correct": is_correct
        })
    
    return results


# ============================================================================
# 🃏 FLASHCARD MODUS FUNCTIES - FLEXIBEL (MET OF ZONDER BESTAND)
# ============================================================================

def generate_flashcards_json(client: OpenAI, study: str, subject: str, book: str, source_text: str = None):
    """
    🧠 INTELLIGENTE FLASHCARD GENERATIE
    Werkt met OF zonder brontekst.
    """
    system_prompt = construct_system_prompt(study, subject, book, "flashcards")
    messages = [{"role": "system", "content": system_prompt}]
    
    if source_text and source_text.strip():
        # MET BRONTEKST
        user_content = f"""STUDIEMATERIAAL voor {subject}:

{source_text}

INSTRUCTIE: Gebruik ENKEL de brontekst voor de flashcards.
Genereer nu 10 flashcards SPECIFIEK over {subject} in JSON format."""
    else:
        # ZONDER BRONTEKST
        book_context = f" zoals behandeld in '{book}'" if book and book != "Geen specifiek boek / Algemeen" else ""
        user_content = f"""GEEN BRONTEKST BESCHIKBAAR.

INSTRUCTIE: Gebruik je parate kennis over {subject}{book_context}.
Genereer de 10 belangrijkste begrippen/concepten die een student van {subject} MOET kennen.

Genereer nu 10 flashcards SPECIFIEK over {subject} in JSON format."""
    
    messages.append({"role": "user", "content": user_content})
    
    with st.spinner(f"🃏 Flashcards worden gegenereerd voor {subject}..."):
        response = get_ai_response(client, messages, has_image=False, json_mode=True)
    
    return clean_and_parse_json(response)


def start_flashcard_mode(client: OpenAI, study: str, subject: str, book: str):
    """Start flashcard modus - WERKT MET OF ZONDER BESTAND."""
    
    # Check alleen of het een afbeelding is
    if st.session_state.file_type == "image":
        st.warning("⚠️ Flashcard modus werkt niet met afbeeldingen. Upload een PDF of genereer zonder bestand.")
        return
    
    # Informatieve tekst
    if not st.session_state.source_text or not st.session_state.source_text.strip():
        book_info = f" uit '{book}'" if book and book != "Geen specifiek boek / Algemeen" else ""
        st.info(f"💡 Geen bestand geüpload? Geen probleem. De AI genereert flashcards{book_info} uit parate kennis over {subject}.")
    
    # Genereer flashcards (met of zonder brontekst)
    flashcards = generate_flashcards_json(
        client,
        study,
        subject,
        book,
        st.session_state.source_text if st.session_state.source_text else None
    )
    
    if not flashcards or len(flashcards) == 0:
        st.error("❌ Kon geen flashcards genereren. Probeer opnieuw.")
        return
    
    st.session_state.flashcards = flashcards
    st.session_state.current_flashcard_index = 0
    st.session_state.show_flashcard_answer = False
    st.session_state.context_set = True
    st.success(f"✅ {len(flashcards)} flashcards gegenereerd voor {subject}!")
    st.rerun()


# ============================================================================
# 🚀 MAIN APPLICATIE
# ============================================================================

def main():
    """Hoofdfunctie voor de White Label Studie-Applicatie."""
    
    initialize_session_state()
    
    # ⚠️ BELANGRIJK: Stel page_config in VOOR de sidebar rendering
    # Gebruik de huidige session_state waarde (wordt later geüpdatet)
    st.set_page_config(
        page_title=f"AI Studietrainer - {st.session_state.selected_major}",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    client = get_openai_client()
    
    # ========================================================================
    # SIDEBAR - MET JAAR HIERARCHIE
    # ========================================================================
    
    with st.sidebar:
        st.title("⚙️ Instellingen")
        
        # Studie selectie MET CALLBACK
        st.markdown("### 📚 Selecteer Studierichting")
        
        major_list = list(STUDY_FIELDS.keys())
        try:
            current_major_index = major_list.index(st.session_state.selected_major)
        except ValueError:
            current_major_index = 0
            st.session_state.selected_major = major_list[0]
        
        selected_major = st.selectbox(
            "Hoofdstudie:",
            major_list,
            index=current_major_index,
            key="major_selector",
            on_change=reset_study_state
        )
        
        # ✅ UPDATE: Zorg dat selected_major DIRECT wordt geüpdatet
        st.session_state.selected_major = selected_major
        
        # NIEUW: Jaar selectie MET CALLBACK
        st.markdown("### 📅 Selecteer Studiejaar")
        
        year_list = list(STUDY_FIELDS[selected_major]["years"].keys())
        try:
            current_year_index = year_list.index(st.session_state.selected_year)
        except ValueError:
            current_year_index = 0
            st.session_state.selected_year = year_list[0]
        
        selected_year = st.selectbox(
            "Studiejaar:",
            year_list,
            index=current_year_index,
            key="year_selector",
            on_change=reset_year_state
        )
        
        st.session_state.selected_year = selected_year
        
        # Vak selectie (afhankelijk van studie + jaar)
        st.markdown("### 📖 Selecteer Vak")
        
        current_subjects = STUDY_FIELDS[selected_major]["years"][selected_year]["sub_subjects"]
        try:
            current_subject_index = current_subjects.index(st.session_state.selected_subject)
        except ValueError:
            current_subject_index = 0
            st.session_state.selected_subject = current_subjects[0]
        
        selected_subject = st.selectbox(
            "Specifiek vak:",
            current_subjects,
            index=current_subject_index,
            key="subject_selector"
        )
        st.session_state.selected_subject = selected_subject
        
        # Boek selectie (dynamisch, afhankelijk van studie + jaar + vak)
        st.markdown("### 📚 Focus op Boek (Optioneel)")
        
        available_books = STUDY_FIELDS[selected_major]["years"][selected_year]["books"].get(selected_subject, [])
        book_options = ["Geen specifiek boek / Algemeen"] + available_books
        
        try:
            current_book_index = book_options.index(st.session_state.selected_book)
        except ValueError:
            current_book_index = 0
            st.session_state.selected_book = "Geen specifiek boek / Algemeen"
        
        selected_book = st.selectbox(
            "Kies een boek:",
            book_options,
            index=current_book_index,
            key="book_selector",
            help="Selecteer een specifiek boek om de AI te laten focussen op de stijl en terminologie van dat boek"
        )
        st.session_state.selected_book = selected_book
        
        st.markdown("---")
        
        # 🔒 FIX 2: Studiemodus selectie MET CALLBACK
        st.markdown("### 🎯 Kies Modus")
        study_mode = st.selectbox(
            "Studiemodus:",
            ["🟢 Oefenen", "📝 Tentamen Simulatie", "🃏 Flashcards"],
            key="mode_selector",
            on_change=reset_mode_state  # 🔒 CALLBACK VOOR NAVIGATIE FIX
        )
        st.session_state.study_mode = study_mode
        
        # Slider voor Tentamen
        if study_mode == "📝 Tentamen Simulatie":
            st.markdown("#### ⚙️ Tentamen Instellingen")
            num_questions = st.slider(
                "Aantal vragen:",
                min_value=3,
                max_value=20,
                value=st.session_state.exam_num_questions,
                step=1,
                key="exam_slider"
            )
            st.session_state.exam_num_questions = num_questions
            
            # 🏥 FIX 3: GENEESKUNDE SPECIFIEK - Vraagtype selectie
            if selected_major == "Geneeskunde 🩺":
                st.markdown("#### 🏥 Vraagtype (Geneeskunde)")
                question_type = st.radio(
                    "Type vragen:",
                    ["Mix", "Klinisch (Casussen)", "Theoretisch (Feiten)"],
                    index=["Mix", "Klinisch (Casussen)", "Theoretisch (Feiten)"].index(st.session_state.exam_question_type),
                    key="question_type_selector",
                    help="Kies het type vragen voor je tentamen"
                )
                st.session_state.exam_question_type = question_type
        
        st.markdown("---")
        
        # Score weergave
        if st.session_state.study_mode == "🟢 Oefenen" and st.session_state.context_set and st.session_state.total_questions > 0:
            st.markdown("### 📊 Jouw Score")
            
            score_display = f"{st.session_state.score} / {st.session_state.total_questions}"
            percentage = (st.session_state.score / st.session_state.total_questions) * 100
            
            st.metric("Score", score_display)
            st.progress(st.session_state.score / st.session_state.total_questions)
            st.caption(f"✨ {percentage:.1f}% correct")
            
            st.markdown("---")
        
        # Reset knop
        if st.button("🔄 Reset Sessie", use_container_width=True):
            reset_session()
            st.rerun()
        
        st.markdown("---")
        
        # Instructies
        st.markdown("### 📖 Instructies")
        if study_mode == "🟢 Oefenen":
            st.markdown("""
            1. **Selecteer** jaar, vak en optioneel een boek
            2. **Upload** studiemateriaal (optioneel)
            3. **Klik** op "Start Oefenen" of "Start zonder bestand"
            4. **Beantwoord** vragen van de AI
            5. **Ontvang** directe feedback
            """)
        elif study_mode == "📝 Tentamen Simulatie":
            st.markdown("""
            1. **Stel** aantal vragen in (slider)
            2. **Upload** studiemateriaal (optioneel!)
            3. **Klik** op "Genereer Tentamen"
            4. **Beantwoord** alle vragen
            5. **Lever in** en zie je cijfer (1-10)
            """)
        else:
            st.markdown("""
            1. **Upload** studiemateriaal (optioneel!)
            2. **Klik** op "Genereer Flashcards"
            3. **Bestudeer** begrippen
            4. **Klik** om definitie te zien
            5. **Navigeer** door de kaarten
            """)
        
        st.markdown("---")
        st.caption(f"🎨 {selected_major}")
        st.caption(f"📅 {selected_year}")
        st.caption(f"📖 {selected_subject}")
        if selected_book != "Geen specifiek boek / Algemeen":
            st.caption(f"📚 {selected_book}")
        st.caption(f"🎯 {study_mode}")
    
    # ========================================================================
    # ✅ BEPAAL CURRENT_CONFIG NA SIDEBAR RENDERING
    # ========================================================================
    
    # Nu pas bepalen we de current_config op basis van de GEÜPDATETE session_state
    current_major = st.session_state.selected_major
    current_config = STUDY_FIELDS[current_major]
    
    # ✅ PAS NU PAS DE STYLING TOE (na sidebar rendering)
    apply_custom_styling(current_config["color"])
    
    # ========================================================================
    # MAIN CONTENT - MET VERSE VARIABELEN
    # ========================================================================
    
    st.title(f"🎓 AI Studietrainer - Bachelor Suite")
    st.markdown(f"### {current_major} - {st.session_state.selected_year}")
    st.markdown(f"**Vak:** {st.session_state.selected_subject}")
    if st.session_state.selected_book != "Geen specifiek boek / Algemeen":
        st.markdown(f"**Boek:** {st.session_state.selected_book}")
    st.markdown(f"**Modus:** {st.session_state.study_mode}")
    st.markdown("---")
    
    # ========================================================================
    # UPLOAD INTERFACE
    # ========================================================================
    
    if not st.session_state.context_set:
        st.subheader("📤 Upload Studiemateriaal (Optioneel)")
        
        uploaded_file = st.file_uploader(
            "Kies een bestand:",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Upload een PDF met tekst of een afbeelding (alleen voor Oefenmodus)"
        )
        
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == "pdf":
                with st.spinner("📄 PDF wordt verwerkt..."):
                    text, num_pages = extract_text_from_pdf(uploaded_file)
                    if text:
                        st.session_state.source_text = text
                        st.session_state.file_type = "pdf"
                        st.success(f"✅ PDF succesvol verwerkt! ({num_pages} pagina's, {len(text)} karakters)")
            
            elif file_extension in ["png", "jpg", "jpeg"]:
                if st.session_state.study_mode != "🟢 Oefenen":
                    st.warning("⚠️ Afbeeldingen worden alleen ondersteund in Oefenmodus.")
                else:
                    with st.spinner("🖼️ Afbeelding wordt verwerkt..."):
                        st.session_state.image_base64 = encode_image(uploaded_file)
                        st.session_state.file_type = "image"
                        uploaded_file.seek(0)
                        st.image(uploaded_file, caption="Geüploade afbeelding", use_container_width=True)
                        st.success("✅ Afbeelding succesvol verwerkt!")
        
        # Start knoppen (dynamisch per modus)
        st.markdown("---")
        
        if st.session_state.study_mode == "🟢 Oefenen":
            col1, col2 = st.columns(2)
            
            with col1:
                # Dynamische knop tekst
                if st.session_state.source_text or st.session_state.image_base64:
                    button_text = "🚀 Start Oefenen\n(uit Bestand)"
                else:
                    button_text = "🚀 Start Oefenen\n(uit Boek)"
                
                if st.button(button_text, use_container_width=True, type="primary"):
                    start_practice_mode(
                        client, 
                        st.session_state.selected_major, 
                        st.session_state.selected_subject,
                        st.session_state.selected_book,
                        with_file=True
                    )
            
            with col2:
                button_text = "🎲 Start zonder bestand\n(AI kiest onderwerp)"
                if st.session_state.selected_book != "Geen specifiek boek / Algemeen":
                    button_text = f"📚 Start zonder bestand\n(uit {st.session_state.selected_book[:20]}...)"
                
                if st.button(button_text, use_container_width=True):
                    start_practice_mode(
                        client, 
                        st.session_state.selected_major, 
                        st.session_state.selected_subject,
                        st.session_state.selected_book,
                        with_file=False
                    )
        
        elif st.session_state.study_mode == "📝 Tentamen Simulatie":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Dynamische knop tekst
                if st.session_state.source_text:
                    button_text = f"📝 Genereer Tentamen\n({st.session_state.exam_num_questions} vragen uit Bestand)"
                else:
                    book_suffix = f" uit {st.session_state.selected_book}" if st.session_state.selected_book != "Geen specifiek boek / Algemeen" else ""
                    button_text = f"🚀 Genereer Tentamen\n({st.session_state.exam_num_questions} vragen{book_suffix})"
                
                if st.button(button_text, use_container_width=True, type="primary"):
                    start_exam_mode(
                        client, 
                        st.session_state.selected_major, 
                        st.session_state.selected_subject,
                        st.session_state.selected_book,
                        st.session_state.exam_num_questions,
                        st.session_state.exam_question_type
                    )
        
        else:  # Flashcards
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Dynamische knop tekst
                if st.session_state.source_text:
                    button_text = "🃏 Maak Flashcards\n(uit Bestand)"
                else:
                    book_suffix = f" uit {st.session_state.selected_book}" if st.session_state.selected_book != "Geen specifiek boek / Algemeen" else ""
                    button_text = f"🚀 Maak Flashcards\n(uit Boek{book_suffix})"
                
                if st.button(button_text, use_container_width=True, type="primary"):
                    start_flashcard_mode(
                        client, 
                        st.session_state.selected_major, 
                        st.session_state.selected_subject,
                        st.session_state.selected_book
                    )
    
    # ========================================================================
    # ACTIEVE SESSIE
    # ========================================================================
    
    else:
        if st.session_state.study_mode == "🟢 Oefenen":
            st.subheader("💬 Training Sessie")
            
            # 🔧 BUG FIX 1: Trigger AI response als we vanuit tentamen komen
            if st.session_state.trigger_ai_response:
                st.session_state.trigger_ai_response = False
                
                # Haal de laatste user message op
                if st.session_state.history and st.session_state.history[-1]["role"] == "user":
                    user_context_message = st.session_state.history[-1]["content"]
                    
                    # Trigger AI om direct te antwoorden
                    system_prompt = construct_system_prompt(
                        st.session_state.selected_major,
                        st.session_state.selected_subject,
                        st.session_state.selected_book,
                        "practice"
                    )
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_context_message}
                    ]
                    
                    with st.spinner("🤖 AI bereidt een uitgebreide uitleg voor..."):
                        ai_response = get_ai_response(client, messages, has_image=False)
                    
                    if not ai_response.startswith("❌"):
                        st.session_state.history.append({
                            "role": "assistant",
                            "content": ai_response
                        })
                        st.rerun()
            
            for message in st.session_state.history:
                if message["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message["content"])
                elif message["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
            
            user_input = st.chat_input("Type je antwoord hier...")
            
            if user_input:
                handle_practice_answer(
                    client,
                    user_input,
                    st.session_state.selected_major,
                    st.session_state.selected_subject,
                    st.session_state.selected_book
                )
                st.rerun()
        
        elif st.session_state.study_mode == "📝 Tentamen Simulatie":
            if not st.session_state.exam_completed:
                st.subheader("📝 Tentamen - Multiple Choice")
                
                num_questions = len(st.session_state.exam_questions)
                st.info(f"📋 Tentamen met {num_questions} vragen over {st.session_state.selected_subject} | Beantwoord alle vragen en lever in")
                
                with st.form("exam_form"):
                    for i, question in enumerate(st.session_state.exam_questions):
                        st.markdown(f"### Vraag {i+1}")
                        st.markdown(question.get("vraag", ""))
                        
                        options = question.get("opties", [])
                        selected = st.radio(
                            f"Kies je antwoord:",
                            options,
                            key=f"q_{i}",
                            index=None
                        )
                        
                        if selected:
                            st.session_state.exam_answers[i] = selected
                        
                        st.markdown("---")
                    
                    submitted = st.form_submit_button("✅ Lever Tentamen In", use_container_width=True, type="primary")
                    
                    if submitted:
                        if len(st.session_state.exam_answers) < num_questions:
                            st.error(f"⚠️ Je hebt nog niet alle vragen beantwoord ({len(st.session_state.exam_answers)}/{num_questions})")
                        else:
                            st.session_state.exam_completed = True
                            st.rerun()
            
            else:
                st.subheader("📊 Tentamen Resultaten")
                
                results = evaluate_exam()
                
                num_questions = len(results)
                correct_count = sum(1 for r in results if r["correct"])
                grade = (correct_count / num_questions) * 9 + 1
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if grade >= 5.5:
                        st.success(f"### 🎓 Je cijfer: {grade:.1f}")
                        st.balloons()
                    else:
                        st.error(f"### 📉 Je cijfer: {grade:.1f}")
                    
                    st.progress(correct_count / num_questions)
                    st.caption(f"{correct_count} van {num_questions} vragen correct ({int(correct_count/num_questions*100)}%)")
                
                st.markdown("---")
                st.markdown("### 📋 Gedetailleerde Feedback")
                
                for i, result in enumerate(results):
                    emoji = "✅" if result["correct"] else "❌"
                    
                    with st.expander(f"{emoji} Vraag {i+1}: {result['vraag'][:60]}..."):
                        st.markdown(f"**Vraag:**\n{result['vraag']}")
                        st.markdown("---")
                        
                        st.markdown("**Opties:**")
                        for opt in result['opties']:
                            st.markdown(f"- {opt}")
                        
                        st.markdown("---")
                        
                        if result["correct"]:
                            st.success(f"**Jouw antwoord:** {result['user_answer']} ✅")
                        else:
                            st.error(f"**Jouw antwoord:** {result['user_answer']} ❌")
                            st.info(f"**Correct antwoord:** {result['correct_answer']}")
                        
                        st.markdown("---")
                        st.markdown(f"**Uitleg:**\n{result['uitleg']}")
                        
                        # 🧠 OEFENEN MET DIT ONDERWERP - Alleen bij foute antwoorden
                        if not result["correct"]:
                            st.markdown("---")
                            
                            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                            with col_btn2:
                                # 🔧 BUG FIX 1: Gebruik on_click callback om state modification error te voorkomen
                                st.button(
                                    "🧠 Oefenen met dit onderwerp",
                                    key=f"practice_{i}",
                                    use_container_width=True,
                                    type="primary",
                                    on_click=switch_to_practice_mode,
                                    args=(
                                        result['vraag'],
                                        result['user_answer'],
                                        result['correct_answer'],
                                        result['uitleg']
                                    )
                                )
        
        else:  # Flashcards
            st.subheader("🃏 Flashcards")
            
            if st.session_state.flashcards:
                total_cards = len(st.session_state.flashcards)
                current_index = st.session_state.current_flashcard_index
                current_card = st.session_state.flashcards[current_index]
                
                st.progress((current_index + 1) / total_cards)
                st.caption(f"Kaart {current_index + 1} van {total_cards}")
                
                st.markdown("---")
                
                if not st.session_state.show_flashcard_answer:
                    st.markdown(f"### 📌 Begrip:")
                    st.markdown(f"## {current_card.get('term', '')}")
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🔍 Toon Definitie", use_container_width=True, type="primary"):
                            st.session_state.show_flashcard_answer = True
                            st.rerun()
                
                else:
                    st.markdown(f"### 📌 Begrip:")
                    st.markdown(f"## {current_card.get('term', '')}")
                    
                    st.markdown("---")
                    
                    st.markdown(f"### ✅ Definitie:")
                    st.markdown(f"{current_card.get('definitie', '')}")
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if current_index > 0:
                            if st.button("⬅️ Vorige", use_container_width=True):
                                st.session_state.current_flashcard_index -= 1
                                st.session_state.show_flashcard_answer = False
                                st.rerun()
                    
                    with col2:
                        if st.button("🔄 Verberg", use_container_width=True):
                            st.session_state.show_flashcard_answer = False
                            st.rerun()
                    
                    with col3:
                        if current_index < total_cards - 1:
                            if st.button("Volgende ➡️", use_container_width=True, type="primary"):
                                st.session_state.current_flashcard_index += 1
                                st.session_state.show_flashcard_answer = False
                                st.rerun()
                        else:
                            st.success("🎉 Alle kaarten voltooid!")
            
            else:
                st.info("Geen flashcards beschikbaar.")


if __name__ == "__main__":
    main()
