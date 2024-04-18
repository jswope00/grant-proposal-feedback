import openai
import os
from dotenv import find_dotenv, load_dotenv
import json
import re
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from contextlib import nullcontext
from openai import OpenAI, AssistantEventHandler

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
       "value":"Founded in 1981, we now operate 38 stores in six states, including the bookstore at the Anasazi Heritage Center. SNCHA supports the educational, interpretive and research programs of three federal agencies. We also publish The Escalante Community: Where did they go? Why did they leave?, and The Dolores River Guide.  [Mission] The Heritage Center opened to the public in 1988 and averages 40,000+ visitors each year.  SNCHA and the AHC received two previous Colorado State Historical Fund grants totaling more than $135,000, committed to the Lowry CD-rom People in the Past Project. Historical Society product reviews for the project were excellent.",
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


load_dotenv()
client = openai.OpenAI()

function_map = {
    "text_input": st.text_input,
    "text_area": st.text_area,
    "warning": st.warning,
    "button": st.button,
    "radio": st.radio
}

user_input = {}

def build_field(i, phases_dict):

    phase_name = list(phases_dict.keys())[i]
    phase_dict = list(phases_dict.values())[i]
    field_type = phase_dict.get("type","")
    field_label = phase_dict.get("label","")
    field_body = phase_dict.get("body","")
    field_value = phase_dict.get("value","")
    field_max_chars = phase_dict.get("max_chars",None)
    field_help = phase_dict.get("help","")
    field_on_click = phase_dict.get("on_click",None)
    field_options = phase_dict.get("options","")
    field_horizontal = phase_dict.get("horizontal",False)
    field_height = phase_dict.get("height",None)

    kwargs = {}
    if field_label:
        kwargs['label'] = field_label
    if field_body:
        kwargs['body'] = field_body
    if field_value:
        kwargs['value'] = field_value
    if field_options:
        kwargs['options'] = field_options
    if field_max_chars:
        kwargs['max_chars'] = field_max_chars
    if field_help:
        kwargs['help'] = field_help
    if field_on_click:
        kwargs['on_click'] = field_on_click
    if field_horizontal:
        kwargs['horizontal'] = field_horizontal
    if field_height:
        kwargs['height'] = field_height
 
    key = f"{phase_name}_phase_status"
    #print("Session State Key: " + key)
    #print("Phase Status: " + str(st.session_state[key]))
    #If the user has already answered this question:
    if key in st.session_state and st.session_state[key]:
        #Write their answer
        kwargs['value'] = st.session_state[f"{phase_name}_user_input"]
        #Disable the field
        kwargs['disabled'] = True

    my_input_function = function_map[field_type]

    with stylable_container(
        key="large_label",
        css_styles="""
            label p {
                font-weight: bold;
                font-size: 28px;
            }
            """,
    ):

        user_input[phase_name] = my_input_function(**kwargs)


class AssistantManager:
    assistant_id = ASSISTANT_ID
    thread_id = ASSISTANT_THREAD
    
    def __init__(self, model: str = OPENAI_MODEL):
        self.client = client
        self.model = OPENAI_MODEL
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssisID:::: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            if st.session_state.thread_obj:
                print(f"Grabbing existing thread...")
                thread_obj = st.session_state.thread_obj
            else:
                print(f"Creating and saving new thread")
                thread_obj = self.client.beta.threads.create()
                st.session_state.thread_obj = thread_obj

            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")
        else:
            print(f"A thread already exists: {self.thread.id}")

    # Create a MESSAGE within our thread. Indicate if the message is from the user or assistant.
    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, 
                role=role, 
                content=content
            )

    # Create a RUN that sends the thread (with our messages) to the ASSISTANT
    def run_assistant(self, instructions, current_phase, scoring_run=False, temperature = TEMPERATURE, response_format="auto"):
        if self.thread and self.assistant:

            # Create a RUN that sends the thread (with our messages) to the ASSISTANT
            if not scoring_run or (scoring_run and SCORING_DEBUG_MODE):
                res_box = st.info(body="", icon="🤖")
            report = []

            stream = self.client.beta.threads.runs.create(
                assistant_id=self.assistant.id,
                thread_id=self.thread.id,
                instructions=instructions,
                temperature=temperature,
                stream=True
                )

            context_manager = st.spinner('Checking Score...') if scoring_run else nullcontext()

            with context_manager:
                for event in stream:
                    if event.data.object == "thread.message.delta":
                        #Iterate over content in the delta
                        for content in event.data.delta.content:
                            if content.type == 'text':
                                #Print the value field from text deltas
                                report.append(content.text.value)
                                result = "".join(report).strip()
                                if scoring_run == False:
                                    res_box.info(body=f'{result}', icon="🤖")
                                if scoring_run and SCORING_DEBUG_MODE:
                                    res_box.info(body=f'SCORE (DEBUG MODE): {result}', icon="🤖")


            if scoring_run == False:
                st_store(result,current_phase,"ai_response")
            else:
                st_store(result,current_phase,"ai_result")
                score = extract_score(result)
                st_store(score,current_phase,"ai_score")




def st_store(input, phase_name, phase_key):
    key = f"{phase_name}_{phase_key}"
    if key not in st.session_state:
        st.session_state[key] = input
        

def build_scoring_instructions(rubric):
    scoring_instructions = """Please score the user's previous response based on the following rubric: \n """
    scoring_instructions += rubric
    scoring_instructions += """\n\nPlease output your response as JSON, using this format: { "[criteria 1]": "[score 1]", "[criteria 2]": "[score 2]", "total": "[total score]" }"""
    return scoring_instructions

def extract_score(text):
    # Define the regular expression pattern
    #regex has been modified to grab the total value whether or not it is returned inside double quotes. The AI seems to fluctuate between using quotes around values and not. 
    pattern = r'"total":\s*"?(\d+)"?'
    
    # Use regex to find the score pattern in the text
    match = re.search(pattern, text)
    
    # If a match is found, return the score, otherwise return None
    if match:
        return int(match.group(1))
    else:
        return 0


def check_score(PHASE_NAME):
    score = st.session_state[f"{PHASE_NAME}_ai_score"]
    try:
        if score >= PHASES[PHASE_NAME]["minimum_score"]:
            st.session_state[f"{PHASE_NAME}_phase_status"] = True
            return True
        else:
            st.session_state[f"{PHASE_NAME}_phase_status"] = False
            return False
    except:
        st.session_state[f"{PHASE_NAME}_phase_status"] = False
        return False

def celebration():
    rain(
        emoji="🥳",
        font_size=54,
        falling_speed=5,
        animation_length=1,
    )



def main():
    global ASSISTANT_ID

    if 'current_question_index' not in st.session_state:
        st.session_state.thread_obj = []

    st.title(APP_TITLE)
    st.markdown(APP_INTRO)

    if APP_HOW_IT_WORKS:
        with st.expander("Learn how this works", expanded=False):
            st.markdown(APP_HOW_IT_WORKS)


    if SHARED_ASSET:
        # Download button for the PDF
        with open(SHARED_ASSET["path"], "rb") as asset_file:
            st.download_button(label=SHARED_ASSET["button_text"],
                data=asset_file,
                file_name=SHARED_ASSET["name"],
                mime="application/octet-stream")

    #Create the assistant one time. Only if the Assistant ID is not found, create a new one. 
    openai_assistant = AssistantManager()
    
    #Run the create_assistant. It only creates a new assistant if one is not found. 
    openai_assistant.create_assistant(
        name=ASSISTANT_NAME,
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=""
    )

    #Create a thread, or retrieve the existing thread if it exists in local Storage. 
    openai_assistant.create_thread()
    
    i=0

    #Create a variable for the current phase, starting at 0
    if 'CURRENT_PHASE' not in st.session_state:
        st.session_state['CURRENT_PHASE'] = 0


    #Loop until you reach the currently active phase. 
    while  i <= st.session_state['CURRENT_PHASE']:
        submit_button = False
        skip_button = False
        final_phase_name = list(PHASES.keys())[-1]
        final_key = f"{final_phase_name}_ai_response"



        # Build the field, according to the values in the PHASES dictionary
        build_field(i, PHASES)
        #Store the Name of the Phase and the values for that Phase
        PHASE_NAME = list(PHASES.keys())[i]
        PHASE_DICT = list(PHASES.values())[i]

        key = f"{PHASE_NAME}_phase_status"
        if key not in st.session_state:
            st.session_state[key] = False
        #If the phase isn't passed and it isn't a recap of the final phase, then give the user a submit button
        if st.session_state[key] != True and final_key not in st.session_state:
                with st.container(border=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.button(label=PHASE_DICT.get("button_label","Submit"), type="primary", key="submit "+str(i))
                    with col2:
                        skip_button = st.button(label="Skip Question", key="skip " + str(i))

        #If the phase has user input:
        key = f"{PHASE_NAME}_user_input"
        if key in st.session_state:
            # Then try to print the stored AI Response
            key = f"{PHASE_NAME}_ai_response"
            #If the AI has responded:
            if key in st.session_state:
                #Then print the stored AI Response
                st.info(st.session_state[key], icon ="🤖")
            key = f"{PHASE_NAME}_ai_result"
            #If we are showing a score:
            if key in st.session_state and SCORING_DEBUG_MODE == True:
                #Then print the stored AI Response
                st.info(st.session_state[key], icon ="🤖")
            #key = f"{PHASE_NAME}_phase_status"
            #if key in st.session_state:
            #   st.warning(st.session_state[key])

        
        #key = f"{PHASE_NAME}_phase_status"
        #if key not in st.session_state:
    #       st.session_state[key] = False
        #st.write("Phase Status: " + str(st.session_state[key]))
        #if st.session_state[key] != True:
        #else:
                #If it is a user input field and it has not been answered, then add a submit button. 
        ##  with st.container(border=False):
        #       col1, col2 = st.columns(2)
    #           with col1:
        #           submit_button = st.button(label=PHASE_DICT.get("button_label","Submit"), type="primary", key="submit "+str(i))
        #       with col2:
        #           skip_button = st.button(label="Skip Question", key="skip " + str(i))
        if submit_button:
            #Add INSTRUCTIONS message to the thread
            openai_assistant.add_message_to_thread(
                role="assistant", 
                content=PHASE_DICT.get("instructions","")
                )
            #Store the users input in a session variable
            st_store(user_input[PHASE_NAME], PHASE_NAME, "user_input")
            #Add USER MESSAGE to the thread
            openai_assistant.add_message_to_thread(
                role="user", 
                content=user_input[PHASE_NAME]
                )
            #Currently, all instructions are handled in the system prompts, so no need to add additional instructions here. 
            instructions = ""
            #Run the thread
            openai_assistant.run_assistant(instructions, PHASE_NAME)
            
            if PHASE_DICT.get("scored_phase","") == True:
                if "rubric" in PHASE_DICT:
                    scoring_instructions = build_scoring_instructions(PHASE_DICT["rubric"])
                    openai_assistant.add_message_to_thread(
                    role="assistant", 
                    content=scoring_instructions,
                    )
                    openai_assistant.run_assistant(instructions, PHASE_NAME, True, temperature=.2,response_format="json")
                    if check_score(PHASE_NAME):
                        st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES)-1)
                    else:
                        st.warning("You haven't passed. Please try again.")
                else:
                    st.error('You need to include a rubric for a scored phase', icon="🚨")
            else: 
                st.session_state[f"{PHASE_NAME}_phase_status"] = True
                st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES)-1)

            #Rerun Streamlit to refresh the page
            st.rerun()

        if skip_button:
            st_store(user_input[PHASE_NAME], PHASE_NAME, "user_input")
            st.session_state[f"{PHASE_NAME}_ai_response"] = "This phase was skipped."
            st.session_state[f"{PHASE_NAME}_phase_status"] = True
            st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES)-1)
            st.rerun()

        if final_key in st.session_state and i == st.session_state['CURRENT_PHASE']:
            st.success(COMPLETION_MESSAGE)
            if COMPLETION_CELEBRATION:
                celebration()

        #Increment i, but never more than the number of possible phases
        i = min(i + 1, len(PHASES))









if __name__ == "__main__":
    main()