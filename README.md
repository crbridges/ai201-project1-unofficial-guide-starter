# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

I have selected elective options and ratings for my undergraduate CS program, Oregon State Universitie's post bacc degree. The online post bacc program is smaller and entirely online, so the data is hard to separate from in person classes for distance learners. 

---

## Document Sources


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

**Chunk size:** I split my data into individual replies to each Reddit post. I discarded the original post after revising my application.

**Overlap:** I chose not to any overlap. Each section of text is represented only once in the ChromaDB. I did strip all data related to reddit posts though, such as upvates, users, and dates.

**Why these choices fit your documents:** I chose to split based on posts, because the size of a post was extremely variable. There is no consistency or format between reddit posts, so I tokenized the data instead. I chose not to have any overlap, because there was no way the idea could be split between chunks by breaking things up by reply. I also chose to remove the original post from the embedded chunks, because they were getting outsized representation in the results. Instead I passed the original post in as metadata to give the reply context. 

**Final chunk count:** I ended up with 75 chunks, which correspond to the 75 reddit posts. Originally there were 10 additional chunks, but I opted to remove those.

---

## Embedding Model

**Model used:** I used the all-MiniLM-L6-v2 via sentence-transformers, because my data was largely text and context oriented. This model was able to embed it based meaning. 

**Production tradeoff reflection:**I would probably increase the chunking size by a lot. By splitting it into separate posts, you lose a lot of context, since all of the posts are really related to the thread. Since the chunks would also be much larger, I would need a faster model to parse such a large amount of text.


---

## Grounded Generation


**System prompt grounding instruction:**

The query tells the model it can only use the student reviews I give it and no outside knowledge. If the reviews don't cover the question, it says "The student reviews I have don't cover that" instead of guessing. It also says that when reviews disagree, call it mixed instead of picking one as fact. I feed it the top 5 chunks as numbered blocks (thread question + reply + source URL).

**How source attribution is surfaced in the response:**

Each chunk carries its thread URL, so after the answer I show the URLs of the retrieved chunks as a clickable "Sources" list in the Gradio app. Claude code also decieded to add a dropdown with the raw chunks and their similarity distances so you can check the answer against what students said.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which elective do students recommend as most useful for landing a software engineering job? | 372 Networking and 493 Cloud | Said no single elective stands out, named Networking (372) as useful on the job and Mobile (492). Missed Cloud entirely. | Partially relevant | Partially accurate |
| 2 | Which electives do students describe as the easiest or lightest workload? | Parallel Programming and Open Source Software | Named CS 352 Usability and CS 391 Social/Ethical Issues as easiest (both are genuinely called easy in the data). Did not surface Parallel or Open Source. | Partially relevant | Partially accurate |
| 3 | Which electives are considered the hardest? | Cryptogrpahy, Into to Networking, and Operating Systems II | Correctly flagged Cryptography as hard and honestly hedged that the reviews don't directly compare difficulty. Missed OS2 and Networking. | Partially relevant | Partially accurate |
| 4 | What do students say about CS493 Cloud Systems? | It has mixed reviews, with most students saying positive things. | Gave a mixed-but-mostly-positive summary: "excellent but misleadingly named," teaches RESTful APIs, with one "waste of money" dissent. Matched expected closely. | Relevant | Accurate |
| 5 | Which electives do student say are the most fun? | 450 Graphics and 474 Parallel Programming | Named Parallel Programming (correct) and Cryptography, and noted an unspecified "super fun" class. Missed Graphics (450) entirely. | Partially relevant | Partially accurate |


**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis


**Question that failed:** "Which electives are the most fun?"

**What the system returned:** It named Parallel Programming (which is correct) and Cryptography(which is wrong), and mentioned an unspecified super fun class.

**Root cause (tied to a specific pipeline stage):** The fragment is a retrieval failure caused by my chunking choice. Because I split by reply, responses to responses have no context and are sometimes unrelated to the original post. The cryptography incorrect choice was caused by a lack of data I think. One person really like it, but most people don't. They had a very strong positive reply though.

**What you would change to fix it:** For the unspecified fragment, I would filter out the tiny fragment chunks (set a minimum length), since those context-free one-liners barely mean anything on their own. And for the incorrect choice, I think pulling an unlimited number of chunks as long as they are a high match would help. That would give a relative count of how many people actually liked each class instead of relying on only the strongest opinionated replies.
---

## Spec Reflection

**One way the spec helped you during implementation:**
The spec helped me to plan out the isntructions to give to claude code in order to build the application correctly the first time. I knew what to expect as input and output of each step, and this allowed claude to more or less build everything flawlessly on the first attempt. Most of the issues I had were due to checking the results and realizing my data wasn't good enough. 

**One way your implementation diverged from the spec, and why:**
I ended up redoing how my chunking was working. Originally I had everything just split into posts and replies and all dumped into the database as chunks, but without context most of the replies are meaningless. I had to go back and add the posts into the metadata for each reply in order to give the llm some context on what the person was talking about. 

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My raw Reddit copy-paste text files and my chunking plan from planning.md (split by reply, use === as a delimiter, and keep each thread's URL).
- *What it produced:* A Python script (clean_documents.py) that stripped the Reddit junk (upvotes, usernames, dates, ads) and a load_documents() function that returned the chunks.
- *What I changed or overrode:* I directed it to attach the original post to each reply as context so short replies still made sense, but to NOT embed the original post so it wouldn't dilute the vectors. I also had it drop leftover "Read more" lines it missed.

**Instance 2**

- *What I gave the AI:* I asked it to embed my chunks into ChromaDB with all-MiniLM-L6-v2 and build the retrieval function.
- *What it produced:* embed_store.py with the index and a retrieve() function, plus a test query to check it worked.
- *What I changed or overrode:* The first test showed the original-post questions out-ranking the actual answers in retrieval, so I decided to drop the original posts out of the embeddings entirely (going from 85 to 75 chunks), which fixed it.
