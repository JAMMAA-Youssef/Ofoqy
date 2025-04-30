import logging
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Session storage
user_sessions = {}

# Questions by RIASEC type
questions_by_type = {
    "Realistic": [
        "Dans quelle mesure êtes-vous intéressé(e) par réparer un moteur ?",
        "Dans quelle mesure êtes-vous intéressé(e) par utiliser des outils de menuiserie ?",
        "Dans quelle mesure êtes-vous intéressé(e) par conduire un chariot élévateur ?",
        "Dans quelle mesure êtes-vous intéressé(e) par cultiver des plantes ?",
        "Dans quelle mesure êtes-vous intéressé(e) par travailler dehors ?",
        "Dans quelle mesure êtes-vous intéressé(e) par installer un système électrique ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire de la plomberie ?",
        "Dans quelle mesure êtes-vous intéressé(e) par utiliser une perceuse électrique ?",
        "Dans quelle mesure êtes-vous intéressé(e) par réparer un vélo ?",
        "Dans quelle mesure êtes-vous intéressé(e) par peindre une maison ?"
    ],
    "Investigative": [
        "Dans quelle mesure êtes-vous intéressé(e) par résoudre des problèmes de mathématiques ?",
        "Dans quelle mesure êtes-vous intéressé(e) par analyser des données ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire des expériences scientifiques ?",
        "Dans quelle mesure êtes-vous intéressé(e) par étudier l’anatomie humaine ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire de la recherche en laboratoire ?",
        "Dans quelle mesure êtes-vous intéressé(e) par lire des articles scientifiques ?",
        "Dans quelle mesure êtes-vous intéressé(e) par observer des phénomènes naturels ?",
        "Dans quelle mesure êtes-vous intéressé(e) par calculer des statistiques ?",
        "Dans quelle mesure êtes-vous intéressé(e) par étudier le comportement humain ?",
        "Dans quelle mesure êtes-vous intéressé(e) par écrire un rapport technique ?"
    ],
    "Artistic": [
        "Dans quelle mesure êtes-vous intéressé(e) par peindre un tableau ?",
        "Dans quelle mesure êtes-vous intéressé(e) par écrire de la poésie ?",
        "Dans quelle mesure êtes-vous intéressé(e) par jouer d’un instrument de musique ?",
        "Dans quelle mesure êtes-vous intéressé(e) par créer une affiche graphique ?",
        "Dans quelle mesure êtes-vous intéressé(e) par écrire une pièce de théâtre ?",
        "Dans quelle mesure êtes-vous intéressé(e) par photographier la nature ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire du théâtre ?",
        "Dans quelle mesure êtes-vous intéressé(e) par illustrer un livre ?",
        "Dans quelle mesure êtes-vous intéressé(e) par créer une animation ?",
        "Dans quelle mesure êtes-vous intéressé(e) par improviser une chanson ?"
    ],
    "Social": [
        "Dans quelle mesure êtes-vous intéressé(e) par aider une personne âgée ?",
        "Dans quelle mesure êtes-vous intéressé(e) par enseigner à des enfants ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire du bénévolat dans un centre social ?",
        "Dans quelle mesure êtes-vous intéressé(e) par organiser une collecte de fonds ?",
        "Dans quelle mesure êtes-vous intéressé(e) par être à l’écoute des autres ?",
        "Dans quelle mesure êtes-vous intéressé(e) par encourager quelqu’un en difficulté ?",
        "Dans quelle mesure êtes-vous intéressé(e) par expliquer une idée à un groupe ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire une présentation éducative ?",
        "Dans quelle mesure êtes-vous intéressé(e) par travailler avec des enfants handicapés ?",
        "Dans quelle mesure êtes-vous intéressé(e) par contribuer à une œuvre caritative ?"
    ],
    "Enterprising": [
        "Dans quelle mesure êtes-vous intéressé(e) par lancer un nouveau produit ?",
        "Dans quelle mesure êtes-vous intéressé(e) par diriger une équipe ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire une campagne publicitaire ?",
        "Dans quelle mesure êtes-vous intéressé(e) par convaincre quelqu’un d’acheter quelque chose ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire une négociation ?",
        "Dans quelle mesure êtes-vous intéressé(e) par présenter un projet devant un public ?",
        "Dans quelle mesure êtes-vous intéressé(e) par créer une entreprise ?",
        "Dans quelle mesure êtes-vous intéressé(e) par organiser une conférence ?",
        "Dans quelle mesure êtes-vous intéressé(e) par gérer un projet d’équipe ?",
        "Dans quelle mesure êtes-vous intéressé(e) par défendre un point de vue ?"
    ],
    "Conventional": [
        "Dans quelle mesure êtes-vous intéressé(e) par classer des fichiers ?",
        "Dans quelle mesure êtes-vous intéressé(e) par travailler avec des feuilles Excel ?",
        "Dans quelle mesure êtes-vous intéressé(e) par gérer un agenda ?",
        "Dans quelle mesure êtes-vous intéressé(e) par organiser des documents ?",
        "Dans quelle mesure êtes-vous intéressé(e) par faire de la comptabilité ?",
        "Dans quelle mesure êtes-vous intéressé(e) par remplir des formulaires administratifs ?",
        "Dans quelle mesure êtes-vous intéressé(e) par créer un tableau budgétaire ?",
        "Dans quelle mesure êtes-vous intéressé(e) par corriger des erreurs de frappe ?",
        "Dans quelle mesure êtes-vous intéressé(e) par suivre un planning ?",
        "Dans quelle mesure êtes-vous intéressé(e) par utiliser un logiciel de gestion ?"
    ]
}

ria_sec_universities = {
    "Realistic": [
        "🔧 <b>Filières</b>: Génie mécanique, Génie civil, Énergies renouvelables",
        "🏫 <b>Écoles</b>: ENSAM Meknès, ENSA Agadir, IAV Rabat"
    ],
    "Investigative": [
        "🔬 <b>Filières</b>: Mathématiques, Médecine, Informatique, Sciences de la vie",
        "🏫 <b>Écoles</b>: Faculté des Sciences Marrakech, FMP Rabat, Al Akhawayn"
    ],
    "Artistic": [
        "🎨 <b>Filières</b>: Beaux-arts, Design, Littérature, Architecture",
        "🏫 <b>Écoles</b>: INBA Tétouan, ENA Rabat, Faculté des Lettres"
    ],
    "Social": [
        "🧑‍🏫 <b>Filières</b>: Éducation, Infirmier, Psychologie, Sociologie",
        "🏫 <b>Écoles</b>: ENS Rabat, FMP Marrakech, Faculté des Lettres"
    ],
    "Enterprising": [
        "💼 <b>Filières</b>: Commerce, Management, Marketing, Droit, Sciences Politiques",
        "🏫 <b>Écoles</b>: ENCG Casablanca, Rabat Business School, Faculté de Droit"
    ],
    "Conventional": [
        "📊 <b>Filières</b>: Comptabilité, Finance, Gestion, Statistiques",
        "🏫 <b>Écoles</b>: ENCG Agadir, Faculté d’Économie Rabat, Al Akhawayn"
    ]
}

university_info = {
    "ensa": {
        "Nom": "ENSA Agadir",
        "Ville": "Agadir",
        "Spécialités": "Génie Informatique, Électrique, Civil",
        "Site": "http://www.ensa-agadir.ac.ma/",
        "Téléphone": "+212 528 22 83 13",
        "Présentation": "L'École Nationale des Sciences Appliquées d'Agadir (ENSA Agadir), affiliée à l'Université Ibn Zohr, est l'une des principales écoles d'ingénieurs du sud du Maroc. Elle propose des formations de haut niveau en génie informatique, génie électrique, génie civil et systèmes industriels. Elle est équipée de laboratoires modernes et développe des partenariats avec des entreprises locales."
    },
    "ensam": {
        "Nom": "ENSAM Meknès",
        "Ville": "Meknès",
        "Spécialités": "Génie Mécanique, Génie Industriel",
        "Site": "https://www.ensam-umi.ac.ma/",
        "Téléphone": "+212 5 35 46 71 60",
        "Présentation": "L'École Nationale Supérieure d'Arts et Métiers de Meknès (ENSAM), rattachée à l'Université Moulay Ismaïl, forme des ingénieurs dans le domaine industriel. Elle propose des parcours en mécanique, électromécanique et production industrielle avec un fort accent sur la pratique."
    },
    "iav": {
        "Nom": "IAV Rabat",
        "Ville": "Rabat",
        "Spécialités": "Agronomie, Médecine vétérinaire",
        "Site": "http://www.iav.ac.ma/",
        "Téléphone": "+212 537 68 19 49",
        "Présentation": "L'Institut Agronomique et Vétérinaire Hassan II (IAV) est une référence en sciences agricoles et vétérinaires. Il forme des ingénieurs agronomes, vétérinaires et experts en environnement et développement rural. Il dispose de fermes expérimentales et de laboratoires avancés."
    },
    "fmp": {
        "Nom": "Faculté de Médecine Rabat",
        "Ville": "Rabat",
        "Spécialités": "Médecine, Pharmacie",
        "Site": "http://fmp.um5.ac.ma/",
        "Téléphone": "+212 537 77 29 82",
        "Présentation": "La Faculté de Médecine et de Pharmacie de Rabat est l’un des établissements médicaux les plus anciens du Maroc. Elle offre des cursus en médecine, spécialités médicales, pharmacie et recherche biomédicale avec accès aux CHU."
    },
    "akhawayn": {
        "Nom": "Université Al Akhawayn",
        "Ville": "Ifrane",
        "Spécialités": "Business, Informatique, Ingénierie",
        "Site": "https://www.aui.ma/",
        "Téléphone": "+212 535 86 29 00",
        "Présentation": "Al Akhawayn est une université privée à Ifrane qui suit un modèle américain. Elle propose des formations en anglais en business, sciences informatiques, ingénierie, sciences humaines et relations internationales."
    },
    "inba": {
        "Nom": "INBA Tétouan",
        "Ville": "Tétouan",
        "Spécialités": "Beaux-arts, Arts visuels",
        "Site": "https://www.inba-tetouan.ma/",
        "Téléphone": "+212 539 97 90 00",
        "Présentation": "L’Institut National des Beaux-Arts de Tétouan forme des artistes dans la peinture, le graphisme, la sculpture et le design visuel. Il joue un rôle culturel important au Maroc et en Méditerranée."
    },
    "encg": {
        "Nom": "ENCG Casablanca",
        "Ville": "Casablanca",
        "Spécialités": "Marketing, Finance, Audit, Logistique",
        "Site": "https://www.encgcasa.ma/",
        "Téléphone": "+212 522 22 33 44",
        "Présentation": "L'École Nationale de Commerce et de Gestion de Casablanca forme des cadres en gestion, commerce, finance et logistique. Elle est réputée pour ses débouchés professionnels et ses partenariats avec les entreprises."
    },
    "ena": {
        "Nom": "École Nationale d'Architecture de Rabat",
        "Ville": "Rabat",
        "Spécialités": "Architecture, Urbanisme, Patrimoine",
        "Site": "https://www.enarabat.ac.ma/",
        "Téléphone": "+212 537 70 40 40",
        "Présentation": "L'École Nationale d’Architecture de Rabat est la première école d’architecture du Maroc. Elle propose un cursus de six ans axé sur la conception, l’urbanisme et la réhabilitation patrimoniale."
    },
    "fst": {
        "Nom": "Faculté des Sciences et Techniques - Fès",
        "Ville": "Fès",
        "Spécialités": "Informatique, Mathématiques, Biologie, Chimie, Physique",
        "Site": "https://www.fst-usmba.ac.ma/",
        "Téléphone": "+212 535 61 20 00",
        "Présentation": "La FST Fès offre des formations en sciences et technologies avec une forte orientation pratique. Elle est intégrée à l’Université Sidi Mohamed Ben Abdellah et dispose de laboratoires et d’unités de recherche modernes."
    }
}

# --- Command logic ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue sur le bot OFOQY ! Tape /holland pour commencer le test ou /university pour explorer les écoles."
    )

async def holland(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    questions = [(q, t) for t, lst in questions_by_type.items() for q in lst]
    random.shuffle(questions)
    user_sessions[user_id] = {
        "questions": questions,
        "index": 0,
        "scores": {k: 0 for k in questions_by_type}
    }
    await update.message.reply_text("""🎯 Pour chaque question, choisissez un chiffre de 1 à 5 selon votre degré d'intérêt :

1️⃣ : Pas du tout intéressé(e)
2️⃣ : Peu intéressé(e)
3️⃣ : Neutre
4️⃣ : Assez intéressé(e)
5️⃣ : Très intéressé(e)""")
    await send_next_question(update, context, user_id)

async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    session = user_sessions[user_id]
    if session["index"] < len(session["questions"]):
        q, _ = session["questions"][session["index"]]
        reply_markup = ReplyKeyboardMarkup([['1', '2', '3', '4', '5']], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"{session['index'] + 1}/{len(session['questions'])} ➤ {q}",
            reply_markup=reply_markup
        )
    else:
        await show_results(update, context, user_id)

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_sessions:
        return
    msg = update.message.text.strip()
    if msg not in ["1", "2", "3", "4", "5"]:
        await update.message.reply_text("Merci de répondre par un chiffre entre 1 et 5.")
        return
    val = int(msg)
    session = user_sessions[uid]
    _, typ = session["questions"][session["index"]]
    session["scores"][typ] += val
    session["index"] += 1
    await send_next_question(update, context, uid)

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    scores = user_sessions[user_id]["scores"]
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    dominant_type = sorted_scores[0][0]
    top3 = " - ".join([f"<b>{k}</b> ({v})" for k, v in sorted_scores[:3]])
    suggestions = "\n".join(ria_sec_universities.get(dominant_type, []))
    await update.message.reply_text(
        f"""✅ <b>Test terminé</b>

🎓 <b>Vos types dominants</b> : {top3}

{suggestions}

💡 Si vous souhaitez en savoir plus sur une université, tapez la commande /university pour afficher la liste.""",
        parse_mode="HTML"
    )
    del user_sessions[user_id]

async def university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmds = "\n".join([f"/{k}" for k in university_info])
    await update.message.reply_text("🏫 Tape une commande pour voir les infos :\n" + cmds)

def generate_university_command(code):
    async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = university_info[code]
        text = f"""🏛️ <b>{data['Nom']}</b>
<b>Ville</b>: {data['Ville']}
<b>Spécialités</b>: {data['Spécialités']}
<b>Site</b>: {data['Site']}
<b>Téléphone</b>: {data['Téléphone']}

{data['Présentation']}"""
        await update.message.reply_text(text, parse_mode="HTML")
    return show_info

def main():
    app = ApplicationBuilder().token("7698177248:AAHedsAQXWNVWs53QFVe6blPdqDn3aS28Dc").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("holland", holland))
    app.add_handler(CommandHandler("university", university))
    for code in university_info:
        app.add_handler(CommandHandler(code, generate_university_command(code)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    app.run_polling()

if __name__ == "__main__":
    main()


