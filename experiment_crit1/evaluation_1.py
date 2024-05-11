import json
import openai
import os
import time
import pandas as pd

# GPT Params
MODEL = 'gpt-4-0613'#instead of gpt 4

TEMPERATURE = 0
COMPLETION_LEN = 2000
TOP_P = 1
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0

# Define paths to prompts
SYSTEM_PRINCIPLES_TEXT_FILE = 'prompts/system_1.txt'
QUESTION_TEXT_FILE = 'prompts/question_1.txt'
CRITERIA = 'prompts/principle_1.txt'

with open('../openai_config.json','r') as f:
    openai.api_key = json.load(f)['api_key']
    
# Completion functions
def request_gpt_magic(messages_input):
    try:
        return openai.ChatCompletion.create(
            model=MODEL,
            messages=messages_input,
            temperature=TEMPERATURE,
            max_tokens=COMPLETION_LEN,
            top_p=TOP_P,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY
        )
    except openai.error.RateLimitError:
        print('Rate limit exceeded. Waiting 60 seconds...')
        time.sleep(60)
        return request_gpt_magic(messages_input)


def get_completion(response):
    return response['choices'][0]['message']['content']


def evaluater(system_prompt, question):    
   
    #Prepare question to send in to gpt
    with open(QUESTION_TEXT_FILE,'r') as f:
        question_user_prompt = f.read()
    question_user_prompt = question_user_prompt.replace('{QUESTION}', json.dumps(question, sort_keys=False, indent=4))
    
    messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question_user_prompt}
            ]
     
    gpt_reason = get_completion(request_gpt_magic(messages))
    #print(gpt_answer)
    messages.append({'role': 'assistant', 'content': gpt_reason})

    with open(CRITERIA,'r') as f:
        question_user_prompt = f.read()
    messages.append({'role': 'user', 'content': question_user_prompt})
    gpt_answer = get_completion(request_gpt_magic(messages))
    messages.append({'role': 'assistant', 'content': gpt_answer})

    return messages, gpt_answer

# Make System Prompt
with open(SYSTEM_PRINCIPLES_TEXT_FILE,'r',encoding='UTF8') as f:
    SYSTEM_PROMPT = f.read()


in_directory = './mcqs/'
out_directory = './responses/'

df = pd.read_csv('gold_50_1.csv')
df['questionID'] = df['questionID'].astype(str)
df['auto_criteria_1'] = '100'

for file_name in os.listdir(in_directory):
    file_path = os.path.join(in_directory, file_name)
    if os.path.isfile(file_path) and file_name not in os.listdir(out_directory):
        
        with open(file_path, 'r') as file:
            mcq = json.load(file)
        
        gpt_output, mcq_eval = evaluater(SYSTEM_PROMPT,mcq)

        df.loc[df['questionID']==file_name.split('.')[0],'auto_criteria_1'] = mcq_eval
        with open(file_path.replace(in_directory,out_directory),'w',encoding="utf-8") as outfile: 
            json.dump(gpt_output, outfile, indent=4)
        
        


print(df)
df.to_csv('./evaluation.csv')