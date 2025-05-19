from random import choice
from .gem import process_generated_content


def generate_content(model, version, api_key, theme, text, mode="agricultural consultant", max_paragraphs=1, max_words_per_sentence=6):

    # Mode-specific instructions
    if mode.lower() == "agricultural engineer":
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
    elif mode == "farm manager":
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
    
    elif mode == "agricultural consultant":
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
        
    elif mode == "quality manager":
        specific_instructions = f"""
            Give a response only, without any explanations,
            comments, or supplementary text.
            Here's the request: 
            Act as an expert Agricultural Engineer with 15+ years of experience in sustainable farming, precision agriculture, irrigation systems, crop management, and agribusiness solutions. Your role is to provide scientifically accurate, practical, and innovative advice tailored to farmers, agronomists, policymakers, and researchers.

                When responding:

                    Assess the context (e.g., climate, soil type, crop, scale of operation).

                    Prioritize sustainability (resource efficiency, eco-friendly practices).

                    Use data-driven insights (mention tools like GIS, remote sensing, or IoT if relevant).

                    Explain technical terms clearly for non-experts but retain depth for professionals.

                    Offer actionable steps (e.g., irrigation schedules, pest control methods, tech recommendations).

                Example scenarios you might address:

                    Designing drip irrigation for arid regions.

                    Optimizing fertilizer use with soil sensors.

                    Mitigating post-harvest losses in developing countries.

                    Integrating AI/robotics into modern farms.

            Always cite recent research or case studies when possible.

            Provide only the response, no explanations.
        """
    elif mode == "crop manager" or "agronomist":
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
    elif mode == "operations" or "production manager":
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