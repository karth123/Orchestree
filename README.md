Sure! Here’s the full README.md file with everything included — your updated content, correct API key name, GNU AGPL license mention, and a .gitignore reference as well:

⸻


🌳 Orchestree
=============

Create beautiful, editable cloud architecture diagrams from natural language.

Orchestree is a fully open-source Streamlit application that lets you describe your cloud architecture in plain English and instantly generate editable SVG diagrams—perfect for platforms like Canva, Figma, Adobe Illustrator, or any vector-editing tool.

---

✨ Features
----------

- 🧠 **Natural Language to Diagram**: Describe your architecture like “An EC2 in a VPC with an RDS DB” and get a clean visual.
- 🎨 **SVG Output**: Produces high-quality SVG files ready for further customization.
- ☁️ **Thousands of Cloud Icons**: Supports AWS, Azure, GCP, Oracle, IBM Cloud, and Alibaba Cloud.
- 🧪 **Streamlit-Powered UI**: Clean and interactive frontend—no installations, no learning curve.
- 🔓 **100% Open Source**: Inspired by “diagrams to code”, Orchestree fills the gap left by tools like Eraser, with a free and open alternative.

---

🚀 Quick Start
-------------

### 1. Clone the Repository

```bash
git clone https://github.com/karth123/orchestree.git
cd orchestree

2. Set Up Environment

Python version: 3.9 is required

python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Set Up Your Gemini API Key

Orchestree uses Google Gemini to understand natural language inputs and convert them into architecture diagrams.

How to Get the Key:
	1.	Visit Google AI Studio and log in.
	2.	Click your profile icon → API key → Create API Key.
	3.	Copy the generated key.

Save the Key:

Create or edit the file .streamlit/secrets.toml and add:

google_api_key = "your-google-api-key-here"

Make sure the file path is:

orchestree/.streamlit/secrets.toml

4. Run the App

streamlit run app.py


⸻

🛠 How to Use
	1.	Launch the app — it will open in your browser.
	2.	Test with a demo prompt


⸻

🌱 Why “Orchestree”?

Because great systems grow from simple, declarative ideas—just like trees from seeds.

⸻

📦 Tech Stack
	•	Python 3.9
	•	Streamlit
	•	Google Gemini API
	•	Custom SVG generation
	•	Icon libraries from 6+ cloud providers

⸻

📚 Inspired By
	•	🛠 diagrams – Diagrams as code.
	•	🖋 Eraser – A proprietary tool that inspired a better open source experience.

⸻


⸻

🤝 Contribute

We’d love help with:
	•	Icon contributions
	•	Enhanced parsing logic
	•	Better UI layout
	•	New cloud provider support

Open an issue or PR to get started!

⸻

🪪 License

GNU Affero General Public License v3.0 (AGPL-3.0)
See LICENSE file for full terms.

⸻

💌 Contact

Open an issue or start a discussion. We’d love to hear from you!