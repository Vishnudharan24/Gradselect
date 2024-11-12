import ollama
import json

# def getname_conclusion(recivedMessage):
#     response = ollama.chat(model='llama3.1',messages = [
#         {
#             'role':'system',
#             'content':'give me a very short conclusion of the given message'
#         },
#         {
#             'role':'user',
#             'content':recivedMessage
#         }
#     ])
#     return response

stream_input = []

# Adding a system message to set context or instructions
response = ollama.chat(model='llama3.1', messages=[
    {
        'role': 'system',
        'content': 'Act like a HR from a service based organization , that primarily focused on web based services. do not hallucinate. don\'t be optimistic '
    },
    {
        'role': 'user',
        'content': ''' I'm Aravindh S, an enthusiastic and passionate technologist from Tamil Nadu, currently in my final year of a Bachelor's degree in Information Technology with a CGPA of 9. My journey in technology began at Kongu Matriculation Hr. Sec. School, where I secured 94% in both SSLC and HSC. Since then, I've been driven by a deep interest in new technologies and gadgets, which has shaped my career path.

As an extrovert with a diverse skill set, I thrive in environments where I can leverage my knowledge across multiple domains. My technical expertise spans Web Development, Virtual Reality, IoT, Machine Learning, App Development, and Cloud Computing. I am proficient in C, Java, Python, React, Node.js, PHP, MongoDB, MySQL, Unreal Engine, and basic AWS, which allows me to adapt and excel in various technological landscapes.

My experiences extend beyond the classroom, as I've taken on leadership roles that have honed my management and communication skills. As Placement Coordinator, Project Coordinator, and Class Representative, I've led teams to success, learning from both triumphs and challenges. My dedication has earned me accolades, including Best Student, Academic Excellence awards, and victories in Hackathons, Coding Events, Presentations, and College Cultural activities.

In addition to my technical and leadership skills, I have a strong commitment to mentoring and knowledge-sharing. As the IT Association Secretary, I organized events, including National-level Symposiums, and guided my peers and juniors in their academic and professional growth.

I am always eager to expand my knowledge further and contribute meaningfully to the next phase of my career. My passion for continuous learning and my ability to adapt to new challenges make me confident in my ability to make a positive impact.


is this candidate worth recruiting evaluate him with atleast 5 criterias and award marks for 50''' ,
    }
],

    stream=True
    
)

for smallChunk in response:
    smallWord = smallChunk['message']['content']
    print(smallWord, end = '' , flush=True)
    stream_input.append(smallWord)

print('\n') #Leave a empty line after the stream input 


generated_string = ''
for word in stream_input:
    print(word , end = '')
    generated_string+=word

print('\n') #Leave a empty line after the stream input 


#get the response of the generated message
# conclusion = getname_conclusion(generated_string)

# print("The conclusion of the generated result is : ",conclusion['message']['content'])



