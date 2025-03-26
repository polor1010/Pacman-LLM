from google import genai
from pydantic import BaseModel

'''
file_path = 'prompt_old.txt'
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read() 

print(content)

data = {
    'gPos1': (9,7),
    'gPos2': (11,7),
    'pPos': (7,2)
}
'''

class Ghost(BaseModel):
  ghost_name: str
  setps: list[str]

def GhostController(data):

    file_path = 'prompt.txt'
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read() 
    
    client = genai.Client(api_key='')
    filled_content = content.format(**data)

    #print(filled_content)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash', 
        contents=filled_content,
        #generation_config=genai.GenerationConfig(
        #    max_output_tokens=2000,
        #    temperature=0.9,
        #),
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[Ghost],
        },
    )

    #print(response.text)
    ghosts: list[Ghost] = response.parsed

    #for g in ghosts :
    #  print(g.setps)
    #print('AI prediction : ', ghosts[0].setps[2], ghosts[1].setps[2])
    return ghosts[0].setps[2], ghosts[1].setps[2]
    

#print(response.model_dump_json(exclude_none=True, indent=4))

#print(GhostController(content))