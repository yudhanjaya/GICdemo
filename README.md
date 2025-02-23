# GICdemo

![Screenshot 2025-02-21 103851](https://github.com/user-attachments/assets/ced89e1d-cae8-4556-960b-cb51b786b9bf)

This is a simple prototype showing an easier-to-user government information center (GIC, Sri Lanka) using a new AI-assisted content review policy and RAG search on top. Various procedures from the GIC have been rewritten to be clearer and are available in the docs folder (their old version are available in the originaldocs folder). 

It also contains some idealized guidelines (see guidelines folder) that are written as a general standard we should adhere to. These guidelines do not match current processes. The content guidelines were used to turn the originaldocs into docs. 

Each guide not only contains information, but document metadata as follows.

![Screenshot 2025-02-20 131336](https://github.com/user-attachments/assets/2d8791da-a062-4899-9f43-32e1debed0e2)


On top of these is a simple HTML file that access a bunch of markdown locally and uses Anthropic's Claude to present a basic Retrieval Augmented Generation (RAG) for government information; for comparison purposes, I also present here the simple search variant that does not need any LLM activity to function. 

![Screenshot 2025-02-21 104129](https://github.com/user-attachments/assets/e5d8cf79-e99e-496f-8132-24109a72e9ab)

This is only meant for prototype / showcase purposes. This information is not totally vetted for accuracy, nor is this a complete setup of any kind. To use this code, you'll need to download the folder, and add your Claude API key in the "GIC - llm search.html" file. Look for the words "API-key-here" and replace them with your Anthropic key. 

This repo also contains content guidelines, meant to help shape the large amounts of existing, scattershot and variable-quality information into consistent and useful information from a citizen's perspective. The ideal flow is something as follows:

![image](https://github.com/user-attachments/assets/a4e0ff41-1941-4b44-963a-402431c2edd9)
