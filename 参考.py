from openai import OpenAI

bozo_input=input("请输入问题：")

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key='0bd0ef7f-aab8-4212-aa35-7c49e80a75b6', # ModelScope Token
)

# set extra_body for thinking control
extra_body = {
    # enable thinking, set to False to disable
    "enable_thinking": True,
    # use thinking_budget to contorl num of tokens used for thinking
    # "thinking_budget": 4096
}

response = client.chat.completions.create(
    model='Qwen/Qwen3-235B-A22B',  # ModelScope Model-Id Qwen3-32B
    messages=[
        {
          'role': 'user',
          # 'content': '介绍一下绍兴？'
          'content': bozo_input
        }
    ],
    stream=True,
    extra_body=extra_body
)
done_thinking = False
for chunk in response:
    thinking_chunk = chunk.choices[0].delta.reasoning_content
    answer_chunk = chunk.choices[0].delta.content
    if thinking_chunk != '':
        print(thinking_chunk, end='', flush=True)
    elif answer_chunk != '':
        if not done_thinking:
            print('\n\n === Final Answer ===\n')
            done_thinking = True
        print(answer_chunk, end='', flush=True)
