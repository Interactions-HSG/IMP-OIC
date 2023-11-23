import sys
import openai
import configparser

from openai import OpenAI

config = configparser.ConfigParser()
config.read('config.ini')
client = OpenAI(api_key=config['DEFAULT']['open_ai_api_key'], organization="org-bOaL53AMHfnPzifP0AcjW2Fg")


def run_gpt(context, question):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": context},
                  {"role": "user", "content": question}
                  ],
        temperature=1,
        max_tokens=1532,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

    return response.choices[0].message.content


if __name__ == "__main__":
    print("\nResponse: {}".format(run_gpt(sys.argv[1], sys.argv[2])))
