import json
import anthropic
import os
import time
import pandas as pd


# GPT Params
MODEL = 'claude-3-opus-20240229'#instead of gpt 4

TEMPERATURE = 0
COMPLETION_LEN = 2000
TOP_P = 1
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0

# Define paths to prompts
SYSTEM_PRINCIPLES_TEXT_FILE = 'prompts/principle_5.txt'
QUESTION_TEXT_FILE = 'prompts/question_5.txt'
ANSWER_KEY = 'prompts/iterative/answer_key.txt'
EVALUATION_PRINCIPLE = 'prompts/principle_5.txt'

with open('../claude_config.json','r') as f:
    claude_api_key = json.load(f)['api_key']

client = anthropic.Anthropic(
    api_key=claude_api_key,
)
    
# Completion functions
def request_claude_magic(system_prompt,messages_input):
    try:
        return client.messages.create(
                model=MODEL,
                max_tokens=COMPLETION_LEN,
                system=system_prompt,
                messages=messages_input,
                temperature=TEMPERATURE,
                top_p=TOP_P
            )
    except anthropic.RateLimitError:
        print('Rate limit exceeded. Waiting 20 seconds...')
        time.sleep(20)
        return request_claude_magic(system_prompt, messages_input)


def get_completion(response):
    return response.content[0].text


def evaluater(system_prompt, question):    
   
    #Prepare question to send in to gpt
    with open(QUESTION_TEXT_FILE,'r') as f:
        question_user_prompt = f.read()
    question_user_prompt = question_user_prompt.replace('{QUESTION}', json.dumps(question, sort_keys=False, indent=4))
    
    messages=[
                {'role': 'user', 'content': question_user_prompt}
            ]
     
    gpt_answer = get_completion(request_claude_magic(system_prompt,messages))
    #print(gpt_answer)
    messages.append({'role': 'assistant', 'content': gpt_answer})
    messages.insert(0,{'role': 'system', 'content': system_prompt})

    return messages, gpt_answer

# Make System Prompt
with open(SYSTEM_PRINCIPLES_TEXT_FILE,'r',encoding='UTF8') as f:
    SYSTEM_PROMPT = f.read()


in_directory = './mcqs/'
out_directory = './responses_claude/'

df = pd.read_csv('gold_50_5.csv')
df['questionID'] = df['questionID'].astype(str)
df['auto_criteria_5'] = '100'

for file_name in os.listdir(in_directory):
    file_path = os.path.join(in_directory, file_name)
    if os.path.isfile(file_path):
        if file_name in os.listdir(out_directory):
            with open(os.path.join(out_directory, file_name), 'r') as file:
                mcq_eval = json.load(file)
            print("present ",mcq_eval[-1]['content'])
            df.loc[df['questionID']==file_name.split('.')[0],'auto_criteria_5'] = mcq_eval[-1]['content']
        else:
            with open(file_path, 'r') as file:
                mcq = json.load(file)
            
            gpt_output, mcq_eval = evaluater(SYSTEM_PROMPT, mcq)

            df.loc[df['questionID']==file_name.split('.')[0],'auto_criteria_5'] = mcq_eval
            with open(file_path.replace(in_directory,out_directory),'w',encoding="utf-8") as outfile: 
                json.dump(gpt_output, outfile, indent=4)
            time.sleep(10)
        
        


print(df)
df.to_csv('./evaluation_claude.csv')