########  GENERAL APP INFORMATION  ##############

APP_TITLE = "Writing Your Grant Proposal Introduction"
APP_INTRO = """In this interactive writing assessment, you will write an introduction for your real or hypothetical grant proposal. 

You will receive immediate feedback on your introduction. The feedback is generated by an AI and based on a rubric created by the course instructor. 

You will have a chance to revise your introduction and then receive another round of feedback.

As with all feedback, but especially AI-generated feedback, you should weigh the feedback with your own instincts about your writing. 
"""

APP_HOW_IT_WORKS = """
            This is an **AI-Tutored Rubric exercise** that acts as a tutor guiding a student through a shared asset, like an article. It uses the OpenAI Assistants API with GPT-4. The **questions and rubric** are defined by a **faculty**. The **feedback and the score** are generarated by the **AI**. 

It can:

1. provide feedback on a student's answers to questions about an asset
2. roughly "score" a student to determine if they can move on to the next section.  

Scoring is based on a faculty-defined rubric on the backend. These rubrics can be simple (i.e. "full points if the student gives a thoughtful answer") or specific with different criteria and point thresholds. The faculty also defines a minimum pass threshold for each question. The threshold could be as low as zero points to pass any answer, or it could be higher. 

Using AI to provide feedback and score like this is a very experimental process. Some things to note: 

 - AIs make mistakes. Users are encourage to skip a question if the AI is not understanding them or giving good feedback. 
 - The AI might say things that it can't do, like "Ask me anything about the article". I presume further refinement can reduce these kinds of responses. 
 - Scoring is highly experimental. At this point, it should mainly be used to gauge if a user gave an approximately close answer to what the rubric suggests. It is not recommended to show the user the numeric score. 

 """

SHARED_ASSET = ""

COMPLETION_MESSAGE = "You've reached the end! I hope you learned something!"
COMPLETION_CELEBRATION = False

SCORING_DEBUG_MODE = True

 ####### PHASES INFORMATION #########

PHASES = {
    "org_name": {
        "type": "text_input",
        "label": """What is the name of your organization?""",
        "instructions": """The user will provide you the name of a real or hypothetical organization. Provide exactly this response to the user. 'Hi! I'm an AI programmed to provide feedback on your grant proposal. Let's do a draft-refine-submit exercise where you provide me your proposal introduction for [the name of the company the user provided] and I'll give you some feedback. Then, you'll incorporate that feedback into a final draft and submit. '""",
        "scored": False,
    },
    "first_draft": {
        "type": "text_area",
        "height": 300,
        "label": """Please write your first draft of your proposal introduction.""",
        "button_label": "Submit",
        "value": "Founded in 1981, we now operate 38 stores in six states, including the bookstore at the Anasazi Heritage Center. SNCHA supports the educational, interpretive and research programs of three federal agencies. We also publish The Escalante Community: Where did they go? Why did they leave?, and The Dolores River Guide.  [Mission] The Heritage Center opened to the public in 1988 and averages 40,000+ visitors each year.  SNCHA and the AHC received two previous Colorado State Historical Fund grants totaling more than $135,000, committed to the Lowry CD-rom People in the Past Project. Historical Society product reviews for the project were excellent.",
        "scored_phase": True,
        "instructions": """ Provide the user with feedback on their grant proposal introduction. Do not rewrite their introduction. Given the user's proposal, prioritize 1-3 of the following areas to provide feedback and recommendations for improvement, and then provide those feedback and recommendations: 
        1. Does it provide an effective overview of the organization?
        2. Does it effectively convey who the organization is and what it does?
        3. Does this organization come across as capable of getting things done?
        4. Does the introduction adequately detail whom the organization helps and the impact of their work?
        5. Do the testimonials provide insight into the reputation and impact of the organization?

        """,
        "rubric": """
                1. Organization Introduction
                    2 points - The response introduces the organization and its purpose
                    1 point - The response introduces the organization OR its purpose, but not both. 
                    0 points - The response does not introduce the organization or explain its purpose
                2. Credibility
                    2 points - The response uses one of more compelling points that convey credibility
                    1 point - The response uses one or more points to convey credibility, but they are not compelling
                    0 points - The response does not convey credibility of the organization. 
                3. Accomplishments and testimonials
                    1 point - The response includes a testimonial and or accomplishment that demonstrates success. 
                    0 points - The response does not include any testimonials or accomplishments
        """,
        "minimum_score": 2,
        "user_input": "",
        "ai_response": "",
        "allow_skip": True
    },
    "final_draft": {
       "type": "text_area",
       "height": 300,
       "label": "Now, please attempt to incorporate the relevant feedback and write a second draft fo your introduction.",
       "value":"""Founded in 1981, SNCHA (Southern New Chelsea Housing Association) supports the educational, interpretive and research programs of three federal agencies. We now operate 38 stores in six states, including the bookstore at the Anasazi Heritage Center. We also publish The Escalante Community: Where did they go? Why did they leave?, and The Dolores River Guide.  

The Heritage Center opened to the public in 1988 and averages 40,000+ visitors each year.  SNCHA and the AHC received two previous Colorado State Historical Fund grants totaling more than $135,000, committed to the Lowry CD-rom People in the Past Project. The project has been praised by users and donors alike for being "the most authentic Heritage Center in the country". """,
       "instructions": """Given the user's second draft of their proposal, provide feedback on how well they've incorporated your suggestions. If the student has not made any changes to their original submission in this thread, then admonish them for not following instructions. If the student has made a good faith effort to improve their original submission, then encourage them.
        """,   
       "scored_phase": True,
        "rubric": """
                1. Organization Introduction
                    2 points - The response introduces the organization and its purpose
                    1 point - The response introduces the organization OR its purpose, but not both. 
                    0 points - The response does not introduce the organization or explain its purpose
                2. Credibility
                    2 points - The response uses one of more compelling points that convey credibility
                    1 point - The response uses one or more points to convey credibility, but they are not compelling
                    0 points - The response does not convey credibility of the organization. 
                3. Accomplishments and testimonials
                    1 point - The response includes a testimonial and or accomplishment that demonstrates success. 
                    0 points - The response does not include any testimonials or accomplishments
        """,
       "minimum_score": 4,
       "user_input": "",
       "ai_response": "",
       "allow_skip": True
    },
    # "reflect": {
    #    "type": "text_area",
    #    "height": 100,
    #    "label": "Now, please reflect on this exercise",
    #    "button_label": "Finish",
    #    "value":"I think I did well on this exercise and I'm glad that I got immediate feedback. ",
    #    "instructions": """The user is reflecting on their experience. Acknowlege their reflection. 
    #     """,   
    #    "scored_phase": True,
    #    "rubric": """
    #            1. Correctness
    #                1 point - The user has added an appropriate reflection
    #                0 points - The user has not added an appropriate reflection
    #            """,
    #    "minimum_score": 1,
    #    "user_input": "",
    #    "ai_response": "",
    #    "allow_skip": True

    # #Add more steps as needed
    # }
}

######## AI CONFIGURATION #############
OPENAI_MODEL = "gpt-4-turbo"
ASSISTANT_ID = "asst_2Ax6jYO4FGPio7DvHGkjZhU2"
ASSISTANT_THREAD = ""
FREQUENCY_PENALTY = 0
MAX_TOKENS = 1000
PRESENCE_PENALTY = 0
TEMPERATURE = 1
TOP_P = 1

########## AI ASSISTANT CONFIGURATION #######
ASSISTANT_NAME = "Grant Reviewer"
ASSISTANT_INSTRUCTIONS = """
You are a grant reviewer, for a hypothetical grant organization like the NSA. It is your job to review and provide feedback for grant funding opportunities.
You are tough but fair. You find opportunities to provide critical feedback, but you provide evidence from the user's text for any critical feedback you offer. """

