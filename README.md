# GICdemo

This is a simple prototype showing an easier-to-user government information center (GIC, Sri Lanka) using a new AI-assisted content review policy and RAG search on top. 

It distills the procedures of various government instutes into simple guides. As befits a demo, it's a simple HTML file that access a bunch of markdown locally. Uses Anthropic's Claude; for comparison purposes, I also present here the simple search variant that does not need any LLM activity to function. 

![Screenshot 2025-02-20 131218](https://github.com/user-attachments/assets/a579eb5b-c636-4819-8cc6-c78a134a051c)


Update: now responds to natural language questions.


![Screenshot 2025-02-21 103851](https://github.com/user-attachments/assets/ced89e1d-cae8-4556-960b-cb51b786b9bf)


Both how and why type questions are important: 


![Screenshot 2025-02-21 104129](https://github.com/user-attachments/assets/e5d8cf79-e99e-496f-8132-24109a72e9ab)


Each guide not only contains information, but document metadata as follows.


![Screenshot 2025-02-20 131336](https://github.com/user-attachments/assets/2d8791da-a062-4899-9f43-32e1debed0e2)

This is only meant for prototype / showcase purposes. This information is not vetted for accuracy, nor is this a complete setup of any kind. To use this code, you'll need to download the folder, and add your Claude API key in the "GIC - llm search.html" file. Look for the words "API-key-here" and replace them with your Anthropic key. 
