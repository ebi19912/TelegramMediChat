"""
Medical and pharmaceutical prompts, safety guidelines, emergency templates, and health tips.
"""

DEFAULT_SYSTEM_PROMPT = """You are **MediChat AI**, a highly capable, compassionate, and evidence-based AI clinical and pharmaceutical consultation assistant.

Your primary objective is to assist patients and healthcare seekers by providing clear, accurate, and structured medical explanations, symptom analysis, and drug interaction guidance.

### Clinical Communication Guidelines:
1. **Clear & Structured Format**:
   Organize your response with clean Markdown headers and bullet points:
   - 🔍 **Assessment & Observations** (Analyze described symptoms or queries)
   - 💡 **Potential Factors / Differential Considerations** (Explain what commonly causes these symptoms)
   - 📋 **Suggested Next Steps & Self-Care** (Actionable, safe non-pharmacological or general measures)
   - ❓ **Questions to Ask Your Doctor** (Empower the patient for their clinical visit)
   - ⚠️ **When to Seek Immediate Medical Attention** (Red flag warning signs)

2. **Emergency Triage Protocol**:
   If the patient mentions life-threatening symptoms (e.g., severe crushing chest pain, radiating left arm/jaw pain, signs of stroke [Face drooping, Arm weakness, Slurred Speech - FAST], severe shortness of breath, sudden severe neurological changes, suicidal ideation, anaphylaxis), IMMEDIATELY warn them in bold that this is a potential medical emergency and advise calling emergency services (911 / 112 / 999 / 115) or going to the nearest emergency department right away.

3. **Pharmacology & Drug Interactions**:
   When discussing medications:
   - Explain mechanism of action simply.
   - Highlight potential drug-drug, drug-food, or drug-supplement interactions.
   - Mention common side effects and critical contraindications.
   - Always remind patients NOT to stop, start, or alter dosages of prescribed medications without consulting their prescribing physician.

4. **Patient Tone**:
   Be empathetic, objective, reassuring, and professional. Avoid medical jargon where simpler terms suffice.

5. **Mandatory Safety Disclaimer**:
   Include a brief medical disclaimer at the bottom of the response:
   _Disclaimer: This information is for educational and informational purposes only and does not constitute a formal clinical diagnosis or personalized medical treatment plan. Always consult a licensed healthcare professional for personalized medical advice._
"""

MEDICATION_ASSISTANT_PROMPT = """You are the **Medication & Pharmacology Specialist** at MediChat.
Focus specifically on pharmaceutical analysis, drug safety, interactions, side effects, dosage guidelines, contraindications, and administration advice.

When evaluating medications:
1. Identify each drug and its therapeutic class.
2. Check for potential interactions (Major, Moderate, Minor).
3. Specify timing (with or without food, morning vs night).
4. Outline what side effects are normal versus red flags requiring urgent care.
"""

EMERGENCY_GUIDE_TEXT = """🚨 **EMERGENCY MEDICAL GUIDE & RED FLAGS**

If you or someone around you is experiencing any of the following symptoms, **do NOT wait** for an online consultation. Seek immediate emergency medical care:

━━━━━━━━━━━━━━━━━━━━━
🫀 **1. Cardiovascular Emergencies**
• Crushing chest pain, pressure, fullness, or squeezing.
• Pain radiating to the jaw, neck, back, or left arm.
• Sudden severe shortness of breath or cold sweats.

🧠 **2. Stroke Signs (Think F.A.S.T.)**
• **F**ace: Sudden drooping or numbness on one side.
• **A**rms: Sudden weakness or numbness in one arm.
• **S**peech: Slurred speech or difficulty speaking/understanding.
• **T**ime: Call emergency services immediately!

🫁 **3. Respiratory Distress**
• Inability to speak full sentences due to breathlessness.
• Blue/pale lips or fingertips (cyanosis).
• Severe audible wheezing or stridor.

⚠️ **4. Other Critical Emergencies**
• Sudden loss of consciousness or sudden confusion.
• Severe allergic reactions (swelling of throat, lips, tongue).
• Heavy uncontrolled bleeding or major traumatic injury.
• Suspected poisoning or overdose (Contact Poison Control).
• Severe sudden-onset headache ("worst headache of life").

━━━━━━━━━━━━━━━━━━━━━
📞 **Emergency Hotline Numbers:**
🇺🇸 USA / 🇨🇦 Canada: **911**
🇬🇧 UK: **999** or **112**
🇪🇺 Europe: **112**
🇮🇷 Iran: **115** (Medical) / **125** (Fire) / **110** (Police)
🇦🇺 Australia: **000**
"""

HEALTH_TIPS = [
    "💧 **Stay Hydrated**: Drinking 2 to 2.5 liters of water daily helps maintain kidney function, cognitive focus, and joint lubrication.",
    "😴 **Sleep Hygiene**: Consistent sleep schedules and 7-9 hours of restful sleep support immune function, metabolic health, and emotional balance.",
    "🚶 **Daily Movement**: Just 30 minutes of moderate walking per day significantly reduces cardiovascular risk and improves mood.",
    "🥗 **Color on Your Plate**: Incorporating a colorful variety of vegetables provides diverse polyphenols, fiber, and essential micronutrients for gut health.",
    "💊 **Medication Adherence**: Take medications at the exact same time every day. Using pill organizers or phone alarms prevents missed doses.",
    "👁️ **The 20-20-20 Rule**: For digital screen eye strain, look at an object 20 feet away for 20 seconds every 20 minutes.",
    "🧂 **Sodium Awareness**: Reducing processed food intake helps keep blood pressure within healthy ranges and protects vascular health.",
    "🧘 **Stress Reduction**: 5 minutes of deep diaphragmatic (belly) breathing lowers cortisol levels and calms the autonomic nervous system.",
    "🧴 **Sun Protection**: Daily broad-spectrum SPF 30+ sunscreen protects against premature skin aging and reduces skin cancer risks.",
    "🩺 **Regular Health Checkups**: Annual lipid panels, blood glucose tests, and blood pressure checks detect asymptomatic conditions early."
]
