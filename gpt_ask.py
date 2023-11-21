import sys
import openai
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
openai.organization = "org-bOaL53AMHfnPzifP0AcjW2Fg"
openai.api_key = config['DEFAULT']['open_ai_api_key']
models = openai.Model.list()

def run_gpt(context, question, max_tokens):
    """
    Create a chat completion request using the OpenAI API.

    Args:
        context (str): A system message setting the context/instructions for the conversation.
        question (str): The user's input or question.
        max_tokens (int): The maximum number of tokens in the generated response.

    Returns:
        str: The generated response message content.
    """
    
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                
                messages=[{"role": "system", "content": context},
                            {"role": "user", "content": question}
                ],
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)

    return response.choices[0].message.content

#robot_spec = """axis" :0 = move forward, "axis": 2 = turn right, "speed: 3" = move forward 25cm/sec or turning 180 degrees in 945ms""" 

def run_gpt_robot(context, positions, question, max_token):
    """
    Create a chat completion request using the OpenAI API.

    Args:
        context (str): A system message setting the context/instructions for the conversation.
        positions (str): A system message setting the positions of objects for the conversation.
        question (str): The user's input or question.
        max_token (int): The maximum number of tokens in the generated response.

    Returns:
        str: The generated response message content.
    """
    
    #with open(context) as f:
    #    context_lines = "".join(map(str,f.readlines())) 
    #answerformat="""Answerformat for your answer: {“axis”: 2, “speed”: 3, “duration”: 500} axis" :0 = move forward, "axis": 2 = turn right, "speed: 3" = move forward 25cm/sec or turning 180degree in 945ms"""
    #user_content = question + answerformat
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "system", "content": context},
                            {"role": "system", "content" : positions}, #new
                            #{"role": "system", "content" : robot_spec},
                            #{"role": "system", "content" : answerformat},
                            {"role": "user", "content": question}   #"in json with param axis, speed, duration"}
                            
                ],
                temperature=0,
                max_tokens=max_token,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)

    return response.choices[0].message.content


    
if __name__ == "__main__":
    print("\nResponse: {}".format(run_gpt(sys.argv[1], sys.argv[2])))