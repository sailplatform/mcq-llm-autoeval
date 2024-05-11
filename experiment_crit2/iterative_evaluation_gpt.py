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
SYSTEM_PRINCIPLES_TEXT_FILE = 'prompts/iterative/system.txt'
QUESTION_TEXT_FILE = 'prompts/iterative/question.txt'
ANSWER_KEY = 'prompts/iterative/answer_key.txt'
EVALUATION_PRINCIPLE = 'prompts/iterative/principle_2_multistep_step1.txt'

with open('openai_config.json','r') as f:
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
        return request_gpt_magic(system_prompt, user_prompt)


def get_completion(response):
    return response['choices'][0]['message']['content']


def evaluater(system_prompt, question):    
    #Process the question to remove answer key
    for choice in question['choices']:
        if choice['correct']=='true':
            answer_marked_correct = choice['choice']
        del choice['correct']
    
    #Prepare question to send in to gpt
    with open(QUESTION_TEXT_FILE,'r') as f:
        question_user_prompt = f.read()
    question_user_prompt = question_user_prompt.replace('{QUESTION}', json.dumps(question, sort_keys=False, indent=4))

    #Prepare answer key to send in to gpt
    with open(ANSWER_KEY,'r') as f:
        answer_key_prompt = f.read()
    answer_key_prompt = answer_key_prompt.replace('{CHOICE}',answer_marked_correct)

    #Prepare the principle prompt to send in to gpt
    with open(EVALUATION_PRINCIPLE,'r') as f:
        principle = f.read()
    
    # messages=[
    #             {'role': 'system', 'content': system_prompt},
    #             {'role': 'user', 'content': question_user_prompt}
    #         ]
    
    messages=[
                {'role': 'system', 'content': system_prompt}
            ]
    
    ############ Few-shot prompting ############
    # with open('./prompts/iterative/fewShot_q1.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAns1.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/fewShot_ansKey1.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAnsCheck1.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/principle_2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisEval1.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})

    # with open('./prompts/iterative/fewShot_q2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAns2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/fewShot_ansKey2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAnsCheck2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/principle_2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisEval2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})

    # with open('./prompts/iterative/fewShot_q3.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAns3.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/fewShot_ansKey3.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAnsCheck3.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/principle_2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisEval3.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})

    # with open('./prompts/iterative/fewShot_q4.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAns4.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/fewShot_ansKey4.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisAnsCheck4.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    # with open('./prompts/iterative/principle_2.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'user', 'content': contents})
    # with open('prompts/iterative/fewShot_assisEval4.txt') as f:
    #     contents = f.read()
    # messages.append({'role': 'assistant', 'content': contents})
    
    #First ask GPT to answer the question
    messages.append({'role': 'user', 'content': question_user_prompt})
    gpt_answer = get_completion(request_gpt_magic(messages))
    #print(gpt_answer)
    messages.append({'role': 'assistant', 'content': gpt_answer})

    #Reveal answer key to GPT
    messages.append({'role': 'user', 'content': answer_key_prompt})    
    gpt_key_check = get_completion(request_gpt_magic(messages))
    #print(gpt_key_check)
    messages.append({'role': 'assistant', 'content': gpt_key_check})

    #Ask GPT to evaluate the question based on the principle
    messages.append({'role': 'user', 'content': principle})
    gpt_evaluation = get_completion(request_gpt_magic(messages))

    ######### Multi-step evaluation #########
    if gpt_evaluation=='1':
        messages.append({'role': 'assistant', 'content': gpt_evaluation})
        with open('prompts/iterative/principle_2_multistep_step2.txt','r') as f:
            principle = f.read()
        messages.append({'role': 'user', 'content': principle})
        gpt_evaluation = get_completion(request_gpt_magic(messages))
    elif gpt_evaluation=='2':
        gpt_evaluation = '3'
    elif gpt_evaluation=='3':
        gpt_evaluation='4'

    print(gpt_evaluation)
    messages.append({'role': 'assistant', 'content': gpt_evaluation})
    return messages, gpt_evaluation

# Make System Prompt
with open(SYSTEM_PRINCIPLES_TEXT_FILE,'r',encoding='UTF8') as f:
    SYSTEM_PROMPT = f.read()


in_directory = './experiment_50/mcqs/'
out_directory = './experiment_50/responses_multistep/'

df = pd.read_csv('gold_50.csv')
df['questionID'] = df['questionID'].astype(str)
df['auto_criteria_2'] = '100'

for file_name in os.listdir(in_directory):
    file_path = os.path.join(in_directory, file_name)
    if os.path.isfile(file_path) and file_name not in os.listdir(out_directory):
        
        with open(file_path, 'r') as file:
            mcq = json.load(file)
        
        gpt_output, mcq_eval = evaluater(SYSTEM_PROMPT,mcq)

        df.loc[df['questionID']==file_name.split('.')[0],'auto_criteria_2'] = mcq_eval
        with open(file_path.replace(in_directory,out_directory),'w',encoding="utf-8") as outfile: 
            json.dump(gpt_output, outfile, indent=4)
        #if i==5:
        #    break
        # json_data_str = mcq_eval[mcq_eval.find('{'):mcq_eval.rfind('}') + 1]
        # print(json_data_str)
        # mcq_evalj = json.loads(json_data_str)
        # with open(file_path.replace(in_directory,out_directory),'w',encoding="utf-8") as f:
        #    json.dump(mcq_evalj , f, indent=4)

        

print(df)
df.to_csv('./experiment_50/iterative_multistep.csv')