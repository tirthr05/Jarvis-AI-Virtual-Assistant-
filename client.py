from openai import OpenAI


# pip install OpenAI
# If you saved he key under the diffrent environments variable name,  you can do something like: 

client = OpenAI (api_key= "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" ) 


completion = client.chat.completions.create(
  model="gpt-4.1",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)