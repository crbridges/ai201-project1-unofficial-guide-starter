# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I have selected elective options and ratings for my undergraduate CS program, Oregon State Universitie's post bacc degree. The online post bacc program is smaller and entirely online, so the data is hard to separate from in person classes for distance learners. 

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | A post requesting the best elective choices | https://www.reddit.com/r/OSUOnlineCS/comments/1tbdq3m/what_electives_do_you_reccomend/ |
| 2 | Reddit | A post requesting the best elective choices |https://www.reddit.com/r/OSUOnlineCS/comments/135yej9/best_electives/ |
| 3 | Reddit | A post asking for the easiest electives to take | https://www.reddit.com/r/OSUOnlineCS/comments/scythe/easy_electives_to_finish_off_the_program/ |
| 4 | Reddit | A post asking for the best summer elective | https://www.reddit.com/r/OSUOnlineCS/comments/1362sm5/need_one_more_elective_to_take_in_the_summer_term/ |
| 5 | Reddit | A post asking for fun electives| https://www.reddit.com/r/OSUOnlineCS/comments/1hi5c5x/what_are_some_interesting_and_fun_electives_you/ |
| 6 | Reddit | A post asking for elective reviews | https://www.reddit.com/r/OSUOnlineCS/comments/muc6r7/feedback_on_electives/ |
| 7 | Reddit | A post asking for elective recommendations | https://www.reddit.com/r/OSUOnlineCS/comments/1hxg5h8/elective_recommendations/ |
| 8 | Reddit | A post asking for the most fulfilling electives | https://www.reddit.com/r/OSUOnlineCS/comments/jro3a1/what_are_the_bestmost_fullfilling_electives_that/ |
| 9 | Reddit | A post asking for recommended electives | https://www.reddit.com/r/OSUOnlineCS/comments/1n5u40a/recommended_electives/ |
| 10 | Reddit | A post asking for the best electives to be job ready | https://www.reddit.com/r/OSUOnlineCS/comments/18nu07r/what_electives_were_most_useful_in_your_job_search/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** I will chunk my data in tokens split up by reddit post. I will use a delimiter between posts to separate them all individually.
 
**Overlap:** I won't have any overlap.

**Reasoning:**  Because I am splitting by post, all data should be split into complete thoughts. There shouldn't be an chance of ideas getting split between retrievals.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** I will use the all-MiniLM-L6-v2 via sentence-transformers and the llama-3.3-70b-versatile LLM model.

**Top-k:** I will take the top 5 chunks per query.

**Production tradeoff reflection:** I would probably increase the chunking size by a lot. By splitting it into separate posts, you lose a lot of context, since all of the posts are really related to the thread. Since the chunks would also be much larger, I would need a faster model to parse such a large amount of text.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which elective do students recommend as most useful for landing a software engineering job? | 372 Networking and 493 Cloud |
| 2 | Which electives do students describe as the easiest or lightest workload? | Parallel Programming and Open Source Software|
| 3 | Which electives are considered the hardest? |  Cryptogrpahy, Into to Networking, and Operating Systems II|
| 4 | What do students say about CS493 Cloud Systems? | It has mixed reviews, with most students saying positive things. |
| 5 | Which electives do student say are the most fun? | 450 Graphics and 474 Parallel Programming |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The documents are going to be very noisy and inconsistent. Many posts above the same class have conflicting opinions, and by limiting the top k returns to 5 there could be a poor sampling that skews the repsonse. 

2. Some classes are rarely taken, so there could be a lack of information about those classes. This could cause the top k chunks to actually contain information about the wrong classes.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     Ingestion
     (Python to read data from text files into a list)
          |
     Chunking
     (Split files into posts)
          |
     Embedding + Vector Store
     (all-MiniLM-L6-v2 via sentence-transformers -> ChromaDB)
          |
     Retrieval
     (ChromaDB similarity search, top-k = 5)
          |
     Generation
     (Groq / Llama 3.3 70B, grounded prompt + cited sources -> Gradio UI)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will ask claude code to load all files into memory with a function named load_documents(). They will be split into sections for each reply to the comment thread separated at the delimited '==='. The function will return a list of dictionary replies with the url and text for each.

**Milestone 4 — Embedding and retrieval:**
I will ask claude code to create a function embed_data() that stores all of the chunks into the ChromaDB. 
I will ask claude code to write a function to retrieve the top 5 nearest data points by embedding the user request.

**Milestone 5 — Generation and interface:**
I will ask claude code to generate a function called generate_answer() that calls the llm to generate a response based on only on the top-k results. If there is no good answer, then the model should say so. If there is, the source should be sited. 

I will ask claude code to generate a basic interface with a question bar for the user to enter a query using Gradio.