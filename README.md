# GICdemo

![Screenshot 2025-02-21 103851](https://github.com/user-attachments/assets/ced89e1d-cae8-4556-960b-cb51b786b9bf)

This is a simple prototype showing an easier-to-user government information center (GIC, Sri Lanka) using a new AI-assisted content review policy and RAG search on top. Various procedures from the GIC have been rewritten to be clearer and are available in the docs folder (their old version are available in the originaldocs folder). It also contains some idealized guidelines (see guidelines folder) that are written as a general standard we should adhere to. These guidelines do not match current processes. The content guidelines were used to turn the originaldocs into docs. 

All in all, we have here
- 623 base documents (docs)
- 3 content guidelines (guidelines - one for how to write, one for visual design, and the other for the management and maintenance of information)
- 624 original documents (originaldocs) - inbound
- 
I'm defaulting to English here, because this stuff is easier to prototype in English.

Each doc not only contains information, but metadata as follows.

![Screenshot 2025-02-20 131336](https://github.com/user-attachments/assets/2d8791da-a062-4899-9f43-32e1debed0e2)

On top of these is a simple HTML file that access a bunch of markdown locally and uses Anthropic's Claude to present a basic Retrieval Augmented Generation (RAG) for government information; for comparison purposes, I also present here the simple search variant that does not need any LLM activity to function. 

![Screenshot 2025-02-21 104129](https://github.com/user-attachments/assets/e5d8cf79-e99e-496f-8132-24109a72e9ab)

This is only meant for prototype / showcase purposes. This information is not totally vetted for accuracy, nor is this a complete setup of any kind. To use this code, you'll need to download the folder, and add your Claude API key in the "GIC - llm search.html" file. Look for the words "API-key-here" and replace them with your Anthropic key. 

This repo also contains content guidelines, meant to help shape the large amounts of existing, scattershot and variable-quality information into consistent and useful information from a citizen's perspective. The ideal flow is something as follows:

![image](https://github.com/user-attachments/assets/a4e0ff41-1941-4b44-963a-402431c2edd9)

The python scripts (rewriter_lite.py and validator.py) are first steps in this rewriter->validate chain. Rewriter_lite was used to write the content in the docs folder. Both scripts need guidelines.txt (the distilled instructions for rewriting and content quality), a text file containing your api key, and appropritate input and output folders - check the code for the exact values needed. Here's what the output from the rewriter looks like for now:

![image](https://github.com/user-attachments/assets/dab42ad2-d3a9-443e-bc75-ee8a7dea886a)


And it's run through the validator before upload. 


![image](https://github.com/user-attachments/assets/6126896a-5a35-445b-bfd5-22645a652c15)

Ideally this stuff becomes part of a better-designed, actual deployment down the line. Right now, these are just proofs of concept.


