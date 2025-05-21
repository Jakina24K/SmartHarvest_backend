from random import choice
from .gem import process_generated_content


def generate_content(model, version, api_key, theme, text, mode="agricultural consultant", max_paragraphs=1, max_words_per_sentence=6):

    # Mode-specific instructions
    if mode.lower() == "agricultural engineer":
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome IA spécialisé en pathologie végétale et agriculture de précision.

            Tâche : Analyser les données d'entrée : {text}, (la probability ne montre pas seulement la precission de la maladie, mais aussi la precision du nom de la plante).

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (le nom de plante, saine/ sa maladie), un diagnostic selon la précision, des interventions (maladie : traitements simple/traditionnelles/biologiques/chimiques, isolement, cultivars résistants; santé : pratiques d'entretien) (avec des explications d'application), des instructions necessaires à savoir avec la contexte de la plante, des recommandations d'outils technologiques (capteurs spectraux, PCR, drones), et des mesures de prévention durable (rotation culturale, amendements, ajustements microclimatiques).

            Réponse en français, sans texte supplémentaire.
        """

    elif mode == "farm manager":
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome IA spécialisé en pathologie végétale et agriculture de précision, avec un focus sur la gestion pratique.

            Tâche : Analyser les données d'entrée : {text}

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (climat, sol, culture, échelle d'exploitation), un diagnostic selon la précision (≥90% : 'haute confiance : [plante] présente [maladie/santé]'; 70-90% : 'confiance modérée, vérifier avec [test/outil]'; <70% : 'fiabilité faible, tester en laboratoire pour [pathogène/déficience]'), des interventions pratiques (maladie : traitements biologiques/chimiques, isolement, cultivars résistants; santé : gestion simplifiée comme irrigation, fertilisation), des outils technologiques accessibles (capteurs IoT, drones, apps IA), et des mesures de prévention durable (rotation, amendements sol, gestion microclimatique).

            Réponse en français, sans texte supplémentaire.
        """

    elif mode == "agricultural consultant":
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome IA spécialisé en pathologie végétale et agriculture de précision, avec un focus sur des conseils stratégiques.

            Tâche : Analyser les données d'entrée : {text}

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (climat, sol, culture, contraintes régionales), un diagnostic selon la précision (≥90% : 'haute confiance : [plante] présente [maladie/santé]'; 70-90% : 'confiance modérée, vérifier avec [test/outil]'; <70% : 'fiabilité faible, tester en laboratoire pour [pathogène/déficience]'), des interventions stratégiques (maladie : traitements biologiques/chimiques, isolement, cultivars adaptés; santé : optimisation des pratiques comme irrigation, nutrition), des outils technologiques avancés (SIG, drones, IA, capteurs), et des mesures de prévention durable (planification rotation, amendements, microclimat).

            Réponse en français, sans texte supplémentaire.
        """

    elif mode == "quality manager":
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome expert (15+ ans) en agriculture durable, précision, irrigation, gestion des cultures et solutions agro-industrielles.

            Tâche : Analyser les données d'entrée : {text}

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (climat, sol, culture, échelle, contraintes), des recommandations durables (pratiques éco-responsables, optimisation des ressources), des actions concrètes (gestion des cultures, irrigation, lutte antiparasitaire), l'intégration de technologies avancées (SIG, IoT, télédétection, IA), des références à des recherches ou études de cas récentes si pertinent, et les résultats attendus (amélioration de la productivité, qualité, durabilité).

            Réponse en français, sans texte supplémentaire.
        """

    elif mode in ["crop manager", "agronomist"]:
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome IA spécialisé en pathologie végétale et agriculture de précision, avec un focus sur la gestion des cultures.

            Tâche : Analyser les données d'entrée : {text}

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (climat, sol, culture, besoins spécifiques), un diagnostic selon la précision (≥90% : 'haute confiance : [plante] présente [maladie/santé]'; 70-90% : 'confiance modérée, vérifier avec [test/outil]'; <70% : 'fiabilité faible, tester en laboratoire pour [pathogène/déficience]'), des interventions optimisées (maladie : traitements biologiques/chimiques, isolement, cultivars résistants; santé : optimisation culturale comme irrigation, fertilisation), des outils technologiques (capteurs IoT, drones, analyses IA), et des mesures de prévention durable (rotation, amendements, gestion microclimatique).

            Réponse en français, sans texte supplémentaire.
        """

    elif mode in ["operations", "production manager"]:
        specific_instructions = f"""
            Fournir uniquement la réponse, sans commentaires ni texte supplémentaire.

            Requête : Agir en tant qu'ingénieur agronome IA spécialisé en pathologie végétale et agriculture de précision, avec un focus sur l'efficacité opérationnelle.

            Tâche : Analyser les données d'entrée : {text}

            Réponse : Fournir une réponse en un seul paragraphe intégrant : une évaluation du contexte (climat, sol, culture, contraintes opérationnelles), un diagnostic selon la précision (≥90% : 'haute confiance : [plante] présente [maladie/santé]'; 70-90% : 'confiance modérée, vérifier avec [test/outil]'; <70% : 'fiabilité faible, tester en laboratoire pour [pathogène/déficience]'), des interventions efficaces (maladie : traitements biologiques/chimiques, isolement, cultivars résistants; santé : pratiques opérationnelles comme irrigation, fertilisation), des outils technologiques (solutions IoT, drones, logiciels IA), et des mesures de prévention durable (rotation, amendements, optimisation microclimatique).

            Réponse en français, sans texte supplémentaire.
        """
    else:
        # Agricultural Consultant
        specific_instructions = f"""
           Give a response only, without comments, or supplementary text.

            Here's the request:

                Act as an AI Agricultural Engineer specializing in plant pathology and precision agriculture.
                
                    Your task is to analyze input data:{text}

                    For each query, respond with:

                        Diagnosis Confirmation:

                            If precision ≥90%, state: "High-confidence diagnosis: [plant] shows [X disease/health]."

                            If 70-90%, add: "Moderate confidence; verify with [additional test/tool]."

                            If <70%, warn: "Low reliability—recommend lab testing for [specific pathogen/nutrient deficiency]."

                    Immediate Actions:

                        Disease: Suggest targeted treatments (organic/chemical), isolation protocols, and resistant cultivars.

                        Health: Advise maintenance practices (e.g., optimal irrigation pH/NPK levels).

                    Precision Boost:

                        Recommend tools to improve accuracy (e.g., spectral sensors, PCR kits, or drone imaging).

                    Prevention:

                        Crop rotation, soil amendments, or microclimate adjustments.

                Provide only the response in french, no supplementary text.
                
        """

    if text and specific_instructions:
        full_prompt = specific_instructions
    else:
        return "Error: Missing data or specific instructions."

    # Simulate content generation (replace with actual model call)
    content = process_generated_content(model, version, api_key, full_prompt, True)
    return content